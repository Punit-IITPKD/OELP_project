"""Small reusable statistical summaries used by the research notebooks."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2, chi2_contingency, mannwhitneyu


DEFAULT_PERCENTILES = (0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99)


def summarize_numeric_features(
    frame: pd.DataFrame,
    columns: list[str] | tuple[str, ...] | None = None,
    *,
    percentiles: tuple[float, ...] = DEFAULT_PERCENTILES,
) -> pd.DataFrame:
    """Return descriptive statistics, including IQR and skewness by column."""
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError("frame must be a non-empty DataFrame.")
    selected = list(columns) if columns is not None else list(
        frame.select_dtypes(include="number").columns
    )
    if not selected:
        raise ValueError("At least one numeric column is required.")
    missing = [column for column in selected if column not in frame]
    if missing:
        raise ValueError(f"frame is missing requested columns: {missing}")
    data = frame.loc[:, selected].apply(pd.to_numeric, errors="raise")
    if np.isinf(data.to_numpy(dtype=float)).any():
        raise ValueError("Numeric summaries do not accept infinite values.")
    describe = data.describe(percentiles=list(percentiles)).T
    describe["iqr"] = describe["75%"] - describe["25%"]
    describe["skewness"] = data.skew()
    return describe


def cohens_h(proportion_a: float, proportion_b: float) -> float:
    """Cohen's h effect size for two proportions, matching Notebook 05."""
    values = np.asarray([proportion_a, proportion_b], dtype=float)
    if not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("Proportions must be finite values between zero and one.")
    return float(2 * (np.arcsin(np.sqrt(values[0])) - np.arcsin(np.sqrt(values[1]))))


def rank_biserial(u_statistic: float, n_a: int, n_b: int) -> float:
    """Rank-biserial correlation from the first sample's Mann–Whitney U."""
    if n_a <= 0 or n_b <= 0:
        raise ValueError("Both sample sizes must be positive.")
    if not np.isfinite(u_statistic) or not 0 <= u_statistic <= n_a * n_b:
        raise ValueError("u_statistic must be finite and between zero and n_a*n_b.")
    return float(1 - (2 * u_statistic) / (n_a * n_b))


def _validated_sample(values, name: str) -> np.ndarray:
    sample = np.asarray(values, dtype=float).reshape(-1)
    if not len(sample) or not np.isfinite(sample).all():
        raise ValueError(f"{name} must contain at least one finite observation.")
    return sample


def bootstrap_median_ci(
    values,
    *,
    n_boot: int = 2_000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Percentile bootstrap interval for a median, as used in Notebook 05."""
    sample = _validated_sample(values, "values")
    if not isinstance(n_boot, (int, np.integer)) or n_boot <= 0:
        raise ValueError("n_boot must be a positive integer.")
    if not np.isfinite(ci) or not 0 < ci < 1:
        raise ValueError("ci must be between zero and one.")
    rng = np.random.default_rng(seed)
    medians = [
        np.median(rng.choice(sample, size=len(sample), replace=True))
        for _ in range(n_boot)
    ]
    alpha = (1 - ci) / 2
    return (
        float(np.quantile(medians, alpha)),
        float(np.quantile(medians, 1 - alpha)),
    )


def bootstrap_proportion_ci(
    successes: int,
    n: int,
    *,
    n_boot: int = 2_000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Parametric bootstrap interval for a proportion, as used in Notebook 05."""
    if (
        not isinstance(n, (int, np.integer))
        or not isinstance(successes, (int, np.integer))
        or n <= 0
        or successes < 0
        or successes > n
    ):
        raise ValueError("successes and n must be integers with 0 <= successes <= n.")
    if not isinstance(n_boot, (int, np.integer)) or n_boot <= 0:
        raise ValueError("n_boot must be a positive integer.")
    if not np.isfinite(ci) or not 0 < ci < 1:
        raise ValueError("ci must be between zero and one.")
    rng = np.random.default_rng(seed)
    proportion = successes / n
    bootstrapped = [
        rng.binomial(n, proportion) / n for _ in range(n_boot)
    ]
    alpha = (1 - ci) / 2
    return (
        float(np.quantile(bootstrapped, alpha)),
        float(np.quantile(bootstrapped, 1 - alpha)),
    )


def _km_median(durations: np.ndarray, events: np.ndarray) -> float:
    """Kaplan–Meier median from observed/censored durations."""
    survival = 1.0
    for time in np.unique(durations):
        at_risk = int(np.count_nonzero(durations >= time))
        observed = int(np.count_nonzero((durations == time) & events))
        if observed:
            survival *= 1 - observed / at_risk
            if survival <= 0.5:
                return float(time)
    return float("inf")


def logrank_test_two_groups(
    durations_a,
    events_a,
    durations_b,
    events_b,
) -> dict[str, float]:
    """Two-sample log-rank test and Kaplan–Meier medians.

    Durations are observed times; event flags are one for the observed event
    (purchase) and zero for right-censoring. This reproduces Notebook 05 without
    treating an unobserved future purchase as permanent churn.
    """
    time_a = _validated_sample(durations_a, "durations_a")
    time_b = _validated_sample(durations_b, "durations_b")
    event_a = np.asarray(events_a).reshape(-1)
    event_b = np.asarray(events_b).reshape(-1)
    if len(time_a) != len(event_a) or len(time_b) != len(event_b):
        raise ValueError("Each event flag array must align with its duration array.")
    for name, events in (("events_a", event_a), ("events_b", event_b)):
        if pd.isna(events).any() or not np.isin(events, [0, 1, False, True]).all():
            raise ValueError(f"{name} must contain only binary event flags.")
    if (time_a < 0).any() or (time_b < 0).any():
        raise ValueError("Survival durations must be non-negative.")
    event_a = event_a.astype(bool)
    event_b = event_b.astype(bool)
    all_times = np.unique(np.concatenate([time_a, time_b]))
    observed_minus_expected = 0.0
    variance = 0.0
    for time in all_times:
        n_a = int(np.count_nonzero(time_a >= time))
        n_b = int(np.count_nonzero(time_b >= time))
        at_risk = n_a + n_b
        d_a = int(np.count_nonzero((time_a == time) & event_a))
        d_b = int(np.count_nonzero((time_b == time) & event_b))
        events = d_a + d_b
        if events == 0 or at_risk <= 1:
            continue
        expected_a = events * n_a / at_risk
        observed_minus_expected += d_a - expected_a
        variance += (
            n_a * n_b * events * (at_risk - events)
            / (at_risk**2 * (at_risk - 1))
        )
    if variance <= 0:
        raise ValueError("Log-rank test has no estimable event variance.")
    statistic = float(observed_minus_expected**2 / variance)
    return {
        "statistic": statistic,
        "p_value": float(chi2.sf(statistic, df=1)),
        "median_days_a": _km_median(time_a, event_a),
        "median_days_b": _km_median(time_b, event_b),
    }


def estimate_historical_gap_percentile(
    orders: pd.DataFrame,
    cutoff_date: pd.Timestamp,
    *,
    percentile: float = 90,
) -> tuple[float, int]:
    """Estimate a gap percentile using only distinct orders before cutoff."""
    required = {"Customer ID", "PurchaseDate"}
    missing = sorted(required.difference(orders.columns))
    if missing:
        raise ValueError(f"orders is missing required columns: {missing}")
    if not np.isfinite(percentile) or not 0 <= percentile <= 100:
        raise ValueError("percentile must be between zero and 100.")
    cutoff = pd.Timestamp(cutoff_date)
    data = orders.loc[:, ["Customer ID", "PurchaseDate"]].copy()
    data["PurchaseDate"] = pd.to_datetime(data["PurchaseDate"], errors="raise")
    data = data.loc[data["PurchaseDate"] < cutoff]
    gaps = []
    for _, group in data.groupby("Customer ID", sort=False):
        dates = np.sort(group["PurchaseDate"].drop_duplicates().to_numpy())
        if len(dates) >= 2:
            gaps.extend(np.diff(dates).astype("timedelta64[ns]").astype("int64") / 86_400_000_000_000)
    if not gaps:
        raise ValueError("At least one historical inter-purchase gap is required.")
    values = np.asarray(gaps, dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Historical gaps must be finite and non-negative.")
    return float(np.percentile(values, percentile)), int(len(values))


def validate_segment_outcomes(
    analysis: pd.DataFrame,
    *,
    segment_column: str = "Hist_Segment",
    active_label: str = "Recent / Active",
    lapsed_label: str = "Lapsed / At-Risk",
) -> dict[str, dict[str, float | str | None]]:
    """Reproduce Notebook 05's retrospective segment validation statistics."""
    required = {
        segment_column,
        "Purchased_90d",
        "FutureOrders_90d",
        "FutureRevenue_90d",
        "Survival_duration",
        "Event_flag",
    }
    missing = sorted(required.difference(analysis.columns))
    if missing:
        raise ValueError(f"analysis is missing validation columns: {missing}")
    if analysis.empty:
        raise ValueError("analysis must contain at least one row.")
    groups = {
        active_label: analysis.loc[analysis[segment_column].eq(active_label)],
        lapsed_label: analysis.loc[analysis[segment_column].eq(lapsed_label)],
    }
    if any(group.empty for group in groups.values()):
        raise ValueError("Both historical customer segments must contain observations.")
    if analysis[segment_column].isna().any():
        raise ValueError(f"{segment_column} cannot contain missing values.")

    active = groups[active_label]
    lapsed = groups[lapsed_label]
    n_active, n_lapsed = len(active), len(lapsed)
    k_active = int(pd.to_numeric(active["Purchased_90d"], errors="raise").sum())
    k_lapsed = int(pd.to_numeric(lapsed["Purchased_90d"], errors="raise").sum())
    purchase_values = pd.to_numeric(analysis["Purchased_90d"], errors="raise")
    if purchase_values.isna().any() or not purchase_values.isin([0, 1]).all():
        raise ValueError("Purchased_90d must be a complete binary outcome.")
    if not (0 <= k_active <= n_active and 0 <= k_lapsed <= n_lapsed):
        raise ValueError("Purchased_90d must be a binary outcome.")
    p_active, p_lapsed = k_active / n_active, k_lapsed / n_lapsed
    contingency = np.asarray(
        [[k_active, n_active - k_active], [k_lapsed, n_lapsed - k_lapsed]],
        dtype=int,
    )
    chi_square, chi_p, _, _ = chi2_contingency(contingency)

    output: dict[str, dict[str, float | str | None]] = {
        "binary_90d_purchase": {
            "test": "chi-square",
            "chi2": round(float(chi_square), 4),
            "p_value": float(f"{chi_p:.6e}"),
            "purchase_rate_active": round(p_active, 4),
            "purchase_rate_lapsed": round(p_lapsed, 4),
            "cohens_h": round(cohens_h(p_active, p_lapsed), 4),
        }
    }
    for key, column in (
        ("order_count_90d", "FutureOrders_90d"),
        ("revenue_90d", "FutureRevenue_90d"),
    ):
        active_values = _validated_sample(active[column], column)
        lapsed_values = _validated_sample(lapsed[column], column)
        u_statistic, p_value = mannwhitneyu(
            active_values, lapsed_values, alternative="two-sided"
        )
        output[key] = {
            "test": "mann_whitney_u",
            "U": float(u_statistic),
            "p_value": float(f"{p_value:.6e}"),
            "median_active": round(float(np.median(active_values)), 2),
            "median_lapsed": round(float(np.median(lapsed_values)), 2),
            "rank_biserial_r": round(
                rank_biserial(u_statistic, len(active_values), len(lapsed_values)), 4
            ),
        }

    survival = logrank_test_two_groups(
        active["Survival_duration"],
        active["Event_flag"],
        lapsed["Survival_duration"],
        lapsed["Event_flag"],
    )
    output["survival_logrank"] = {
        "test": "log_rank",
        "statistic": round(survival["statistic"], 4),
        "p_value": float(f"{survival['p_value']:.6e}"),
        "median_days_active": (
            survival["median_days_a"]
            if np.isfinite(survival["median_days_a"])
            else None
        ),
        "median_days_lapsed": (
            survival["median_days_b"]
            if np.isfinite(survival["median_days_b"])
            else None
        ),
        "note": "Survival durations in fractional days (total_seconds/86400)",
    }
    return output


def validate_threshold_baseline(
    analysis: pd.DataFrame,
    training_p90_threshold_days: float,
    *,
    full_year_p90_days: float = 101.9,
) -> dict[str, float | str]:
    """Reproduce Notebook 05's descriptive recency-threshold comparison."""
    required = {"Recency", "Purchased_90d"}
    missing = sorted(required.difference(analysis.columns))
    if missing:
        raise ValueError(f"analysis is missing threshold-baseline columns: {missing}")
    for value, name in (
        (training_p90_threshold_days, "training_p90_threshold_days"),
        (full_year_p90_days, "full_year_p90_days"),
    ):
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative.")
    recency = pd.to_numeric(analysis["Recency"], errors="raise")
    purchased = pd.to_numeric(analysis["Purchased_90d"], errors="raise")
    if recency.isna().any() or purchased.isna().any() or not purchased.isin([0, 1]).all():
        raise ValueError("Recency and Purchased_90d must be complete; purchase must be binary.")
    at_risk = recency > training_p90_threshold_days
    n_at_risk = int(at_risk.sum())
    n_not_at_risk = int((~at_risk).sum())
    if not n_at_risk or not n_not_at_risk:
        raise ValueError("The threshold must create non-empty at-risk and not-at-risk groups.")
    p_at_risk = float(purchased.loc[at_risk].mean())
    p_not_at_risk = float(purchased.loc[~at_risk].mean())
    successes_at_risk = int(purchased.loc[at_risk].sum())
    successes_not_at_risk = int(purchased.loc[~at_risk].sum())
    contingency = np.asarray(
        [
            [successes_at_risk, n_at_risk - successes_at_risk],
            [successes_not_at_risk, n_not_at_risk - successes_not_at_risk],
        ],
        dtype=int,
    )
    chi_square, p_value, _, _ = chi2_contingency(contingency)
    return {
        "training_p90_threshold_days": round(float(training_p90_threshold_days), 2),
        "full_year_p90_nb03": round(float(full_year_p90_days), 2),
        "chi2": round(float(chi_square), 4),
        "p_value": float(f"{p_value:.6e}"),
        "cohens_h": round(cohens_h(p_not_at_risk, p_at_risk), 4),
        "purchase_rate_not_atrisk": round(p_not_at_risk, 4),
        "purchase_rate_atrisk": round(p_at_risk, 4),
        "comparison_note": (
            "Cohen h values for K-Means and threshold are descriptive only; "
            "not comparable as predictive metrics — base rates differ."
        ),
    }
