"""Leakage-safe customer behavior features for historical monitoring.

This module works on invoice-level valid purchase orders. It describes changes
in a customer's observed purchase cadence and gross revenue rate at a fixed
cutoff; its indicators are not churn probabilities or intervention alerts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)

from src.temporal_framework import ADMIN_EXCLUDE

MODEL_VERSION = "behavior-monitor-v1"
POLICY_VERSION = "behavior-continuous-v1"
SECONDS_PER_DAY = 86_400.0
CUSTOMER_ID = "Customer ID"
INVOICE = "Invoice"
PURCHASE_DATE = "PurchaseDate"
GROSS_REVENUE = "GrossRevenue"
REQUIRED_EVENT_COLUMNS = (CUSTOMER_ID, INVOICE, PURCHASE_DATE, GROSS_REVENUE)
EWMA_LAMBDA_CANDIDATES = (0.2, 0.4, 0.6)


@dataclass(frozen=True)
class BehaviorConfig:
    """Validated windows and minimum history for descriptive behavior features."""

    recent_window_days: int = 30
    reference_window_days: int = 90
    min_gaps_for_mad: int = 4
    min_reference_exposure_days: int = 30
    min_observations_for_ewma: int = 4
    ewma_lambda: float = 0.4
    rate_prior_orders: float = 0.5
    rate_prior_days: float = 30.0

    def __post_init__(self) -> None:
        for name in (
            "recent_window_days",
            "reference_window_days",
            "min_gaps_for_mad",
            "min_reference_exposure_days",
            "min_observations_for_ewma",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")
        if self.reference_window_days <= 0:
            raise ValueError("reference_window_days must be positive.")
        if not np.isfinite(self.ewma_lambda) or not 0 < self.ewma_lambda <= 1:
            raise ValueError("ewma_lambda must be finite and in (0, 1].")
        if (
            not np.isfinite(self.rate_prior_orders)
            or self.rate_prior_orders < 0
            or not np.isfinite(self.rate_prior_days)
            or self.rate_prior_days <= 0
        ):
            raise ValueError("Rate priors must be finite and non-negative/positive.")


DEFAULT_CONFIG = BehaviorConfig()
BEHAVIOR_FEATURE_COLUMNS = (
    "gap_deviation_score",
    "purchase_rate_ratio",
    "purchase_rate_change_per_day",
    "revenue_rate_ratio",
    "revenue_rate_change_per_day",
    "ewma_gap_change_days",
)


def _validate_cutoff(cutoff_date: Any) -> pd.Timestamp:
    cutoff = pd.Timestamp(cutoff_date)
    if pd.isna(cutoff) or cutoff.tz is not None:
        raise ValueError("cutoff_date must be a valid timezone-naive timestamp.")
    return cutoff


def prepare_purchase_events(orders: pd.DataFrame) -> pd.DataFrame:
    """Validate and sort invoice-level purchases once for downstream features.

    Cancellation invoices and the two administrative accounts excluded by the
    temporal framework are removed. Other invalid values are rejected rather
    than silently repaired. Customer identifiers are retained without casting.
    """
    if not isinstance(orders, pd.DataFrame):
        raise TypeError("orders must be a pandas DataFrame.")
    missing = [column for column in REQUIRED_EVENT_COLUMNS if column not in orders]
    if missing:
        raise ValueError(f"orders is missing required columns: {missing}")
    events = orders.loc[:, REQUIRED_EVENT_COLUMNS].copy()
    if events[[CUSTOMER_ID, INVOICE, PURCHASE_DATE]].isna().any().any():
        raise ValueError("Customer ID, Invoice, and PurchaseDate cannot be missing.")

    events[PURCHASE_DATE] = pd.to_datetime(events[PURCHASE_DATE], errors="raise")
    if events[PURCHASE_DATE].dt.tz is not None:
        raise ValueError("PurchaseDate values must be timezone-naive.")
    events[GROSS_REVENUE] = pd.to_numeric(events[GROSS_REVENUE], errors="raise")
    revenue = events[GROSS_REVENUE].to_numpy(dtype=float)
    if not np.isfinite(revenue).all() or (revenue < 0).any():
        raise ValueError("GrossRevenue must contain finite, non-negative values.")

    cancellation = events[INVOICE].astype(str).str.upper().str.startswith("C")
    numeric_customer_ids = pd.to_numeric(events[CUSTOMER_ID], errors="coerce")
    administrative = numeric_customer_ids.isin(ADMIN_EXCLUDE)
    events = events.loc[~cancellation & ~administrative].copy()
    if events.empty:
        raise ValueError("No valid purchase orders remain after exclusions.")
    if events.duplicated([CUSTOMER_ID, INVOICE]).any():
        raise ValueError("Each Customer ID and Invoice pair must be unique.")

    events["_customer_sort"] = events[CUSTOMER_ID].astype(str)
    events["_invoice_sort"] = events[INVOICE].astype(str)
    events = (
        events.sort_values(
            ["_customer_sort", PURCHASE_DATE, "_invoice_sort"],
            kind="mergesort",
        )
        .drop(columns=["_customer_sort", "_invoice_sort"])
        .reset_index(drop=True)
    )
    events.attrs["behavior_monitor_prepared"] = True
    return events


def _prepared_events(purchase_events: pd.DataFrame) -> pd.DataFrame:
    """Accept the sorted module format, preparing ordinary order tables as needed."""
    if not isinstance(purchase_events, pd.DataFrame):
        raise TypeError("purchase_events must be a pandas DataFrame.")
    if purchase_events.attrs.get("behavior_monitor_prepared") is True:
        missing = [column for column in REQUIRED_EVENT_COLUMNS if column not in purchase_events]
        if missing:
            raise ValueError(f"purchase_events is missing required columns: {missing}")
        return purchase_events
    return prepare_purchase_events(purchase_events)


def compute_completed_gaps(
    purchase_events: pd.DataFrame,
    cutoff_date: Any | None = None,
) -> pd.DataFrame:
    """Return each completed consecutive invoice gap observed strictly pre-cutoff."""
    events = _prepared_events(purchase_events)
    data = events
    if cutoff_date is not None:
        cutoff = _validate_cutoff(cutoff_date)
        data = events.loc[events[PURCHASE_DATE].lt(cutoff)]
    gaps = data.loc[:, [CUSTOMER_ID, PURCHASE_DATE]].copy()
    gaps["previous_purchase_date"] = gaps.groupby(
        CUSTOMER_ID, sort=False
    )[PURCHASE_DATE].shift()
    gaps["completed_gap_days"] = (
        gaps[PURCHASE_DATE] - gaps["previous_purchase_date"]
    ).dt.total_seconds() / SECONDS_PER_DAY
    gaps = gaps.dropna(subset=["completed_gap_days"]).rename(
        columns={PURCHASE_DATE: "gap_end_date"}
    )
    if not gaps.empty:
        values = gaps["completed_gap_days"].to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError("Completed purchase gaps must be finite and non-negative.")
    return gaps.reset_index(drop=True)


def _latest_grouped_ewma(
    gaps: pd.DataFrame,
    *,
    alpha: float,
) -> tuple[pd.Series, pd.Series]:
    """Compute each customer's latest EWM and observation count using groupby EWM."""
    if gaps.empty:
        return pd.Series(dtype=float), pd.Series(dtype="int64")
    weighted = gaps.groupby(CUSTOMER_ID, sort=False)["completed_gap_days"].ewm(
        alpha=alpha,
        adjust=False,
    ).mean()
    weighted.index = weighted.index.get_level_values(-1)
    enriched = gaps.assign(_ewma=weighted)
    latest = enriched.groupby(CUSTOMER_ID, sort=False)["_ewma"].last()
    count = enriched.groupby(CUSTOMER_ID, sort=False)["completed_gap_days"].size()
    return latest, count


def _ewma_from_gaps(
    gaps: pd.DataFrame,
    cutoff: pd.Timestamp,
    config: BehaviorConfig,
) -> pd.DataFrame:
    columns = [
        CUSTOMER_ID,
        "reference_ewma_gap_days",
        "recent_ewma_gap_days",
        "reference_ewma_gap_count",
        "recent_ewma_gap_count",
        "ewma_gap_change_days",
        "ewma_lambda",
    ]
    if gaps.empty:
        return pd.DataFrame(columns=columns)

    recent_start = cutoff - pd.Timedelta(days=config.recent_window_days)
    reference = gaps.loc[gaps["gap_end_date"].lt(recent_start)]
    recent = gaps.loc[gaps["gap_end_date"].ge(recent_start)]
    reference_ewma, reference_count = _latest_grouped_ewma(
        reference, alpha=config.ewma_lambda
    )
    recent_ewma, recent_count = _latest_grouped_ewma(
        recent, alpha=config.ewma_lambda
    )
    customer_ids = gaps[CUSTOMER_ID].drop_duplicates()
    result = pd.DataFrame({CUSTOMER_ID: customer_ids})
    result["reference_ewma_gap_days"] = result[CUSTOMER_ID].map(reference_ewma)
    result["recent_ewma_gap_days"] = result[CUSTOMER_ID].map(recent_ewma)
    result["reference_ewma_gap_count"] = (
        result[CUSTOMER_ID].map(reference_count).fillna(0).astype(int)
    )
    result["recent_ewma_gap_count"] = (
        result[CUSTOMER_ID].map(recent_count).fillna(0).astype(int)
    )
    enough_history = (
        result["reference_ewma_gap_count"].ge(config.min_observations_for_ewma)
        & result["recent_ewma_gap_count"].ge(config.min_observations_for_ewma)
    )
    result["ewma_gap_change_days"] = (
        result["recent_ewma_gap_days"] - result["reference_ewma_gap_days"]
    ).where(enough_history)
    result["reference_ewma_gap_days"] = result[
        "reference_ewma_gap_days"
    ].where(enough_history)
    result["recent_ewma_gap_days"] = result["recent_ewma_gap_days"].where(
        enough_history
    )
    result["ewma_lambda"] = float(config.ewma_lambda)
    return result.loc[:, columns]


def compute_ewma_features(
    purchase_events: pd.DataFrame,
    cutoff_date: Any,
    config: BehaviorConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Compare recent and historical EWM purchase gaps using completed events only."""
    cutoff = _validate_cutoff(cutoff_date)
    events = _prepared_events(purchase_events)
    gaps = compute_completed_gaps(events, cutoff)
    return _ewma_from_gaps(gaps, cutoff, config)


def compute_behavior_features(
    purchase_events: pd.DataFrame,
    cutoff_date: Any,
    config: BehaviorConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Build one leakage-safe row per customer with a pre-cutoff valid purchase."""
    cutoff = _validate_cutoff(cutoff_date)
    events = _prepared_events(purchase_events)
    historical = events.loc[events[PURCHASE_DATE].lt(cutoff)]
    if historical.empty:
        raise ValueError("No valid purchase orders occur before cutoff_date.")

    summary = (
        historical.groupby(CUSTOMER_ID, sort=False)
        .agg(
            first_purchase_date=(PURCHASE_DATE, "min"),
            last_purchase_date=(PURCHASE_DATE, "max"),
            historical_order_count=(INVOICE, "nunique"),
            historical_gross_revenue=(GROSS_REVENUE, "sum"),
        )
        .reset_index()
    )
    recent_start = cutoff - pd.Timedelta(days=config.recent_window_days)
    reference_start = recent_start - pd.Timedelta(days=config.reference_window_days)
    recent = historical.loc[historical[PURCHASE_DATE].ge(recent_start)]
    reference = historical.loc[
        historical[PURCHASE_DATE].ge(reference_start)
        & historical[PURCHASE_DATE].lt(recent_start)
    ]
    recent_summary = (
        recent.groupby(CUSTOMER_ID, sort=False)
        .agg(
            recent_order_count=(INVOICE, "nunique"),
            recent_gross_revenue=(GROSS_REVENUE, "sum"),
        )
        .reset_index()
    )
    reference_summary = (
        reference.groupby(CUSTOMER_ID, sort=False)
        .agg(
            reference_order_count=(INVOICE, "nunique"),
            reference_gross_revenue=(GROSS_REVENUE, "sum"),
        )
        .reset_index()
    )
    summary = summary.merge(recent_summary, on=CUSTOMER_ID, how="left", validate="one_to_one")
    summary = summary.merge(
        reference_summary, on=CUSTOMER_ID, how="left", validate="one_to_one"
    )
    for column in (
        "recent_order_count",
        "recent_gross_revenue",
        "reference_order_count",
        "reference_gross_revenue",
    ):
        summary[column] = summary[column].fillna(0)
    summary["recent_order_count"] = summary["recent_order_count"].astype(int)
    summary["reference_order_count"] = summary["reference_order_count"].astype(int)

    first = pd.to_datetime(summary["first_purchase_date"])
    recent_observed_start = first.where(first.ge(recent_start), recent_start)
    reference_observed_start = first.where(first.ge(reference_start), reference_start)
    summary["recent_observed_days"] = (
        (cutoff - recent_observed_start).dt.total_seconds() / SECONDS_PER_DAY
    ).clip(lower=0, upper=config.recent_window_days)
    summary["reference_observed_days"] = (
        (recent_start - reference_observed_start).dt.total_seconds()
        / SECONDS_PER_DAY
    ).clip(lower=0, upper=config.reference_window_days)
    summary["current_elapsed_gap_days"] = (
        (cutoff - pd.to_datetime(summary["last_purchase_date"])).dt.total_seconds()
        / SECONDS_PER_DAY
    )

    recent_rate = (
        summary["recent_order_count"] + config.rate_prior_orders
    ) / (summary["recent_observed_days"] + config.rate_prior_days)
    reference_rate = (
        summary["reference_order_count"] + config.rate_prior_orders
    ) / (summary["reference_observed_days"] + config.rate_prior_days)
    reference_sufficient = summary["reference_observed_days"].ge(
        config.min_reference_exposure_days
    )
    summary["recent_order_rate_per_day"] = recent_rate
    summary["reference_order_rate_per_day"] = reference_rate.where(reference_sufficient)
    summary["purchase_rate_ratio"] = (recent_rate / reference_rate).where(
        reference_sufficient
    )
    summary["purchase_rate_change_per_day"] = (recent_rate - reference_rate).where(
        reference_sufficient
    )
    raw_recent_rate = summary["recent_order_count"] / summary[
        "recent_observed_days"
    ].replace(0, np.nan)
    raw_reference_rate = summary["reference_order_count"] / summary[
        "reference_observed_days"
    ].replace(0, np.nan)
    summary["raw_purchase_rate_ratio"] = (raw_recent_rate / raw_reference_rate).where(
        reference_sufficient & raw_reference_rate.gt(0)
    )

    summary["recent_revenue_rate_per_day"] = (
        summary["recent_gross_revenue"]
        / summary["recent_observed_days"].replace(0, np.nan)
    )
    summary["reference_revenue_rate_per_day"] = (
        summary["reference_gross_revenue"]
        / summary["reference_observed_days"].replace(0, np.nan)
    ).where(reference_sufficient)
    positive_reference_revenue = (
        reference_sufficient & summary["reference_revenue_rate_per_day"].gt(0)
    )
    summary["revenue_rate_ratio"] = (
        summary["recent_revenue_rate_per_day"]
        / summary["reference_revenue_rate_per_day"]
    ).where(positive_reference_revenue)
    summary["revenue_rate_change_per_day"] = (
        summary["recent_revenue_rate_per_day"]
        - summary["reference_revenue_rate_per_day"]
    ).where(reference_sufficient)
    summary["recent_order_rate"] = summary["recent_order_rate_per_day"]
    summary["reference_order_rate"] = summary["reference_order_rate_per_day"]
    summary["purchase_rate_change"] = summary["purchase_rate_change_per_day"]
    summary["recent_revenue_rate"] = summary["recent_revenue_rate_per_day"]
    summary["reference_revenue_rate"] = summary["reference_revenue_rate_per_day"]

    gaps = compute_completed_gaps(events, cutoff)
    if gaps.empty:
        gap_summary = pd.DataFrame(
            columns=[
                CUSTOMER_ID,
                "completed_gap_count",
                "median_completed_gap_days",
                "mean_completed_gap_days",
                "mad_completed_gap_days",
            ]
        )
    else:
        gaps["gap_median"] = gaps.groupby(CUSTOMER_ID, sort=False)[
            "completed_gap_days"
        ].transform("median")
        gaps["absolute_deviation"] = (
            gaps["completed_gap_days"] - gaps["gap_median"]
        ).abs()
        gap_summary = (
            gaps.groupby(CUSTOMER_ID, sort=False)
            .agg(
                completed_gap_count=("completed_gap_days", "size"),
                median_completed_gap_days=("completed_gap_days", "median"),
                mean_completed_gap_days=("completed_gap_days", "mean"),
                mad_completed_gap_days=("absolute_deviation", "median"),
            )
            .reset_index()
        )
    summary = summary.merge(gap_summary, on=CUSTOMER_ID, how="left", validate="one_to_one")
    summary["completed_gap_count"] = (
        summary["completed_gap_count"].fillna(0).astype(int)
    )
    ewma = _ewma_from_gaps(gaps, cutoff, config)
    summary = summary.merge(ewma, on=CUSTOMER_ID, how="left", validate="one_to_one")
    summary["ewma_lambda"] = float(config.ewma_lambda)
    summary["ewma_gap_observation_count"] = (
        summary["reference_ewma_gap_count"].fillna(0).astype(int)
        + summary["recent_ewma_gap_count"].fillna(0).astype(int)
    )
    enough_gaps = summary["completed_gap_count"].ge(config.min_gaps_for_mad)
    robust_scale = (1.4826 * summary["mad_completed_gap_days"]).clip(lower=1.0)
    summary["gap_deviation_score"] = (
        (summary["current_elapsed_gap_days"] - summary["median_completed_gap_days"])
        / robust_scale
    ).where(enough_gaps)
    summary["gap_deviation_method"] = np.where(
        enough_gaps, "median_mad", "unavailable_insufficient_gaps"
    )

    enough_reference = summary["reference_observed_days"].ge(
        config.min_reference_exposure_days
    )
    sufficient_history = enough_gaps & enough_reference
    limited_history = summary["completed_gap_count"].ge(2) | enough_reference
    summary["history_sufficiency"] = np.select(
        [sufficient_history, limited_history],
        ["sufficient", "limited"],
        default="insufficient",
    )
    summary["cutoff_date"] = cutoff
    summary["feature_version"] = MODEL_VERSION
    summary["policy_version"] = POLICY_VERSION
    return summary.sort_values(CUSTOMER_ID, key=lambda values: values.astype(str)).reset_index(
        drop=True
    )


def calculate_behavior_scores(
    behavior_features: pd.DataFrame,
    parameters: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Return continuous component indicators without an unvalidated alert label."""
    parameters = parameters or {}
    unknown_parameters = set(parameters).difference(
        {"feature_version", "policy_version", "ewma_lambda"}
    )
    if unknown_parameters:
        raise ValueError(f"Unsupported behavior-score parameters: {sorted(unknown_parameters)}")
    if parameters.get("feature_version", MODEL_VERSION) != MODEL_VERSION:
        raise ValueError("Unsupported behavior feature version.")
    if parameters.get("policy_version", POLICY_VERSION) != POLICY_VERSION:
        raise ValueError("Unsupported behavior policy version.")
    ewma_lambda = float(parameters.get("ewma_lambda", DEFAULT_CONFIG.ewma_lambda))
    if not np.isfinite(ewma_lambda) or not 0 < ewma_lambda <= 1:
        raise ValueError("ewma_lambda must be finite and in (0, 1].")
    required = [CUSTOMER_ID, "cutoff_date", *BEHAVIOR_FEATURE_COLUMNS]
    missing = [column for column in required if column not in behavior_features]
    if missing:
        raise ValueError(f"behavior_features is missing required columns: {missing}")
    result = behavior_features.loc[:, [CUSTOMER_ID, "cutoff_date"]].copy()
    result["gap_deviation_score"] = pd.to_numeric(
        behavior_features["gap_deviation_score"], errors="coerce"
    )
    result["purchase_rate_decline_fraction"] = 1 - pd.to_numeric(
        behavior_features["purchase_rate_ratio"], errors="coerce"
    )
    result["revenue_rate_decline_fraction"] = 1 - pd.to_numeric(
        behavior_features["revenue_rate_ratio"], errors="coerce"
    )
    result["ewma_gap_increase_days"] = pd.to_numeric(
        behavior_features["ewma_gap_change_days"], errors="coerce"
    )
    result["available_indicator_count"] = result[
        [
            "gap_deviation_score",
            "purchase_rate_decline_fraction",
            "revenue_rate_decline_fraction",
            "ewma_gap_increase_days",
        ]
    ].notna().sum(axis=1)
    if "history_sufficiency" in behavior_features:
        result["history_sufficiency"] = behavior_features[
            "history_sufficiency"
        ].astype(str)
    else:
        result["history_sufficiency"] = "unavailable"
    result["policy_status"] = "continuous_indicators_only"
    result["policy_version"] = POLICY_VERSION
    result["ewma_lambda"] = ewma_lambda
    return result


def build_behavior_trajectory(
    purchase_events: pd.DataFrame,
    customer_id: Any,
    cutoff_date: Any,
    *,
    window_days: int = 30,
    max_history_days: int = 365,
) -> pd.DataFrame:
    """Build compact, cutoff-safe fixed-window order and revenue history."""
    cutoff = _validate_cutoff(cutoff_date)
    for name, value in (("window_days", window_days), ("max_history_days", max_history_days)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer.")
    events = _prepared_events(purchase_events)
    customer = events.loc[
        events[CUSTOMER_ID].eq(customer_id) & events[PURCHASE_DATE].lt(cutoff)
    ]
    if customer.empty:
        raise KeyError(customer_id)
    first_purchase = pd.Timestamp(customer[PURCHASE_DATE].min())
    history_start = max(first_purchase, cutoff - pd.Timedelta(days=max_history_days))
    elapsed_days = (cutoff - history_start).total_seconds() / SECONDS_PER_DAY
    period_count = max(1, ceil(elapsed_days / window_days))
    width = pd.Timedelta(days=window_days)
    first_period_start = cutoff - period_count * width
    rows: list[dict[str, Any]] = []
    for index in range(period_count):
        period_start = first_period_start + index * width
        period_end = period_start + width
        observed_start = max(period_start, first_purchase)
        exposure = max(
            0.0,
            min(
                window_days,
                (min(period_end, cutoff) - observed_start).total_seconds()
                / SECONDS_PER_DAY,
            ),
        )
        if exposure <= 0:
            continue
        period_orders = customer.loc[
            customer[PURCHASE_DATE].ge(period_start)
            & customer[PURCHASE_DATE].lt(period_end)
        ]
        rows.append(
            {
                CUSTOMER_ID: customer_id,
                "period_start": period_start,
                "period_end": min(period_end, cutoff),
                "observed_exposure_days": exposure,
                "order_count": int(period_orders[INVOICE].nunique()),
                "gross_revenue": float(period_orders[GROSS_REVENUE].sum()),
                "order_rate_per_day": int(period_orders[INVOICE].nunique()) / exposure,
                "revenue_rate_per_day": float(period_orders[GROSS_REVENUE].sum())
                / exposure,
            }
        )
    return pd.DataFrame(rows)


def behavior_config_metadata(config: BehaviorConfig = DEFAULT_CONFIG) -> dict[str, Any]:
    """Return JSON-safe configuration and version metadata."""
    return {
        "feature_version": MODEL_VERSION,
        "policy_version": POLICY_VERSION,
        "config": asdict(config),
        "recent_window": "[cutoff - recent_window_days, cutoff)",
        "reference_window": (
            "[cutoff - recent_window_days - reference_window_days, "
            "cutoff - recent_window_days)"
        ),
        "cutoff_rule": "Only purchases with PurchaseDate < cutoff are used.",
        "policy_status": "continuous_indicators_only",
        "alert_threshold": None,
    }


def evaluate_binary_risk(
    outcomes: pd.Series | np.ndarray,
    risk_scores: pd.Series | np.ndarray,
    *,
    top_fraction: float = 0.10,
) -> dict[str, float | int]:
    """Evaluate nonpurchase ranking and a fixed-budget top-fraction comparison."""
    y = np.asarray(outcomes, dtype=int)
    scores = np.asarray(risk_scores, dtype=float)
    if y.ndim != 1 or scores.ndim != 1 or len(y) != len(scores) or not len(y):
        raise ValueError("outcomes and risk_scores must be non-empty aligned vectors.")
    if not np.isin(y, (0, 1)).all():
        raise ValueError("outcomes must contain only binary 0/1 values.")
    if not np.isfinite(scores).all():
        raise ValueError("risk_scores must contain only finite values.")
    if not 0 < top_fraction <= 1:
        raise ValueError("top_fraction must be in (0, 1].")
    if np.unique(y).size != 2:
        raise ValueError("Both outcome classes are required for ranking metrics.")
    top_n = max(1, int(ceil(len(y) * top_fraction)))
    selected = np.argpartition(scores, len(scores) - top_n)[-top_n:]
    true_positives = int(y[selected].sum())
    positives = int(y.sum())
    negatives = len(y) - positives
    false_positives = top_n - true_positives
    return {
        "n_customers": int(len(y)),
        "nonpurchase_rate": float(y.mean()),
        "roc_auc": float(roc_auc_score(y, scores)),
        "average_precision": float(average_precision_score(y, scores)),
        "precision_at_budget": float(true_positives / top_n),
        "recall_at_budget": float(true_positives / positives) if positives else 0.0,
        "false_alert_rate_at_budget": (
            float(false_positives / negatives) if negatives else 0.0
        ),
        "alert_coverage_at_budget": float(top_n / len(y)),
        "budget_fraction": float(top_fraction),
        "budget_customer_count": int(top_n),
    }


def probability_metrics(
    outcomes: pd.Series | np.ndarray,
    predicted_probabilities: pd.Series | np.ndarray,
) -> dict[str, float]:
    """Return probability calibration metrics for a finite 0-to-1 prediction."""
    y = np.asarray(outcomes, dtype=int)
    probabilities = np.asarray(predicted_probabilities, dtype=float)
    if y.ndim != 1 or probabilities.ndim != 1 or len(y) != len(probabilities) or not len(y):
        raise ValueError("outcomes and probabilities must be non-empty aligned vectors.")
    if not np.isin(y, (0, 1)).all():
        raise ValueError("outcomes must contain only binary 0/1 values.")
    if not np.isfinite(probabilities).all() or ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError("predicted_probabilities must be finite and in [0, 1].")
    return {
        "brier_score": float(brier_score_loss(y, probabilities)),
        "log_loss": float(log_loss(y, np.clip(probabilities, 1e-12, 1 - 1e-12))),
        "mean_predicted_nonpurchase_probability": float(probabilities.mean()),
        "actual_nonpurchase_rate": float(y.mean()),
    }


def evaluate_frozen_alert_threshold(
    outcomes: pd.Series | np.ndarray,
    risk_scores: pd.Series | np.ndarray,
    threshold: float,
) -> dict[str, float | int]:
    """Evaluate a threshold frozen before TEST; no test-set threshold is inferred."""
    y = np.asarray(outcomes, dtype=int)
    scores = np.asarray(risk_scores, dtype=float)
    if y.ndim != 1 or scores.ndim != 1 or len(y) != len(scores) or not len(y):
        raise ValueError("outcomes and risk_scores must be non-empty aligned vectors.")
    if not np.isin(y, (0, 1)).all() or not np.isfinite(scores).all():
        raise ValueError("outcomes must be binary and risk_scores must be finite.")
    if not np.isfinite(threshold):
        raise ValueError("threshold must be finite.")
    predicted = scores >= float(threshold)
    positives = y == 1
    negatives = ~positives
    true_positives = int((predicted & positives).sum())
    false_positives = int((predicted & negatives).sum())
    return {
        "threshold": float(threshold),
        "alert_count": int(predicted.sum()),
        "alert_coverage": float(predicted.mean()),
        "precision": (
            float(true_positives / predicted.sum()) if predicted.any() else 0.0
        ),
        "recall": (
            float(true_positives / positives.sum()) if positives.any() else 0.0
        ),
        "false_alert_rate": (
            float(false_positives / negatives.sum()) if negatives.any() else 0.0
        ),
    }


def select_alert_threshold(
    validation_scores: pd.Series | np.ndarray,
    *,
    alert_budget: float = 0.10,
) -> float:
    """Choose a numeric validation-only score threshold for a fixed alert budget."""
    scores = np.asarray(validation_scores, dtype=float)
    if scores.ndim != 1 or not len(scores) or not np.isfinite(scores).all():
        raise ValueError("validation_scores must be a non-empty finite vector.")
    if not 0 < alert_budget <= 1:
        raise ValueError("alert_budget must be in (0, 1].")
    alert_count = max(1, int(ceil(len(scores) * alert_budget)))
    return float(np.partition(scores, len(scores) - alert_count)[len(scores) - alert_count])


def paired_customer_bootstrap_difference(
    outcomes: pd.Series | np.ndarray,
    first_scores: pd.Series | np.ndarray,
    second_scores: pd.Series | np.ndarray,
    customer_ids: pd.Series | np.ndarray,
    *,
    metric: str = "average_precision",
    n_resamples: int = 1000,
    random_state: int = 42,
) -> dict[str, float | int | str]:
    """Paired cluster-bootstrap metric difference by customer.

    Positive differences mean ``first_scores`` scores higher for ROC-AUC/AP;
    for Brier score, a negative difference is an improvement. If customers
    contribute multiple rows, each sampled customer brings all of their rows.
    """
    y = np.asarray(outcomes, dtype=int)
    first = np.asarray(first_scores, dtype=float)
    second = np.asarray(second_scores, dtype=float)
    ids = np.asarray(customer_ids)
    if not (y.ndim == first.ndim == second.ndim == ids.ndim == 1):
        raise ValueError("Bootstrap inputs must be one-dimensional.")
    if not len(y) or not (len(y) == len(first) == len(second) == len(ids)):
        raise ValueError("Bootstrap inputs must be non-empty and aligned.")
    if not np.isin(y, (0, 1)).all() or not np.isfinite(first).all() or not np.isfinite(second).all():
        raise ValueError("Bootstrap outcomes must be binary and scores must be finite.")
    if metric not in {"roc_auc", "average_precision", "brier"}:
        raise ValueError("metric must be roc_auc, average_precision, or brier.")
    if isinstance(n_resamples, bool) or not isinstance(n_resamples, int) or n_resamples < 100:
        raise ValueError("n_resamples must be an integer of at least 100.")

    customer_codes, unique_customers = pd.factorize(ids, sort=False)
    if (customer_codes < 0).any():
        raise ValueError("customer_ids cannot contain missing values.")
    customer_count = len(unique_customers)
    rng = np.random.default_rng(random_state)
    differences = np.full(n_resamples, np.nan, dtype=float)
    metric_function = {
        "roc_auc": roc_auc_score,
        "average_precision": average_precision_score,
        "brier": brier_score_loss,
    }[metric]
    for index in range(n_resamples):
        sampled = rng.integers(0, customer_count, size=customer_count)
        sampled_customer_weights = np.bincount(sampled, minlength=customer_count)
        row_weights = sampled_customer_weights[customer_codes].astype(float)
        if row_weights.sum() == 0:
            continue
        try:
            if metric == "brier":
                first_value = metric_function(y, first, sample_weight=row_weights)
                second_value = metric_function(y, second, sample_weight=row_weights)
            else:
                first_value = metric_function(
                    y, first, sample_weight=row_weights
                )
                second_value = metric_function(
                    y, second, sample_weight=row_weights
                )
        except ValueError:
            continue
        differences[index] = float(first_value - second_value)

    valid = differences[np.isfinite(differences)]
    if len(valid) < n_resamples * 0.8:
        raise ValueError(
            "Too many bootstrap samples lacked both outcome classes; "
            "the cohort is too small for a stable interval."
        )
    return {
        "metric": metric,
        "difference_first_minus_second": float(
            metric_function(
                y,
                first,
                sample_weight=np.ones(len(y)),
            )
            - metric_function(
                y,
                second,
                sample_weight=np.ones(len(y)),
            )
        ),
        "confidence_interval_95_lower": float(np.quantile(valid, 0.025)),
        "confidence_interval_95_upper": float(np.quantile(valid, 0.975)),
        "valid_resamples": int(len(valid)),
        "requested_resamples": int(n_resamples),
        "customer_clusters": int(customer_count),
        "resampling_unit": "Customer ID; paired across both score series",
    }
