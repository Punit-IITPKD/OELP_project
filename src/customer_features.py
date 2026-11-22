"""Customer-level descriptive features matching Notebook 02."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer

from src.data_preparation import clean_transactions
from src.interpurchase import build_interpurchase_gaps, summarize_interpurchase_gaps

CUSTOMER_FEATURE_COLUMNS = (
    "Customer ID",
    "Recency",
    "Frequency",
    "Monetary_Gross",
    "Monetary_Net",
    "AOV",
    "Median_InterPurchase_Days",
    "Cancellation_Count",
    "Cancellation_Rate",
    "Monetary",
    "Recency_Transformed",
    "Frequency_Transformed",
    "Monetary_Transformed",
    "AOV_Transformed",
    "Median_InterPurchase_Transformed",
)


def _yeo_johnson(values: pd.Series) -> np.ndarray:
    """Fit Notebook 02's standardized Yeo-Johnson transform on present values."""
    numeric = pd.to_numeric(values, errors="raise")
    result = np.full(len(numeric), np.nan, dtype=float)
    present = numeric.notna().to_numpy()
    sample = numeric.loc[present].to_numpy(dtype=float).reshape(-1, 1)
    if not len(sample):
        return result
    if len(sample) < 2 or np.all(sample == sample[0]):
        result[present] = 0.0
        return result
    result[present] = PowerTransformer(method="yeo-johnson").fit_transform(sample).ravel()
    return result


def build_customer_features(
    transactions: pd.DataFrame,
    *,
    reference_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Build Notebook 02's 15-column Year 1 customer-feature table.

    Valid purchases are non-cancellation invoices. Frequency counts distinct
    purchase invoices; gross monetary value sums those purchase lines. Net
    monetary value includes all transaction lines, including cancellations.
    Gaps use earliest invoice timestamps and remain missing for one-order
    customers.
    """
    data = clean_transactions(transactions)
    if data.empty:
        raise ValueError("No customer-linked transactions remain after cleaning.")
    if reference_date is None:
        reference = data["InvoiceDate"].max() + pd.Timedelta(days=1)
    else:
        reference = pd.Timestamp(reference_date)
    if pd.isna(reference):
        raise ValueError("reference_date must be a valid timestamp.")

    data = data.copy()
    data["_line_revenue"] = data["Quantity"].astype(float) * data["Price"].astype(float)
    cancellation = data["Invoice"].astype(str).str.startswith("C")
    purchases = data.loc[~cancellation].copy()
    if purchases.empty:
        raise ValueError("No valid purchase invoices are available for feature creation.")

    orders = (
        purchases.groupby(["Customer ID", "Invoice"], as_index=False)
        .agg(
            InvoiceDate=("InvoiceDate", "min"),
            OrderRevenue=("_line_revenue", "sum"),
        )
    )
    features = (
        orders.groupby("Customer ID", as_index=False)
        .agg(
            LastPurchaseDate=("InvoiceDate", "max"),
            Frequency=("Invoice", "nunique"),
            Monetary_Gross=("OrderRevenue", "sum"),
            AOV=("OrderRevenue", "mean"),
        )
    )
    features["Recency"] = (reference - features["LastPurchaseDate"]).dt.days
    features["Monetary_Net"] = (
        data.groupby("Customer ID")["_line_revenue"].sum().reindex(features["Customer ID"]).to_numpy()
    )

    cancellation_count = (
        data.loc[cancellation]
        .groupby("Customer ID")["Invoice"]
        .nunique()
        .reindex(features["Customer ID"], fill_value=0)
        .to_numpy(dtype=int)
    )
    features["Cancellation_Count"] = cancellation_count
    features["Cancellation_Rate"] = cancellation_count / (
        features["Frequency"].to_numpy(dtype=float) + cancellation_count
    )

    gap_rows = build_interpurchase_gaps(data)
    gap_summary = summarize_interpurchase_gaps(gap_rows)
    median_gaps = gap_summary.set_index("Customer ID")["Median_InterPurchase_Days"]
    features["Median_InterPurchase_Days"] = (
        features["Customer ID"].map(median_gaps).astype(float)
    )
    features["Monetary"] = features["Monetary_Gross"]

    features["Recency_Transformed"] = _yeo_johnson(features["Recency"])
    features["Frequency_Transformed"] = np.log1p(features["Frequency"].astype(float))
    features["Monetary_Transformed"] = _yeo_johnson(features["Monetary"])
    features["AOV_Transformed"] = _yeo_johnson(features["AOV"])
    features["Median_InterPurchase_Transformed"] = _yeo_johnson(
        features["Median_InterPurchase_Days"]
    )
    return features.loc[:, CUSTOMER_FEATURE_COLUMNS].sort_values(
        "Customer ID"
    ).reset_index(drop=True)
