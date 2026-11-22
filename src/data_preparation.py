"""Transaction validation and the documented Notebook 01 cleaning decisions."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

TRANSACTION_COLUMNS = (
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
)


def _validate_transaction_schema(transactions: pd.DataFrame) -> None:
    if not isinstance(transactions, pd.DataFrame):
        raise TypeError("transactions must be a pandas DataFrame.")
    missing = [column for column in TRANSACTION_COLUMNS if column not in transactions]
    if missing:
        raise ValueError(f"transactions is missing required columns: {missing}")


def clean_transactions(
    transactions: pd.DataFrame,
    *,
    return_report: bool = False,
) -> pd.DataFrame | tuple[pd.DataFrame, dict[str, Any]]:
    """Apply the established transaction cleaning rules without mutating input.

    Exact duplicate rows are dropped and transactions without a customer ID are
    excluded because they cannot be attributed to a customer. Customer-linked
    cancellations, returns, zero-price lines, and extreme values are retained.
    This matches the Notebook 01 processed transaction data.

    Set ``return_report=True`` to receive counts and the cleaning decisions
    alongside the cleaned frame.
    """
    _validate_transaction_schema(transactions)
    data = transactions.loc[:, TRANSACTION_COLUMNS].copy()
    input_rows = len(data)

    data["Invoice"] = data["Invoice"].astype("string")
    if data["Invoice"].isna().any():
        raise ValueError("Invoice cannot be missing.")
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="raise")
    if data["InvoiceDate"].isna().any():
        raise ValueError("InvoiceDate cannot be missing.")

    for column in ("Quantity", "Price"):
        data[column] = pd.to_numeric(data[column], errors="raise")
        non_missing = data[column].dropna().to_numpy(dtype=float)
        if not np.isfinite(non_missing).all():
            raise ValueError(f"{column} must contain finite values.")
        if data[column].isna().any():
            raise ValueError(f"{column} cannot be missing.")
    if not np.equal(data["Quantity"], np.floor(data["Quantity"])).all():
        raise ValueError("Quantity must contain whole-number values.")
    data["Quantity"] = data["Quantity"].astype("int64")

    customer_ids = pd.to_numeric(data["Customer ID"], errors="raise")
    valid_customer = customer_ids.notna()
    if not np.isfinite(customer_ids.loc[valid_customer].to_numpy(dtype=float)).all():
        raise ValueError("Customer ID must contain finite numeric values when present.")
    if not np.equal(
        customer_ids.loc[valid_customer],
        np.floor(customer_ids.loc[valid_customer]),
    ).all():
        raise ValueError("Customer ID values must be whole numbers.")
    data["Customer ID"] = customer_ids

    duplicate_mask = data.duplicated(keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    data = data.loc[~duplicate_mask].copy()
    missing_customer_rows = int(data["Customer ID"].isna().sum())
    data = data.loc[data["Customer ID"].notna()].copy()
    data["Customer ID"] = data["Customer ID"].astype("int64")
    data = data.reset_index(drop=True)

    report = {
        "input_rows": int(input_rows),
        "duplicate_rows_removed": duplicate_rows,
        "missing_customer_rows_removed": missing_customer_rows,
        "output_rows": int(len(data)),
        "retained_cancellation_rows": int(
            data["Invoice"].astype(str).str.startswith("C").sum()
        ),
        "retained_zero_price_rows": int(data["Price"].eq(0).sum()),
        "rules": [
            "Remove exact duplicate transaction rows, keeping the first copy.",
            "Exclude rows with missing Customer ID; do not impute customer identity.",
            "Retain customer-linked cancellations, zero prices, and extreme values.",
            "Do not remove records by arbitrary quantity, price, or revenue thresholds.",
        ],
    }
    return (data, report) if return_report else data


def validate_transaction_history(
    transactions: pd.DataFrame,
    cutoff_date: pd.Timestamp,
) -> pd.DataFrame:
    """Validate and clean an inference input while preserving future rows.

    Future rows are permitted in the supplied table so callers can reuse a
    larger transaction extract. The inference API must filter them out before
    feature construction; this helper does not turn them into targets.
    """
    cutoff = pd.Timestamp(cutoff_date)
    if pd.isna(cutoff):
        raise ValueError("cutoff_date must be a valid timestamp.")
    return clean_transactions(transactions)
