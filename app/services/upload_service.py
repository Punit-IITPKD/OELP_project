from __future__ import annotations

from collections.abc import Hashable, Mapping
from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import BadZipFile

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

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
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")
    suffix = Path(file_name).suffix.lower()
    if suffix == ".csv":
        try:
            return pd.read_csv(BytesIO(file_bytes))
        except (EmptyDataError, ParserError, UnicodeDecodeError) as exc:
            raise ValueError("Could not read this CSV file. Check its format and encoding.") from exc
    if suffix == ".xlsx":
        try:
            return pd.read_excel(BytesIO(file_bytes))
        except ImportError as exc:
            raise ValueError(
                "Excel support is unavailable. Export the workbook as CSV and retry."
            ) from exc
        except (BadZipFile, EOFError, OSError, ValueError) as exc:
            raise ValueError("Could not read this Excel workbook. Upload a valid .xlsx file.") from exc
    raise ValueError("Upload a CSV file or an Excel workbook (.xlsx).")


def validate_source_headers(frame: pd.DataFrame) -> None:
    """Reject headers that cannot be selected unambiguously in the mapping UI."""
    if not frame.columns.is_unique:
        duplicates = list(
            dict.fromkeys(frame.columns[frame.columns.duplicated()].tolist())
        )
        raise ValueError(
            "The uploaded file has duplicate source headers: "
            + ", ".join(repr(header) for header in duplicates)
            + ". Rename those columns and upload the file again."
        )

    display_headers = [str(header) for header in frame.columns]
    if any(header is None or not str(header).strip() for header in frame.columns):
        raise ValueError(
            "The uploaded file has a blank source header. Add a name to every column "
            "before mapping."
        )
    if len(set(display_headers)) != len(display_headers):
        raise ValueError(
            "Some source headers have the same displayed name and cannot be mapped "
            "unambiguously. Rename those columns and upload the file again."
        )


def map_transaction_columns(
    frame: pd.DataFrame,
    mapping: Mapping[str, Hashable | None],
) -> pd.DataFrame:
    """Rename selected upload headers into the fixed transaction schema."""
    validate_source_headers(frame)
    unexpected_targets = [
        target for target in mapping if target not in TRANSACTION_COLUMNS
    ]
    missing_targets = [
        target
        for target in TRANSACTION_COLUMNS
        if target not in mapping
        or mapping[target] is None
        or (isinstance(mapping[target], str) and not mapping[target].strip())
    ]
    invalid_sources = [
        (target, mapping[target])
        for target in TRANSACTION_COLUMNS
        if target in mapping
        and mapping[target] is not None
        and mapping[target] not in frame.columns
    ]

    targets_by_source: dict[Hashable, list[str]] = {}
    for target in TRANSACTION_COLUMNS:
        source = mapping.get(target)
        if source is not None and source in frame.columns:
            targets_by_source.setdefault(source, []).append(target)
    repeated_sources = {
        source: targets
        for source, targets in targets_by_source.items()
        if len(targets) > 1
    }

    errors = []
    if unexpected_targets:
        errors.append(
            "Unknown required fields: " + ", ".join(map(str, unexpected_targets)) + "."
        )
    if missing_targets:
        errors.append(
            "Choose a source column for: " + ", ".join(missing_targets) + "."
        )
    if invalid_sources:
        errors.append(
            "Selected source columns were not found: "
            + ", ".join(
                f"{target} ← {source!r}" for target, source in invalid_sources
            )
            + "."
        )
    if repeated_sources:
        errors.append(
            "A source column cannot be assigned to more than one required field: "
            + "; ".join(
                f"{source!r} → {', '.join(targets)}"
                for source, targets in repeated_sources.items()
            )
            + "."
        )
    if errors:
        raise ValueError(" ".join(errors))

    return pd.DataFrame(
        {target: frame[mapping[target]] for target in TRANSACTION_COLUMNS},
        index=frame.index,
    )


def build_revenue_trend(
    orders: pd.DataFrame,
    *,
    minimum_coverage_days: int = 14,
) -> tuple[pd.DataFrame | None, str | None, str | None]:
    """Aggregate positive-revenue orders at an honest weekly or monthly scale."""
    if orders.empty:
        return None, None, "No valid purchase orders are available for a revenue trend."
    positive = orders.loc[orders["GrossRevenue"].gt(0)].copy()
    if positive.empty:
        return None, None, "No positive gross purchase-order revenue is available."

    positive["PurchaseDate"] = pd.to_datetime(
        positive["PurchaseDate"], errors="coerce"
    )
    positive = positive.loc[positive["PurchaseDate"].notna()]
    if positive.empty:
        return None, None, "Valid purchase dates are unavailable for a revenue trend."
    coverage_days = (
        positive["PurchaseDate"].max().normalize()
        - positive["PurchaseDate"].min().normalize()
    ).days
    if coverage_days < minimum_coverage_days:
        return (
            None,
            None,
            f"At least {minimum_coverage_days} days of positive-order history are needed "
            "to show a weekly or monthly revenue trend.",
        )

    if coverage_days >= 90:
        positive["Period"] = positive["PurchaseDate"].dt.to_period("M").dt.to_timestamp()
        period_label = "Monthly"
    else:
        positive["Period"] = (
            positive["PurchaseDate"].dt.to_period("W-SUN").dt.start_time
        )
        period_label = "Weekly"
    trend = (
        positive.groupby("Period", as_index=False)
        .agg(
            GrossRevenue=("GrossRevenue", "sum"),
            Orders=("Invoice", "count"),
        )
        .sort_values("Period")
        .reset_index(drop=True)
    )
    return trend, period_label, None


def build_order_frequency_distribution(orders: pd.DataFrame) -> pd.DataFrame:
    """Count customers by invoice-level purchase frequency, not line-item rows."""
    labels = ["1 purchase", "2 purchases", "3 purchases", "4+ purchases"]
    if orders.empty:
        return pd.DataFrame({"Purchase frequency": labels, "Customers": [0, 0, 0, 0]})
    frequency = orders.groupby("Customer ID").size()
    bucket = frequency.map(
        lambda count: labels[count - 1] if count <= 3 else labels[3]
    )
    counts = bucket.value_counts().reindex(labels, fill_value=0)
    return pd.DataFrame(
        {"Purchase frequency": labels, "Customers": counts.to_numpy(dtype=int)}
    )


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

    orders = build_order_level_dataset(cleaned)
    if orders.empty:
        raise ValueError(
            "No valid purchase orders remain after excluding cancellation invoices "
            "and administrative test accounts."
        )

    latest_date = pd.Timestamp(cleaned["InvoiceDate"].max()).normalize()
    reference_date = latest_date + pd.Timedelta(days=1)
    features = build_customer_features(cleaned, reference_date=reference_date)
    positive_orders = orders.loc[orders["GrossRevenue"].gt(0)]
    summary = {
        "input_rows": int(len(frame)),
        "cleaned_rows": int(len(cleaned)),
        "excluded_rows": int(len(frame) - len(cleaned)),
        "customer_count": int(cleaned["Customer ID"].nunique()),
        "order_count": int(len(orders)),
        "positive_order_count": int(len(positive_orders)),
        "positive_gross_revenue": float(positive_orders["GrossRevenue"].sum()),
        "cancellation_rows": cancellation_rows,
        "duplicate_rows": duplicate_rows,
        "invalid_date_rows": invalid_dates,
        "reference_date": reference_date,
        "cleaning_report": cleaning_report,
    }
    return {
        "cleaned_transactions": cleaned,
        "customer_features": features,
        "orders": orders,
        "missing_values": missing_values,
        "summary": summary,
    }
