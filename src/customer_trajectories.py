"""Exposure-aware, pre-cutoff customer purchasing trajectories.

The first observed transaction is a left-truncation boundary, not proof of the
customer's acquisition date. No time before that transaction is treated as
observed inactivity.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.behavior_monitor import prepare_purchase_events

CUSTOMER_ID = "Customer ID"
PURCHASE_DATE = "PurchaseDate"
INVOICE = "Invoice"
GROSS_REVENUE = "GrossRevenue"

TRAJECTORY_COLUMNS = [
    CUSTOMER_ID,
    "cutoff_date",
    "window_index",
    "window_start",
    "window_end",
    "first_observed_purchase_date",
    "observed_exposure_days",
    "purchase_count",
    "gross_revenue",
    "purchase_rate_per_observed_day",
    "revenue_rate_per_observed_day",
    "window_has_purchase",
    "window_observation_status",
    "history_length_days",
    "pre_cutoff_purchase_count",
    "pre_cutoff_gross_revenue",
    "completed_purchase_gaps",
    "completed_gap_slope_days_per_gap",
]


@dataclass(frozen=True)
class TrajectoryConfig:
    """Time grid and minimum support for descriptive trajectories and FDA."""

    window_days: int = 30
    lookback_days: int = 180
    min_summary_observed_windows: int = 4
    min_summary_active_windows: int = 2
    min_functional_observed_windows: int = 6
    min_functional_active_windows: int = 3

    def __post_init__(self) -> None:
        for name in (
            "window_days",
            "lookback_days",
            "min_summary_observed_windows",
            "min_summary_active_windows",
            "min_functional_observed_windows",
            "min_functional_active_windows",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer.")
        if self.lookback_days % self.window_days:
            raise ValueError("lookback_days must be an integer multiple of window_days.")
        if self.min_summary_observed_windows > self.window_count:
            raise ValueError("Summary support cannot require more windows than the grid.")
        if self.min_functional_observed_windows > self.window_count:
            raise ValueError("Functional support cannot require more windows than the grid.")
        if self.min_summary_active_windows > self.window_count:
            raise ValueError("Summary active-window support exceeds the configured grid.")
        if self.min_functional_active_windows > self.window_count:
            raise ValueError("Functional active-window support exceeds the configured grid.")

    @property
    def window_count(self) -> int:
        return self.lookback_days // self.window_days

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


DEFAULT_CONFIG = TrajectoryConfig()


def _validate_cutoff(cutoff_date: Any) -> pd.Timestamp:
    cutoff = pd.Timestamp(cutoff_date)
    if pd.isna(cutoff) or cutoff.tz is not None:
        raise ValueError("cutoff_date must be a valid timezone-naive timestamp.")
    return cutoff


def _empty_trajectory_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=TRAJECTORY_COLUMNS)


def _completed_gap_summary(events: pd.DataFrame) -> pd.DataFrame:
    gaps = events[[CUSTOMER_ID, PURCHASE_DATE]].copy()
    gaps["completed_gap_days"] = (
        gaps.groupby(CUSTOMER_ID, sort=False)[PURCHASE_DATE]
        .diff()
        .dt.total_seconds()
        .div(86_400)
    )
    result = (
        gaps.groupby(CUSTOMER_ID, as_index=False, sort=False)
        .agg(
            completed_purchase_gaps=("completed_gap_days", "count"),
            completed_gap_slope_days_per_gap=("completed_gap_days", _gap_slope),
        )
    )
    return result


def _gap_slope(values: pd.Series) -> float:
    observed = values.dropna().to_numpy(dtype=float)
    if len(observed) < 3:
        return float("nan")
    return float(np.polyfit(np.arange(len(observed), dtype=float), observed, 1)[0])


def build_customer_trajectory_matrix(
    purchase_events: pd.DataFrame,
    cutoff_date: Any,
    window_days: int = 30,
    lookback_days: int = 180,
) -> pd.DataFrame:
    """Build a customer-by-window table using purchases strictly before cutoff.

    Windows are half-open calendar intervals anchored to the cutoff and listed
    oldest first. Exposure begins at the later of the window start and the
    customer's first observed purchase. A window before that point has missing
    counts/rates and status ``pre_observation``; it is not an observed zero.
    """
    config = TrajectoryConfig(
        window_days=window_days,
        lookback_days=lookback_days,
        min_summary_observed_windows=min(4, lookback_days // window_days),
        min_summary_active_windows=min(2, lookback_days // window_days),
        min_functional_observed_windows=lookback_days // window_days,
        min_functional_active_windows=min(3, lookback_days // window_days),
    )
    cutoff = _validate_cutoff(cutoff_date)
    events = prepare_purchase_events(purchase_events)
    events = events.loc[events[GROSS_REVENUE].gt(0)].copy()
    events = events.loc[events[PURCHASE_DATE].lt(cutoff)].copy()
    if events.empty:
        return _empty_trajectory_frame()

    first = (
        events.groupby(CUSTOMER_ID, sort=False)[PURCHASE_DATE]
        .min()
        .rename("first_observed_purchase_date")
    )
    customer_ids = first.index.to_numpy()
    window_indices = np.arange(config.window_count, dtype=int)
    lookback_start = cutoff - pd.Timedelta(days=lookback_days)
    starts = pd.DatetimeIndex(
        [lookback_start + pd.Timedelta(days=i * window_days) for i in window_indices]
    )
    ends = starts + pd.Timedelta(days=window_days)

    grid = pd.DataFrame(
        {
            CUSTOMER_ID: np.repeat(customer_ids, config.window_count),
            "window_index": np.tile(window_indices, len(customer_ids)),
        }
    )
    grid = grid.merge(first, left_on=CUSTOMER_ID, right_index=True, how="left")
    grid["cutoff_date"] = cutoff
    grid["window_start"] = starts.take(grid["window_index"].to_numpy()).to_numpy()
    grid["window_end"] = ends.take(grid["window_index"].to_numpy()).to_numpy()
    effective_start = grid["window_start"].where(
        grid["window_start"].ge(grid["first_observed_purchase_date"]),
        grid["first_observed_purchase_date"],
    )
    effective_end = grid["window_end"].where(grid["window_end"].le(cutoff), cutoff)
    exposure = (effective_end - effective_start).dt.total_seconds().div(86_400)
    grid["observed_exposure_days"] = exposure.clip(lower=0.0)

    within_grid = events.loc[
        events[PURCHASE_DATE].ge(lookback_start)
        & events[PURCHASE_DATE].lt(cutoff)
    ].copy()
    within_grid["window_index"] = np.floor(
        (within_grid[PURCHASE_DATE] - lookback_start).dt.total_seconds()
        / (window_days * 86_400)
    ).astype(int)
    observed_orders = (
        within_grid.groupby([CUSTOMER_ID, "window_index"], as_index=False, sort=False)
        .agg(
            purchase_count=(INVOICE, "nunique"),
            gross_revenue=(GROSS_REVENUE, "sum"),
        )
    )
    grid = grid.merge(
        observed_orders,
        on=[CUSTOMER_ID, "window_index"],
        how="left",
        validate="one_to_one",
    )
    exposed = grid["observed_exposure_days"].gt(0)
    grid["purchase_count"] = pd.to_numeric(grid["purchase_count"], errors="coerce").astype(
        "Int64"
    )
    grid.loc[exposed & grid["purchase_count"].isna(), "purchase_count"] = 0
    grid.loc[~exposed, "purchase_count"] = pd.NA
    grid["gross_revenue"] = pd.to_numeric(grid["gross_revenue"], errors="coerce")
    grid.loc[exposed & grid["gross_revenue"].isna(), "gross_revenue"] = 0.0
    grid.loc[~exposed, "gross_revenue"] = np.nan
    denominator = grid["observed_exposure_days"].where(exposed)
    grid["purchase_rate_per_observed_day"] = (
        grid["purchase_count"].astype("float64") / denominator
    )
    grid["revenue_rate_per_observed_day"] = grid["gross_revenue"] / denominator
    grid["window_has_purchase"] = grid["purchase_count"].gt(0).astype("boolean")
    grid["window_observation_status"] = np.select(
        [
            ~exposed,
            grid["observed_exposure_days"].lt(window_days - 1e-9),
        ],
        ["pre_observation", "partially_exposed"],
        default="fully_exposed",
    )
    grid["history_length_days"] = (
        cutoff - grid["first_observed_purchase_date"]
    ).dt.total_seconds().div(86_400)

    totals = (
        events.groupby(CUSTOMER_ID, as_index=False, sort=False)
        .agg(
            pre_cutoff_purchase_count=(INVOICE, "nunique"),
            pre_cutoff_gross_revenue=(GROSS_REVENUE, "sum"),
        )
    )
    gaps = _completed_gap_summary(events)
    grid = grid.merge(totals, on=CUSTOMER_ID, how="left", validate="many_to_one")
    grid = grid.merge(gaps, on=CUSTOMER_ID, how="left", validate="many_to_one")
    return (
        grid.loc[:, TRAJECTORY_COLUMNS]
        .sort_values([CUSTOMER_ID, "window_index"], kind="mergesort")
        .reset_index(drop=True)
    )


def _slope(index: np.ndarray, values: np.ndarray) -> float:
    finite = np.isfinite(index) & np.isfinite(values)
    if finite.sum() < 3:
        return float("nan")
    return float(np.polyfit(index[finite], values[finite], 1)[0])


def _longest_inactive_run(observed: np.ndarray, active: np.ndarray) -> int:
    longest = current = 0
    for is_observed, is_active in zip(observed, active, strict=False):
        if is_observed and not is_active:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def calculate_trajectory_features(
    trajectory_matrix: pd.DataFrame,
    config: TrajectoryConfig | None = None,
) -> pd.DataFrame:
    """Calculate supported trajectory summaries, leaving unsupported values null."""
    config = config or DEFAULT_CONFIG
    required = {
        CUSTOMER_ID,
        "cutoff_date",
        "window_index",
        "observed_exposure_days",
        "purchase_count",
        "gross_revenue",
        "purchase_rate_per_observed_day",
        "revenue_rate_per_observed_day",
        "history_length_days",
        "pre_cutoff_purchase_count",
        "pre_cutoff_gross_revenue",
        "completed_purchase_gaps",
        "completed_gap_slope_days_per_gap",
    }
    missing = sorted(required.difference(trajectory_matrix.columns))
    if missing:
        raise ValueError(f"trajectory_matrix is missing columns: {missing}")
    if trajectory_matrix.empty:
        return pd.DataFrame()
    if trajectory_matrix.duplicated([CUSTOMER_ID, "cutoff_date", "window_index"]).any():
        raise ValueError("Each customer, cutoff, and window must be unique.")

    rows: list[dict[str, Any]] = []
    for customer_id, group in trajectory_matrix.groupby(CUSTOMER_ID, sort=False):
        group = group.sort_values("window_index", kind="mergesort")
        observed = group["observed_exposure_days"].to_numpy(dtype=float) > 0
        counts = group["purchase_count"].astype("float64").to_numpy()
        active = np.isfinite(counts) & (counts > 0)
        purchase_rates = group["purchase_rate_per_observed_day"].to_numpy(dtype=float)
        revenue_rates = group["revenue_rate_per_observed_day"].to_numpy(dtype=float)
        window_index = group["window_index"].to_numpy(dtype=float)
        observed_purchase_rates = purchase_rates[observed]
        observed_revenue_rates = revenue_rates[observed]
        observed_indices = window_index[observed]
        active_count = int(active.sum())
        observed_count = int(observed.sum())
        gap_count = int(group["completed_purchase_gaps"].iloc[0])
        summary_eligible = (
            observed_count >= config.min_summary_observed_windows
            and active_count >= config.min_summary_active_windows
            and gap_count >= 1
        )
        functional_eligible = (
            observed_count >= config.min_functional_observed_windows
            and observed_count == config.window_count
            and active_count >= config.min_functional_active_windows
            and gap_count >= 2
        )
        if functional_eligible:
            sufficiency = "sufficient_for_functional_analysis"
        elif summary_eligible:
            sufficiency = "sufficient_for_summary_trajectory"
        elif observed_count >= 2 or active_count >= 1:
            sufficiency = "limited_history"
        else:
            sufficiency = "insufficient_history"

        early_late_supported = observed_count >= 4
        rows.append(
            {
                CUSTOMER_ID: customer_id,
                "cutoff_date": group["cutoff_date"].iloc[0],
                "first_observed_purchase_date": group[
                    "first_observed_purchase_date"
                ].iloc[0],
                "history_length_days": float(group["history_length_days"].iloc[0]),
                "pre_cutoff_purchase_count": int(
                    group["pre_cutoff_purchase_count"].iloc[0]
                ),
                "pre_cutoff_gross_revenue": float(
                    group["pre_cutoff_gross_revenue"].iloc[0]
                ),
                "observed_windows": observed_count,
                "active_purchase_windows": active_count,
                "completed_purchase_gaps": gap_count,
                "mean_purchase_rate_per_observed_day": (
                    float(np.nanmean(observed_purchase_rates))
                    if observed_count
                    else np.nan
                ),
                "mean_revenue_rate_per_observed_day": (
                    float(np.nanmean(observed_revenue_rates))
                    if observed_count
                    else np.nan
                ),
                "purchase_rate_slope_per_window": _slope(
                    observed_indices, observed_purchase_rates
                ),
                "revenue_rate_slope_per_window": _slope(
                    observed_indices, observed_revenue_rates
                ),
                "purchase_rate_volatility": (
                    float(np.nanstd(observed_purchase_rates, ddof=1))
                    if observed_count >= 3
                    else np.nan
                ),
                "revenue_rate_volatility": (
                    float(np.nanstd(observed_revenue_rates, ddof=1))
                    if observed_count >= 3
                    else np.nan
                ),
                "purchase_rate_recent_minus_early": (
                    float(np.nanmean(observed_purchase_rates[-2:])
                          - np.nanmean(observed_purchase_rates[:2]))
                    if early_late_supported
                    else np.nan
                ),
                "revenue_rate_recent_minus_early": (
                    float(np.nanmean(observed_revenue_rates[-2:])
                          - np.nanmean(observed_revenue_rates[:2]))
                    if early_late_supported
                    else np.nan
                ),
                "longest_observed_inactive_run": _longest_inactive_run(
                    observed, active
                ),
                "completed_gap_slope_days_per_gap": float(
                    group["completed_gap_slope_days_per_gap"].iloc[0]
                ),
                "history_sufficiency": sufficiency,
                "eligible_for_summary_trajectory": bool(summary_eligible),
                "eligible_for_functional_analysis": bool(functional_eligible),
                "limitations": _limitations(
                    observed_count,
                    active_count,
                    gap_count,
                    config,
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(CUSTOMER_ID, kind="mergesort").reset_index(
        drop=True
    )


def _limitations(
    observed_windows: int,
    active_windows: int,
    completed_gaps: int,
    config: TrajectoryConfig,
) -> list[str]:
    limitations: list[str] = []
    if observed_windows < config.min_summary_observed_windows:
        limitations.append("insufficient_observed_windows_for_summary_trajectory")
    if active_windows < config.min_summary_active_windows:
        limitations.append("insufficient_active_windows_for_summary_trajectory")
    if completed_gaps < 3:
        limitations.append("insufficient_completed_gaps_for_gap_trend")
    if observed_windows < config.window_count or active_windows < config.min_functional_active_windows:
        limitations.append("insufficient_support_for_functional_representation")
    return limitations


def assess_trajectory_sufficiency(
    trajectory_matrix: pd.DataFrame,
    config: TrajectoryConfig | None = None,
) -> pd.DataFrame:
    """Return per-customer history support and explicit method eligibility."""
    columns = [
        CUSTOMER_ID,
        "cutoff_date",
        "observed_windows",
        "active_purchase_windows",
        "completed_purchase_gaps",
        "history_sufficiency",
        "eligible_for_summary_trajectory",
        "eligible_for_functional_analysis",
        "limitations",
    ]
    features = calculate_trajectory_features(trajectory_matrix, config)
    return features.reindex(columns=columns)


def build_customer_trajectory(
    customer_id: Any,
    purchase_events: pd.DataFrame,
    cutoff_date: Any,
    config: TrajectoryConfig,
) -> pd.DataFrame:
    """Return one customer's supported fixed-window history before cutoff."""
    matrix = build_customer_trajectory_matrix(
        purchase_events,
        cutoff_date,
        window_days=config.window_days,
        lookback_days=config.lookback_days,
    )
    customer = matrix.loc[matrix[CUSTOMER_ID].eq(customer_id)].reset_index(drop=True)
    if customer.empty:
        raise KeyError(customer_id)
    return customer


def validate_trajectory_leakage(
    original_events: pd.DataFrame,
    future_extended_events: pd.DataFrame,
    cutoff_date: Any,
    config: TrajectoryConfig,
) -> dict[str, bool]:
    """Verify future rows do not alter pre-cutoff trajectories or features."""
    original_matrix = build_customer_trajectory_matrix(
        original_events,
        cutoff_date,
        window_days=config.window_days,
        lookback_days=config.lookback_days,
    )
    extended_matrix = build_customer_trajectory_matrix(
        future_extended_events,
        cutoff_date,
        window_days=config.window_days,
        lookback_days=config.lookback_days,
    )
    pd.testing.assert_frame_equal(
        original_matrix.reset_index(drop=True),
        extended_matrix.reset_index(drop=True),
        check_dtype=False,
        check_like=False,
    )
    original_features = calculate_trajectory_features(original_matrix, config)
    extended_features = calculate_trajectory_features(extended_matrix, config)
    pd.testing.assert_frame_equal(
        original_features.reset_index(drop=True),
        extended_features.reset_index(drop=True),
        check_dtype=False,
        check_like=False,
    )
    return {
        "trajectory_matrix_unchanged": True,
        "trajectory_features_unchanged": True,
    }
