from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import MAX_UPLOAD_BYTES
from src.customer_features import build_customer_features
from src.data_preparation import TRANSACTION_COLUMNS, clean_transactions
from src.temporal_framework import build_order_level_dataset


def parse_uploaded_file(
    file_name: str,
    file_bytes: bytes,
    *,
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> pd.DataFrame:
    """Read a supported upload from memory; no file is written to disk."""
    if len(file_bytes) > max_bytes:
        raise ValueError(
            f"File is larger than the {max_bytes // (1024 * 1024)} MB upload limit."
        )
    suffix = Path(file_name).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(BytesIO(file_bytes))
    if suffix == ".xlsx":
        try:
            return pd.read_excel(BytesIO(file_bytes))
        except ImportError as exc:
            raise ValueError(
                "Excel support is unavailable. Export the workbook as CSV and retry."
            ) from exc
    raise ValueError("Upload a CSV file or an Excel workbook (.xlsx).")


def inspect_upload(frame: pd.DataFrame) -> dict[str, Any]:
    """Validate supported transaction columns and compute descriptive features only."""
    if frame.empty:
        raise ValueError("The uploaded file has no transaction rows.")

    missing_columns = [column for column in TRANSACTION_COLUMNS if column not in frame]
    if missing_columns:
        raise ValueError(
            "Required transaction columns are missing: "
            + ", ".join(missing_columns)
        )

    missing_values = frame.isna().sum().rename("missing_values").to_frame()
    cancellation_rows = int(
        frame["Invoice"].astype("string").str.startswith("C", na=False).sum()
    )
    duplicate_rows = int(frame.duplicated().sum())
    invalid_dates = int(
        (
            frame["InvoiceDate"].notna()
            & pd.to_datetime(
                frame["InvoiceDate"], errors="coerce", format="mixed"
            ).isna()
        ).sum()
    )
    if invalid_dates:
        raise ValueError(
            f"{invalid_dates:,} rows have invalid invoice dates. Correct them and retry."
        )

    cleaned, cleaning_report = clean_transactions(frame, return_report=True)
    if cleaned.empty:
        raise ValueError("No valid transaction rows remain after the standard cleaning.")

    latest_date = pd.Timestamp(cleaned["InvoiceDate"].max()).normalize()
    reference_date = latest_date + pd.Timedelta(days=1)
    features = build_customer_features(cleaned, reference_date=reference_date)
    orders = build_order_level_dataset(cleaned)
    summary = {
        "input_rows": int(len(frame)),
        "cleaned_rows": int(len(cleaned)),
        "excluded_rows": int(len(frame) - len(cleaned)),
        "customer_count": int(cleaned["Customer ID"].nunique()),
        "order_count": int(orders["Invoice"].nunique()),
        "cancellation_rows": cancellation_rows,
        "duplicate_rows": duplicate_rows,
        "invalid_date_rows": invalid_dates,
        "reference_date": reference_date,
        "cleaning_report": cleaning_report,
    }
    return {
        "cleaned_transactions": cleaned,
        "customer_features": features,
        "missing_values": missing_values,
        "summary": summary,
    }
