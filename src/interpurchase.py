"""Reusable inter-purchase gap summaries and fitted distribution statistics."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from src.data_preparation import clean_transactions

SECONDS_PER_DAY = 86_400.0


def build_interpurchase_gaps(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return one row per valid consecutive invoice gap.

    Invoice timestamps use the earliest line-item time per customer and invoice.
    Cancellation invoices are excluded. Zero-day gaps are retained for
    investigation; distribution fitting excludes them, as in Notebook 03.
    """
    data = clean_transactions(transactions)
    purchase_rows = data.loc[
        ~data["Invoice"].astype(str).str.startswith("C")
    ]
    order_times = (
        purchase_rows.groupby(["Customer ID", "Invoice"], as_index=False)
        .agg(InvoiceDate=("InvoiceDate", "min"))
        .sort_values(["Customer ID", "InvoiceDate", "Invoice"])
        .reset_index(drop=True)
    )
    order_times["gap_days"] = (
        order_times.groupby("Customer ID", sort=False)["InvoiceDate"]
        .diff()
        .dt.total_seconds()
        .div(SECONDS_PER_DAY)
    )
    gaps = order_times.dropna(subset=["gap_days"]).copy()
    values = gaps["gap_days"].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Inter-purchase gaps must be finite and non-negative.")
    return gaps.reset_index(drop=True)


def summarize_interpurchase_gaps(gap_rows: pd.DataFrame) -> pd.DataFrame:
    """Summarize each customer's observed gaps without imputing single orders."""
    required = {"Customer ID", "gap_days"}
    missing = sorted(required.difference(gap_rows.columns))
    if missing:
        raise ValueError(f"gap_rows is missing required columns: {missing}")
    data = gap_rows.dropna(subset=["gap_days"]).copy()
    if data.empty:
        return pd.DataFrame(
            columns=[
                "Customer ID",
                "Gap_Count",
                "Mean_InterPurchase_Days",
                "Median_InterPurchase_Days",
                "Std_InterPurchase_Days",
                "Min_InterPurchase_Days",
                "Max_InterPurchase_Days",
            ]
        )
    values = pd.to_numeric(data["gap_days"], errors="raise")
    if not np.isfinite(values.to_numpy(dtype=float)).all() or values.lt(0).any():
        raise ValueError("gap_days must contain finite non-negative values.")
    summary = (
        data.assign(gap_days=values)
        .groupby("Customer ID", as_index=False)
        .agg(
            Gap_Count=("gap_days", "size"),
            Mean_InterPurchase_Days=("gap_days", "mean"),
            Median_InterPurchase_Days=("gap_days", "median"),
            Std_InterPurchase_Days=("gap_days", "std"),
            Min_InterPurchase_Days=("gap_days", "min"),
            Max_InterPurchase_Days=("gap_days", "max"),
        )
    )
    return summary


def fit_interpurchase_distributions(gap_rows: pd.DataFrame) -> pd.DataFrame:
    """Fit Notebook 03's four zero-location distributions by maximum likelihood.

    Only strictly positive gaps are fitted. The KS statistic is returned for
    directional comparison; its standard p-value is intentionally omitted
    because parameters were estimated on the same observations.
    """
    if "gap_days" not in gap_rows:
        raise ValueError("gap_rows must contain a gap_days column.")
    gaps = pd.to_numeric(gap_rows["gap_days"], errors="coerce").dropna().to_numpy(
        dtype=float
    )
    if not np.isfinite(gaps).all() or (gaps < 0).any():
        raise ValueError("gap_days must contain finite non-negative values.")
    gaps = gaps[gaps > 0]
    if len(gaps) < 3:
        raise ValueError("At least three positive inter-purchase gaps are required.")

    candidates = (
        ("Exponential", 1, stats.expon),
        ("Weibull", 2, stats.weibull_min),
        ("Gamma", 2, stats.gamma),
        ("Log-Normal", 2, stats.lognorm),
    )
    rows: list[dict[str, Any]] = []
    for name, parameter_count, distribution in candidates:
        parameters = tuple(float(x) for x in distribution.fit(gaps, floc=0))
        log_likelihood = float(np.sum(distribution.logpdf(gaps, *parameters)))
        ks_statistic = float(stats.kstest(gaps, distribution.cdf, args=parameters).statistic)
        if not np.isfinite(log_likelihood) or not np.isfinite(ks_statistic):
            raise ValueError(f"{name} fit returned non-finite statistics.")
        p90 = float(distribution.ppf(0.90, *parameters))
        p95 = float(distribution.ppf(0.95, *parameters))
        padded_parameters = (*parameters, None, None, None)[:3]
        rows.append(
            {
                "distribution": name,
                "k_params": parameter_count,
                "n_observations": int(len(gaps)),
                "log_likelihood": round(log_likelihood, 4),
                "aic": round(2 * parameter_count - 2 * log_likelihood, 4),
                "bic": round(parameter_count * np.log(len(gaps)) - 2 * log_likelihood, 4),
                "ks_statistic": round(ks_statistic, 6),
                "p90_model_days": round(p90, 2) if np.isfinite(p90) else np.nan,
                "p95_model_days": round(p95, 2) if np.isfinite(p95) else np.nan,
                "param1": round(padded_parameters[0], 6),
                "param2": (
                    round(padded_parameters[1], 6)
                    if padded_parameters[1] is not None
                    else np.nan
                ),
                "param3": (
                    round(padded_parameters[2], 6)
                    if padded_parameters[2] is not None
                    else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)
