"""Financially explicit revenue exposure and forecast comparison utilities.

The saved historical forecast snapshot has no defensible counterfactual revenue
reference. Accordingly, exposure remains nullable unless a caller supplies a
documented, customer-matched business baseline. Forecast disagreement and the
nonreturn-weighted conditional-spending proxy are reported separately.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from src import purchase_clock as pc

SUPPORTED_HORIZONS = (30, 60, 90)
CUSTOMER_ID = "Customer ID"
CUTOFF_DATE = "cutoff_date"
EXPOSURE_NOT_ESTIMABLE = "not_estimable"
OPPORTUNITY_PROXY_METHOD = "(1 - purchase probability) * conditional expected spending"


@dataclass(frozen=True)
class RevenueExposureConfig:
    """Definitions required before a reference-based shortfall is estimable."""

    currency_code: str = "GBP"
    reference_definition: str | None = None
    reference_method: str | None = None

    def __post_init__(self) -> None:
        if self.currency_code != "GBP":
            raise ValueError("The saved Online Retail forecast amounts are denominated in GBP.")
        if self.reference_definition is not None and not self.reference_definition.strip():
            raise ValueError("reference_definition cannot be blank.")
        if self.reference_method is not None and not self.reference_method.strip():
            raise ValueError("reference_method cannot be blank.")


def _validate_horizon(horizon_days: int) -> int:
    if isinstance(horizon_days, bool) or horizon_days not in SUPPORTED_HORIZONS:
        raise ValueError(f"horizon_days must be one of {SUPPORTED_HORIZONS}.")
    return int(horizon_days)


def _require_columns(frame: pd.DataFrame, columns: Iterable[str], *, name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def _finite_nonnegative(frame: pd.DataFrame, columns: list[str], *, name: str) -> None:
    values = frame[columns].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{name} must contain only finite numeric values.")
    if (values < 0).any():
        raise ValueError(f"{name} must contain non-negative values.")


def prepare_revenue_forecast_table(
    forecast_snapshot: pd.DataFrame,
    horizon_days: int,
) -> pd.DataFrame:
    """Return validated, aligned historical customer forecasts for one horizon.

    Only forecast-time inputs and saved predictions are returned. Future target
    fields, when present in a caller's frame, are rejected rather than ignored.
    Monetary values remain in GBP.
    """
    horizon = _validate_horizon(horizon_days)
    if not isinstance(forecast_snapshot, pd.DataFrame):
        raise TypeError("forecast_snapshot must be a pandas DataFrame.")

    target_columns = set(pc.TARGET_COLUMNS).intersection(forecast_snapshot.columns)
    if target_columns:
        raise ValueError(
            "Forecast preparation cannot consume future outcome columns: "
            f"{sorted(target_columns)}"
        )

    probability = f"purchase_probability_{horizon}d"
    conditional = f"personalized_conditional_revenue_{horizon}d"
    expected = f"personalized_expected_revenue_{horizon}d"
    historical = f"historical_rate_expected_revenue_{horizon}d"
    segment = f"segment_expected_revenue_{horizon}d"
    required = [
        CUSTOMER_ID,
        CUTOFF_DATE,
        "Hist_Segment",
        "history_group",
        "Recency",
        "Frequency",
        "Monetary_Gross",
        probability,
        conditional,
        expected,
        historical,
        segment,
    ]
    _require_columns(forecast_snapshot, required, name="forecast_snapshot")
    source = forecast_snapshot.loc[:, required].copy()
    source[CUTOFF_DATE] = pd.to_datetime(source[CUTOFF_DATE], errors="raise")
    if source[CUTOFF_DATE].isna().any() or source[CUSTOMER_ID].isna().any():
        raise ValueError("Customer ID and cutoff_date cannot be missing.")
    if source.duplicated([CUSTOMER_ID, CUTOFF_DATE]).any():
        raise ValueError("Each customer and cutoff pair must be unique.")
    numeric_columns = [
        "Recency",
        "Frequency",
        "Monetary_Gross",
        probability,
        conditional,
        expected,
        historical,
        segment,
    ]
    source[numeric_columns] = source[numeric_columns].apply(
        pd.to_numeric, errors="raise"
    )
    _finite_nonnegative(
        source,
        [
            "Recency",
            "Frequency",
            "Monetary_Gross",
            conditional,
            expected,
            historical,
            segment,
        ],
        name="Forecast features and revenue",
    )
    probabilities = source[probability].to_numpy(dtype=float)
    if not np.isfinite(probabilities).all() or (
        (probabilities < 0) | (probabilities > 1)
    ).any():
        raise ValueError(f"{probability} must be finite and between zero and one.")
    reconstructed = probabilities * source[conditional].to_numpy(dtype=float)
    saved = source[expected].to_numpy(dtype=float)
    if not np.allclose(reconstructed, saved, rtol=1e-10, atol=1e-10):
        raise ValueError(
            f"Saved expected revenue does not equal probability times conditional "
            f"spending for {horizon} days."
        )

    result = source.rename(
        columns={
            CUSTOMER_ID: "customer_id",
            CUTOFF_DATE: "cutoff_date",
            "Hist_Segment": "hist_segment",
            "Recency": "recency_days",
            "Frequency": "purchase_frequency",
            "Monetary_Gross": "historical_gross_spending_gbp",
            probability: "purchase_probability",
            conditional: "conditional_expected_spending_gbp",
            expected: "personalized_expected_revenue_gbp",
            historical: "historical_rate_expected_revenue_gbp",
            segment: "segment_expected_revenue_gbp",
        }
    )
    result["horizon_days"] = horizon
    result["currency_code"] = "GBP"
    result["nonreturn_probability"] = 1.0 - result["purchase_probability"]
    result["nonreturn_weighted_conditional_spending_proxy_gbp"] = (
        result["nonreturn_probability"]
        * result["conditional_expected_spending_gbp"]
    )
    result["opportunity_proxy_method"] = OPPORTUNITY_PROXY_METHOD
    result["estimated_revenue_exposure_gbp"] = pd.Series(
        pd.NA, index=result.index, dtype="Float64"
    )
    result["exposure_status"] = EXPOSURE_NOT_ESTIMABLE
    result["exposure_method"] = None
    result["exposure_reference_definition"] = None
    result.attrs["horizon_days"] = horizon
    return result.sort_values("customer_id", kind="mergesort").reset_index(drop=True)


def compute_forecast_disagreement(
    forecasts: pd.DataFrame,
    horizon_days: int,
) -> pd.DataFrame:
    """Compare saved forecast methods without treating differences as losses."""
    horizon = _validate_horizon(horizon_days)
    required = [
        "customer_id",
        "cutoff_date",
        "horizon_days",
        "personalized_expected_revenue_gbp",
        "historical_rate_expected_revenue_gbp",
        "segment_expected_revenue_gbp",
    ]
    _require_columns(forecasts, required, name="forecasts")
    result = forecasts.loc[:, required].copy()
    if not result["horizon_days"].eq(horizon).all():
        raise ValueError("Forecast rows do not match the requested horizon.")
    value_columns = [
        "personalized_expected_revenue_gbp",
        "historical_rate_expected_revenue_gbp",
        "segment_expected_revenue_gbp",
    ]
    _finite_nonnegative(result, value_columns, name="Forecast values")
    result["historical_minus_personalized_forecast_difference_gbp"] = (
        result["historical_rate_expected_revenue_gbp"]
        - result["personalized_expected_revenue_gbp"]
    )
    result["segment_minus_personalized_forecast_difference_gbp"] = (
        result["segment_expected_revenue_gbp"]
        - result["personalized_expected_revenue_gbp"]
    )
    result["difference_interpretation"] = "forecast_model_disagreement_not_revenue_exposure"
    return result


def calculate_reference_exposure(
    current_forecasts: pd.DataFrame,
    reference_forecasts: pd.DataFrame | None,
    config: RevenueExposureConfig,
) -> pd.DataFrame:
    """Estimate shortfall only against a documented, exactly matched reference.

    This project has no eligible reference forecast in its saved artifacts.
    Passing ``None`` therefore produces nullable, explicitly unsupported
    exposure instead of a fabricated zero.
    """
    if not isinstance(config, RevenueExposureConfig):
        raise TypeError("config must be a RevenueExposureConfig.")
    keys = ["customer_id", "cutoff_date", "horizon_days"]
    _require_columns(
        current_forecasts,
        [*keys, "personalized_expected_revenue_gbp"],
        name="current_forecasts",
    )
    current = current_forecasts.copy()
    current["cutoff_date"] = pd.to_datetime(current["cutoff_date"], errors="raise")
    if current.duplicated(keys).any():
        raise ValueError("Current forecasts must be unique by customer, cutoff, and horizon.")

    current["estimated_revenue_exposure_gbp"] = pd.Series(
        pd.NA, index=current.index, dtype="Float64"
    )
    current["exposure_status"] = EXPOSURE_NOT_ESTIMABLE
    current["exposure_method"] = None
    current["exposure_reference_definition"] = None
    current["reference_expected_revenue_gbp"] = pd.Series(
        pd.NA, index=current.index, dtype="Float64"
    )
    if reference_forecasts is None or reference_forecasts.empty:
        current["exposure_reason"] = (
            "No defensible, chronologically valid matched reference forecast is available."
        )
        return current
    if not config.reference_definition or not config.reference_method:
        raise ValueError(
            "A non-empty reference definition and method are required for exposure."
        )

    _require_columns(
        reference_forecasts,
        [*keys, "reference_expected_revenue_gbp"],
        name="reference_forecasts",
    )
    reference = reference_forecasts.loc[
        :, [*keys, "reference_expected_revenue_gbp"]
    ].copy()
    reference["cutoff_date"] = pd.to_datetime(reference["cutoff_date"], errors="raise")
    if reference.duplicated(keys).any():
        raise ValueError("Reference forecasts must be unique by customer, cutoff, and horizon.")
    _finite_nonnegative(
        reference,
        ["reference_expected_revenue_gbp"],
        name="Reference expected revenue",
    )
    current_for_merge = current.drop(
        columns=["reference_expected_revenue_gbp"], errors="ignore"
    )
    matched = current_for_merge.merge(
        reference,
        on=keys,
        how="left",
        validate="one_to_one",
        indicator="_reference_match",
    )
    has_reference = matched["_reference_match"].eq("both")
    matched["reference_expected_revenue_gbp"] = matched[
        "reference_expected_revenue_gbp"
    ].astype("Float64")
    matched["estimated_revenue_exposure_gbp"] = (
        matched["reference_expected_revenue_gbp"]
        - matched["personalized_expected_revenue_gbp"]
    ).clip(lower=0).astype("Float64")
    matched.loc[~has_reference, "estimated_revenue_exposure_gbp"] = pd.NA
    matched["exposure_status"] = np.where(
        has_reference, "estimable", "reference_not_matched"
    )
    matched["exposure_method"] = np.where(
        has_reference, config.reference_method, None
    )
    matched["exposure_reference_definition"] = np.where(
        has_reference, config.reference_definition, None
    )
    matched["exposure_reason"] = np.where(
        has_reference,
        "Matched to the documented reference forecast.",
        "No reference forecast matched this customer, cutoff, and horizon.",
    )
    return matched.drop(columns="_reference_match")


def calculate_opportunity_proxy(
    forecasts: pd.DataFrame,
    config: RevenueExposureConfig,
) -> pd.DataFrame:
    """Return a nonreturn-weighted spending screening proxy, not recoverable loss."""
    if not isinstance(config, RevenueExposureConfig):
        raise TypeError("config must be a RevenueExposureConfig.")
    _require_columns(
        forecasts,
        ["purchase_probability", "conditional_expected_spending_gbp"],
        name="forecasts",
    )
    result = forecasts.copy()
    probability = pd.to_numeric(
        result["purchase_probability"], errors="raise"
    ).to_numpy(dtype=float)
    conditional = pd.to_numeric(
        result["conditional_expected_spending_gbp"], errors="raise"
    ).to_numpy(dtype=float)
    if (
        not np.isfinite(probability).all()
        or ((probability < 0) | (probability > 1)).any()
    ):
        raise ValueError("purchase_probability must be finite and within [0, 1].")
    if not np.isfinite(conditional).all() or (conditional < 0).any():
        raise ValueError("conditional_expected_spending_gbp must be finite and non-negative.")
    result["nonreturn_probability"] = 1.0 - probability
    result["nonreturn_weighted_conditional_spending_proxy_gbp"] = (
        result["nonreturn_probability"].to_numpy(dtype=float) * conditional
    )
    result["currency_code"] = config.currency_code
    result["opportunity_proxy_method"] = OPPORTUNITY_PROXY_METHOD
    result["opportunity_proxy_interpretation"] = (
        "Hypothetical screening proxy only; not observed loss or recoverable revenue."
    )
    return result


def summarize_portfolio_exposure(
    customer_table: pd.DataFrame,
    config: RevenueExposureConfig,
) -> dict[str, object]:
    """Summarize forecasts, disagreements, proxy coverage, and nullable exposure."""
    if not isinstance(config, RevenueExposureConfig):
        raise TypeError("config must be a RevenueExposureConfig.")
    required = [
        "customer_id",
        "horizon_days",
        "personalized_expected_revenue_gbp",
        "historical_rate_expected_revenue_gbp",
        "segment_expected_revenue_gbp",
        "nonreturn_weighted_conditional_spending_proxy_gbp",
        "exposure_status",
        "estimated_revenue_exposure_gbp",
    ]
    _require_columns(customer_table, required, name="customer_table")
    if customer_table["customer_id"].duplicated().any():
        raise ValueError("Portfolio customer IDs must be unique.")
    revenue_fields = [
        "personalized_expected_revenue_gbp",
        "historical_rate_expected_revenue_gbp",
        "segment_expected_revenue_gbp",
        "nonreturn_weighted_conditional_spending_proxy_gbp",
    ]
    _finite_nonnegative(customer_table, revenue_fields, name="Portfolio revenues")
    exposure = pd.to_numeric(
        customer_table["estimated_revenue_exposure_gbp"], errors="coerce"
    )
    exposure_valid = exposure.notna() & np.isfinite(exposure)
    if (exposure[exposure_valid] < 0).any():
        raise ValueError("Estimated revenue exposure cannot be negative.")
    matched_count = int(exposure_valid.sum())
    customer_count = int(customer_table["customer_id"].nunique())
    exposure_total = float(exposure[exposure_valid].sum()) if matched_count else None
    if matched_count == customer_count and customer_count:
        exposure_status = "estimable"
    elif matched_count:
        exposure_status = "partially_estimable"
    else:
        exposure_status = EXPOSURE_NOT_ESTIMABLE
    horizon_values = customer_table["horizon_days"].dropna().unique()
    if len(horizon_values) == 0 and customer_table.empty:
        horizon_values = np.asarray([customer_table.attrs.get("horizon_days")])
    if len(horizon_values) != 1 or pd.isna(horizon_values[0]):
        raise ValueError("Portfolio summary must contain exactly one horizon.")
    return {
        "cutoff_date": (
            pd.Timestamp(customer_table["cutoff_date"].iloc[0]).date().isoformat()
            if "cutoff_date" in customer_table and not customer_table.empty
            else None
        ),
        "horizon_days": int(horizon_values[0]),
        "eligible_customers": customer_count,
        "currency_code": config.currency_code,
        "personalized_expected_revenue_total_gbp": float(
            customer_table["personalized_expected_revenue_gbp"].sum()
        ),
        "historical_rate_forecast_total_gbp": float(
            customer_table["historical_rate_expected_revenue_gbp"].sum()
        ),
        "segment_forecast_total_gbp": float(
            customer_table["segment_expected_revenue_gbp"].sum()
        ),
        "historical_minus_personalized_forecast_difference_gbp": float(
            (
                customer_table["historical_rate_expected_revenue_gbp"]
                - customer_table["personalized_expected_revenue_gbp"]
            ).sum()
        ),
        "segment_minus_personalized_forecast_difference_gbp": float(
            (
                customer_table["segment_expected_revenue_gbp"]
                - customer_table["personalized_expected_revenue_gbp"]
            ).sum()
        ),
        "estimated_revenue_exposure_total_gbp": exposure_total,
        "exposure_coverage": matched_count / customer_count if customer_count else 0.0,
        "exposure_status": exposure_status,
        "exposure_method": (
            customer_table["exposure_method"].dropna().iloc[0]
            if "exposure_method" in customer_table
            and customer_table["exposure_method"].notna().any()
            else None
        ),
        "opportunity_proxy_total_gbp": float(
            customer_table[
                "nonreturn_weighted_conditional_spending_proxy_gbp"
            ].sum()
        ),
        "opportunity_proxy_method": OPPORTUNITY_PROXY_METHOD,
        "opportunity_proxy_interpretation": (
            "Screening proxy only; not estimated revenue exposure or recoverable revenue."
        ),
    }


def calculate_exposure_concentration(
    customer_table: pd.DataFrame,
    metric_column: str,
    proportions: tuple[float, ...] = (0.01, 0.05, 0.10),
) -> pd.DataFrame:
    """Calculate top-customer shares for a nonnegative financial quantity."""
    _require_columns(
        customer_table, ["customer_id", metric_column], name="customer_table"
    )
    if not proportions or any(
        not np.isfinite(value) or value <= 0 or value > 1 for value in proportions
    ):
        raise ValueError("proportions must contain values in (0, 1].")
    values = pd.to_numeric(customer_table[metric_column], errors="raise").to_numpy(
        dtype=float
    )
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError(f"{metric_column} must contain finite non-negative values.")
    ordered = customer_table.loc[:, ["customer_id", metric_column]].sort_values(
        [metric_column, "customer_id"],
        ascending=[False, True],
        kind="mergesort",
    )
    total = float(values.sum())
    count = len(ordered)
    rows = []
    for proportion in proportions:
        selected_count = min(count, int(np.ceil(count * proportion)))
        selected_total = float(ordered[metric_column].iloc[:selected_count].sum())
        rows.append(
            {
                "metric": metric_column,
                "top_customer_share": float(proportion),
                "selected_customers": selected_count,
                "portfolio_total_gbp": total,
                "selected_total_gbp": selected_total,
                "portfolio_share": selected_total / total if total > 0 else None,
                "status": "estimated" if total > 0 else "not_estimable_zero_total",
            }
        )
    return pd.DataFrame(rows)
