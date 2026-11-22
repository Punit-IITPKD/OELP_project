"""Read-only analytics data access backed by the saved project artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from app.config import (
    MAX_UPLOAD_BYTES,
    METRICS_DIR,
    PREDICTION_CUTOFF,
    PROCESSED_DIR,
    PROJECT_ROOT,
)
from app.services.upload_service import (
    build_order_frequency_distribution,
    build_revenue_trend,
    inspect_upload,
    map_transaction_columns,
    parse_uploaded_file,
    validate_source_headers,
)
from src.customer_intelligence import CustomerIntelligence
from src.forecast_application import build_forecast_snapshot

HORIZONS = (30, 60, 90)
CURVE_DAYS = tuple(range(10, 91, 10))
ALL_ELIGIBLE = "All eligible customers"
HISTORY_GROUPS = (
    "Exactly one purchase",
    "Two to four purchases",
    "Five or more purchases",
)


@dataclass(frozen=True)
class AnalyticsBundle:
    transactions: pd.DataFrame
    orders: pd.DataFrame
    features: pd.DataFrame
    segments: pd.DataFrame
    snapshot: pd.DataFrame
    performance: dict[str, Any]
    descriptive_segments: list[dict[str, Any]]
    historical_segments: list[dict[str, Any]]


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert pandas/numpy values and timestamps into JSON-native values."""
    if frame.empty:
        return []
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _number(value: Any) -> float:
    result = float(value)
    if not np.isfinite(result):
        return 0.0
    return result


def _describe_segments(segments: pd.DataFrame) -> list[dict[str, Any]]:
    grouped = (
        segments.groupby("Segment_Name", dropna=False)
        .agg(
            customers=("Customer ID", "nunique"),
            gross_spend=("Monetary_Gross", "sum"),
            median_recency=("Recency", "median"),
            median_frequency=("Frequency", "median"),
            median_gross_spend=("Monetary_Gross", "median"),
        )
        .reset_index()
        .rename(columns={"Segment_Name": "segment"})
    )
    total_customers = int(grouped["customers"].sum())
    total_revenue = float(grouped["gross_spend"].sum())
    grouped["customer_share"] = (
        grouped["customers"] / total_customers if total_customers else 0.0
    )
    grouped["revenue_share"] = (
        grouped["gross_spend"] / total_revenue if total_revenue else 0.0
    )
    grouped = grouped.rename(
        columns={
            "customers": "customers",
            "gross_spend": "gross_spend",
            "median_recency": "median_recency",
            "median_frequency": "median_frequency",
            "median_gross_spend": "median_gross_spend",
        }
    )
    return _records(grouped)


def _describe_historical_segments(snapshot: pd.DataFrame) -> list[dict[str, Any]]:
    counts = (
        snapshot.groupby("Hist_Segment", as_index=False)
        .agg(customers=("Customer ID", "nunique"))
        .rename(columns={"Hist_Segment": "segment"})
        .sort_values("customers", ascending=False)
    )
    return _records(counts)


@lru_cache(maxsize=1)
def get_analytics() -> AnalyticsBundle:
    """Load source tables and saved models once, then cache the aligned snapshot."""
    transactions_path = PROCESSED_DIR / "online_retail_cleaned_data.csv"
    orders_path = PROCESSED_DIR / "temporal" / "orders.csv"
    features_path = PROCESSED_DIR / "customer_features.csv"
    segments_path = PROCESSED_DIR / "customer_segments.csv"
    metrics_path = METRICS_DIR / "notebook_evaluation_summary.json"
    required_paths = (
        transactions_path,
        orders_path,
        features_path,
        segments_path,
        metrics_path,
    )
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Required saved customer-intelligence data is unavailable: "
            + ", ".join(missing)
        )

    transactions = pd.read_csv(transactions_path, parse_dates=["InvoiceDate"])
    orders = pd.read_csv(orders_path, parse_dates=["PurchaseDate"])
    features = pd.read_csv(features_path)
    segments = pd.read_csv(segments_path)
    for frame in (features, segments):
        frame["Customer ID"] = pd.to_numeric(
            frame["Customer ID"], errors="raise"
        ).astype("int64")

    intelligence = CustomerIntelligence.from_artifacts(PROJECT_ROOT)
    snapshot = build_forecast_snapshot(
        transactions,
        orders,
        segments,
        intelligence,
        PREDICTION_CUTOFF,
    )
    with metrics_path.open(encoding="utf-8") as stream:
        performance = json.load(stream)

    return AnalyticsBundle(
        transactions=transactions,
        orders=orders,
        features=features,
        segments=segments,
        snapshot=snapshot,
        performance=performance,
        descriptive_segments=_describe_segments(segments),
        historical_segments=_describe_historical_segments(snapshot),
    )


def get_overview(
    start_date: pd.Timestamp | None = None,
    end_date: pd.Timestamp | None = None,
) -> dict[str, Any]:
    bundle = get_analytics()
    orders = bundle.orders
    minimum = pd.Timestamp(orders["PurchaseDate"].min()).normalize()
    maximum = pd.Timestamp(orders["PurchaseDate"].max()).normalize()
    start = pd.Timestamp(start_date).normalize() if start_date else minimum
    end = pd.Timestamp(end_date).normalize() if end_date else maximum
    if start > end:
        raise ValueError("start_date must be on or before end_date.")
    if start < minimum or end > maximum:
        raise ValueError(
            f"Choose dates between {minimum.date()} and {maximum.date()}."
        )

    in_period = orders.loc[
        orders["PurchaseDate"].between(
            start,
            end + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1),
        )
    ].copy()
    order_count = int(len(in_period))
    revenue = float(in_period["GrossRevenue"].sum())
    monthly = (
        in_period.assign(
            Month=in_period["PurchaseDate"].dt.to_period("M").dt.to_timestamp()
        )
        .groupby("Month", as_index=False)
        .agg(revenue=("GrossRevenue", "sum"), orders=("Invoice", "nunique"))
        .rename(columns={"Month": "month"})
        .sort_values("month")
    )
    all_forecasts = bundle.snapshot
    forecast = {
        "cutoff_date": PREDICTION_CUTOFF,
        "hist_segment": ALL_ELIGIBLE,
        "eligible_customers": int(all_forecasts["Customer ID"].nunique()),
    }
    for horizon in HORIZONS:
        forecast[f"expected_returners_{horizon}d"] = float(
            all_forecasts[f"purchase_probability_{horizon}d"].sum()
        )
        forecast[f"expected_revenue_{horizon}d"] = float(
            all_forecasts[f"personalized_expected_revenue_{horizon}d"].sum()
        )

    return {
        "period": {"start_date": start.date(), "end_date": end.date()},
        "historical": {
            "customers": int(in_period["Customer ID"].nunique()),
            "orders": order_count,
            "revenue": revenue,
            "average_order_value": revenue / order_count if order_count else 0.0,
        },
        "monthly_trend": _records(monthly),
        "descriptive_segments": bundle.descriptive_segments,
        "forecast": forecast,
    }


def get_segments() -> dict[str, Any]:
    bundle = get_analytics()
    return {
        "descriptive_segments": bundle.descriptive_segments,
        "historical_segments": bundle.historical_segments,
    }


def get_customers(
    *,
    page: int = 1,
    page_size: int = 25,
    search: str | None = None,
    descriptive_segment: str | None = None,
    hist_segment: str | None = None,
) -> dict[str, Any]:
    bundle = get_analytics()
    forecast_columns = bundle.snapshot[
        ["Customer ID", "Hist_Segment", "history_group"]
    ]
    table = bundle.segments.merge(
        forecast_columns,
        how="left",
        on="Customer ID",
        validate="one_to_one",
    )
    if search and search.strip():
        table = table.loc[
            table["Customer ID"]
            .astype("string")
            .str.contains(search.strip(), regex=False, na=False)
        ]
    if descriptive_segment:
        table = table.loc[table["Segment_Name"].eq(descriptive_segment)]
    if hist_segment:
        table = table.loc[table["Hist_Segment"].eq(hist_segment)]

    total = int(len(table))
    table = table.sort_values(
        ["Monetary_Gross", "Customer ID"], ascending=[False, True]
    )
    start = (page - 1) * page_size
    result = table.iloc[start : start + page_size].rename(
        columns={
            "Customer ID": "customer_id",
            "Segment_Name": "descriptive_segment",
            "Hist_Segment": "hist_segment",
            "history_group": "history_group",
            "Recency": "recency",
            "Frequency": "frequency",
            "Monetary_Gross": "monetary_gross",
            "Monetary_Net": "monetary_net",
            "AOV": "average_order_value",
            "At_Risk_Flag": "at_risk_flag",
        }
    )
    return {
        "items": _records(
            result[
                [
                    "customer_id",
                    "descriptive_segment",
                    "hist_segment",
                    "history_group",
                    "recency",
                    "frequency",
                    "monetary_gross",
                    "monetary_net",
                    "average_order_value",
                    "at_risk_flag",
                ]
            ]
        ),
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def _snapshot_record(customer_id: int) -> pd.Series:
    bundle = get_analytics()
    match = bundle.snapshot.loc[bundle.snapshot["Customer ID"].eq(customer_id)]
    if match.empty:
        raise KeyError(customer_id)
    return match.iloc[0]


def _forecast_payload(row: pd.Series) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "customer_id": int(row["Customer ID"]),
        "cutoff_date": pd.Timestamp(row["cutoff_date"]).date(),
        "hist_segment": str(row["Hist_Segment"]),
        "history_group": str(row["history_group"]),
        "first_purchase_date": pd.Timestamp(row["FirstPurchaseDate"]),
        "last_purchase_date": pd.Timestamp(row["LastPurchaseDate"]),
        "recency": _number(row["Recency"]),
        "frequency": _number(row["Frequency"]),
        "monetary_gross": _number(row["Monetary_Gross"]),
        "n_historical_gaps": int(row["n_historical_gaps"]),
        "regularized_expected_gap_days": _number(
            row["regularized_expected_gap_days"]
        ),
        "delay_ratio": _number(row["delay_ratio"]),
        "cumulative_curve": [
            {"day": day, "probability": _number(row[f"personalized_purchase_{day}d"])}
            for day in CURVE_DAYS
        ],
    }
    for horizon in HORIZONS:
        for prefix, column_prefix in (
            ("global", "global_purchase_probability"),
            ("segment", "segment_purchase_probability"),
            ("", "purchase_probability"),
        ):
            if prefix:
                key = f"{prefix}_purchase_probability_{horizon}d"
            else:
                key = f"purchase_probability_{horizon}d"
            payload[key] = _number(row[f"{column_prefix}_{horizon}d"])
        payload[f"personalized_expected_revenue_{horizon}d"] = _number(
            row[f"personalized_expected_revenue_{horizon}d"]
        )
    return payload


def get_customer_profile(customer_id: int) -> dict[str, Any]:
    bundle = get_analytics()
    row = _snapshot_record(customer_id)
    descriptive = bundle.segments.loc[
        bundle.segments["Customer ID"].eq(customer_id)
    ]
    if descriptive.empty:
        raise KeyError(customer_id)
    segment = descriptive.iloc[0]
    payload = _forecast_payload(row)
    payload.update(
        {
            "descriptive_segment": str(segment["Segment_Name"]),
            "monetary_net": _number(segment["Monetary_Net"]),
            "average_order_value": _number(segment["AOV"]),
            "at_risk_flag": bool(segment["At_Risk_Flag"]),
        }
    )
    return payload


def get_customer_history(customer_id: int) -> list[dict[str, Any]]:
    bundle = get_analytics()
    row = _snapshot_record(customer_id)
    cutoff = pd.Timestamp(row["cutoff_date"])
    history = bundle.orders.loc[
        bundle.orders["Customer ID"].eq(customer_id)
        & bundle.orders["PurchaseDate"].lt(cutoff)
    ].sort_values("PurchaseDate")
    history = history.rename(
        columns={
            "Invoice": "invoice",
            "PurchaseDate": "purchase_date",
            "GrossRevenue": "gross_revenue",
        }
    )
    records = _records(history[["invoice", "purchase_date", "gross_revenue"]])
    return [{**record, "invoice": str(record["invoice"])} for record in records]


def get_forecast_summary(
    hist_segment: str | None = None,
    history_group: str | None = None,
) -> dict[str, Any]:
    bundle = get_analytics()
    cohort = bundle.snapshot
    if hist_segment:
        cohort = cohort.loc[cohort["Hist_Segment"].eq(hist_segment)]
    if history_group:
        cohort = cohort.loc[cohort["history_group"].eq(history_group)]

    horizons = []
    for days in HORIZONS:
        horizons.append(
            {
                "days": days,
                "global_probability": _number(
                    cohort[f"global_purchase_probability_{days}d"].mean()
                )
                if len(cohort)
                else 0.0,
                "segment_probability": _number(
                    cohort[f"segment_purchase_probability_{days}d"].mean()
                )
                if len(cohort)
                else 0.0,
                "personalized_probability": _number(
                    cohort[f"purchase_probability_{days}d"].mean()
                )
                if len(cohort)
                else 0.0,
                "historical_rate_expected_revenue": _number(
                    cohort[f"historical_rate_expected_revenue_{days}d"].sum()
                ),
                "segment_expected_revenue": _number(
                    cohort[f"segment_expected_revenue_{days}d"].sum()
                ),
                "personalized_expected_revenue": _number(
                    cohort[f"personalized_expected_revenue_{days}d"].sum()
                ),
            }
        )
    curve = [
        {
            "day": day,
            "probability": _number(cohort[f"personalized_purchase_{day}d"].mean())
            if len(cohort)
            else 0.0,
        }
        for day in CURVE_DAYS
    ]
    return {
        "cutoff_date": PREDICTION_CUTOFF,
        "hist_segment": hist_segment,
        "history_group": history_group,
        "eligible_customers": int(cohort["Customer ID"].nunique()),
        "expected_returners_30d": _number(
            cohort["purchase_probability_30d"].sum()
        ),
        "expected_returners_60d": _number(
            cohort["purchase_probability_60d"].sum()
        ),
        "expected_returners_90d": _number(
            cohort["purchase_probability_90d"].sum()
        ),
        "horizons": horizons,
        "cumulative_curve": curve,
    }


def get_model_performance() -> dict[str, Any]:
    bundle = get_analytics()
    purchase = bundle.performance["purchase_clock"]
    spending = bundle.performance["spending_forecast"]
    test_customers = int(purchase["test_metrics"][0]["n_customers"])
    return {
        "cutoff_date": PREDICTION_CUTOFF,
        "test_customers": test_customers,
        "purchase_metrics": purchase["test_metrics"],
        "purchase_history_metrics": purchase["history_group_metrics"],
        "revenue_metrics": spending["test_metrics"],
        "revenue_group_metrics": spending["group_metrics"],
        "calibration_image_url": (
            "/api/model-performance/assets/purchase_clock_test_calibration.png"
        ),
        "calibration_90d_image_url": (
            "/api/model-performance/assets/purchase_clock_test_calibration_90d.png"
        ),
    }


def get_calibration_asset(*, ninety_day: bool = False) -> Path:
    filename = (
        "purchase_clock_test_calibration_90d.png"
        if ninety_day
        else "purchase_clock_test_calibration.png"
    )
    path = METRICS_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Saved calibration image is unavailable: {filename}")
    return path


def parse_upload(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    return parse_uploaded_file(file_name, file_bytes, max_bytes=MAX_UPLOAD_BYTES)


def inspect_upload_with_mapping(
    frame: pd.DataFrame,
    mapping: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    validate_source_headers(frame)
    mapped = map_transaction_columns(frame, mapping)
    return mapped, inspect_upload(mapped)


def analyze_upload(
    file_name: str,
    file_bytes: bytes,
    mapping: dict[str, Any],
) -> dict[str, Any]:
    raw = parse_upload(file_name, file_bytes)
    mapped, result = inspect_upload_with_mapping(raw, mapping)
    summary = result["summary"]
    report = summary["cleaning_report"]
    features = result["customer_features"]
    orders = result["orders"]
    trend, trend_period, trend_message = build_revenue_trend(orders)

    distributions = []
    for field, label, positive_only in (
        ("Recency", "Recency (days)", False),
        ("Frequency", "Purchase frequency", False),
        ("Monetary_Gross", "Gross spend", True),
        ("AOV", "Average order value", True),
    ):
        values = pd.to_numeric(features[field], errors="coerce").dropna()
        if positive_only:
            values = values.loc[values.gt(0)]
        if values.empty:
            bins = []
        else:
            array = values.to_numpy(dtype=float)
            if positive_only:
                edges = np.geomspace(max(float(array.min()), 1e-6), float(array.max()), 16)
                if np.unique(edges).size < 2:
                    edges = np.array([float(array.min()), float(array.max()) + 1.0])
            else:
                edges = np.histogram_bin_edges(array, bins=min(15, max(1, len(np.unique(array)))))
                if np.unique(edges).size < 2:
                    edges = np.array([float(array.min()), float(array.max()) + 1.0])
            counts, edges = np.histogram(array, bins=edges)
            bins = [
                {
                    "lower": float(edges[index]),
                    "upper": float(edges[index + 1]),
                    "customers": int(counts[index]),
                }
                for index in range(len(counts))
            ]
        distributions.append({"field": field, "label": label, "bins": bins})

    trend_rows = (
        [
            {
                "period": pd.Timestamp(row["Period"]).date(),
                "revenue": float(row["GrossRevenue"]),
                "orders": int(row["Orders"]),
            }
            for row in trend.to_dict(orient="records")
        ]
        if trend is not None
        else []
    )
    missing_values = [
        {"column": str(column), "missing_count": int(count)}
        for column, count in mapped.isna().sum().items()
    ]
    summary_payload = {
        key: summary[key]
        for key in (
            "input_rows",
            "cleaned_rows",
            "excluded_rows",
            "customer_count",
            "order_count",
            "positive_order_count",
            "positive_gross_revenue",
            "cancellation_rows",
            "duplicate_rows",
            "reference_date",
        )
    }
    summary_payload.update(
        {
            "duplicate_rows_removed": int(report["duplicate_rows_removed"]),
            "missing_customer_rows_removed": int(
                report["missing_customer_rows_removed"]
            ),
            "retained_cancellation_rows": int(
                report["retained_cancellation_rows"]
            ),
            "retained_zero_price_rows": int(report["retained_zero_price_rows"]),
        }
    )
    features_preview = features.head(50).copy()
    return {
        "file_name": file_name,
        "summary": summary_payload,
        "missing_values": missing_values,
        "order_frequency": [
            {"label": str(row["Purchase frequency"]), "customers": int(row["Customers"])}
            for row in build_order_frequency_distribution(orders).to_dict(
                orient="records"
            )
        ],
        "revenue_trend": trend_rows,
        "trend_period": trend_period,
        "trend_message": trend_message,
        "rfm_distributions": distributions,
        "customer_features_preview": _records(features_preview),
    }


def export_upload(
    file_name: str,
    file_bytes: bytes,
    mapping: dict[str, Any],
    kind: str,
) -> tuple[str, str]:
    raw = parse_upload(file_name, file_bytes)
    _, result = inspect_upload_with_mapping(raw, mapping)
    if kind == "cleaned_transactions":
        frame = result["cleaned_transactions"]
        download_name = "cleaned_transactions.csv"
    elif kind == "customer_features":
        frame = result["customer_features"]
        download_name = "customer_features.csv"
    else:
        raise ValueError("kind must be cleaned_transactions or customer_features.")
    return frame.to_csv(index=False), download_name
