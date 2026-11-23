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
from src.behavior_monitor import (
    BehaviorConfig,
    POLICY_VERSION,
    behavior_config_metadata,
    build_behavior_trajectory,
    calculate_behavior_scores,
    compute_behavior_features,
    prepare_purchase_events,
)

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


@dataclass(frozen=True)
class BehaviorAnalyticsBundle:
    events: pd.DataFrame
    snapshot: pd.DataFrame
    config: BehaviorConfig


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


def _retrospective_source_period(bundle: AnalyticsBundle) -> dict[str, Any]:
    purchase_dates = pd.to_datetime(bundle.orders["PurchaseDate"], errors="raise")
    return {
        "start_date": pd.Timestamp(purchase_dates.min()).date(),
        "end_date": pd.Timestamp(purchase_dates.max()).date(),
    }


def _retrospective_description(
    bundle: AnalyticsBundle,
    segment: pd.Series,
    source_period: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "source_period": source_period or _retrospective_source_period(bundle),
        "descriptive_segment": str(segment["Segment_Name"]),
        "monetary_net": _number(segment["Monetary_Net"]),
        "average_order_value": _number(segment["AOV"]),
        "at_risk_flag": bool(segment["At_Risk_Flag"]),
    }


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
    retrospective_segment: str | None = None,
    hist_segment: str | None = None,
    history_group: str | None = None,
) -> dict[str, Any]:
    bundle = get_analytics()
    forecast_columns = bundle.snapshot[
        [
            "Customer ID",
            "Hist_Segment",
            "history_group",
            "Recency",
            "Frequency",
            "Monetary_Gross",
        ]
    ]
    retrospective_columns = bundle.segments[
        [
            "Customer ID",
            "Segment_Name",
            "Monetary_Net",
            "AOV",
            "At_Risk_Flag",
        ]
    ]
    table = forecast_columns.merge(
        retrospective_columns,
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
    if retrospective_segment:
        table = table.loc[table["Segment_Name"].eq(retrospective_segment)]
    if hist_segment:
        table = table.loc[table["Hist_Segment"].eq(hist_segment)]
    if history_group:
        table = table.loc[table["history_group"].eq(history_group)]

    total = int(len(table))
    table = table.sort_values(
        ["Monetary_Gross", "Customer ID"], ascending=[False, True]
    )
    start = (page - 1) * page_size
    result = table.iloc[start : start + page_size]
    items = _records(
        result[
            [
                "Customer ID",
                "Hist_Segment",
                "history_group",
                "Recency",
                "Frequency",
                "Monetary_Gross",
            ]
        ].rename(
            columns={
                "Customer ID": "customer_id",
                "Hist_Segment": "hist_segment",
                "Recency": "recency",
                "Frequency": "frequency",
                "Monetary_Gross": "monetary_gross",
            }
        )
    )
    source_period = _retrospective_source_period(bundle)
    for item, (_, row) in zip(items, result.iterrows(), strict=True):
        item["retrospective_description"] = _retrospective_description(
            bundle, row, source_period
        )
    return {
        "items": items,
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
            "retrospective_description": _retrospective_description(
                bundle, segment
            ),
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


@lru_cache(maxsize=1)
def _get_behavior_config() -> BehaviorConfig:
    path = PROJECT_ROOT / "models" / "behavior_monitor" / "metadata.json"
    if not path.is_file():
        raise FileNotFoundError(
            "Saved behavior-monitor metadata is unavailable; run Notebook 08 first."
        )
    with path.open(encoding="utf-8") as stream:
        metadata = json.load(stream)
    if metadata.get("feature_version") != "behavior-monitor-v1":
        raise ValueError("Saved behavior-monitor metadata has an unsupported feature version.")
    if metadata.get("policy_version") != POLICY_VERSION:
        raise ValueError("Saved behavior-monitor metadata has an unsupported policy version.")
    if metadata.get("alert_policy_available") is not False:
        raise ValueError("No validated categorical behavior alert policy is available.")
    return BehaviorConfig(**metadata["config"])


@lru_cache(maxsize=1)
def _get_behavior_analytics() -> BehaviorAnalyticsBundle:
    """Compute the fixed historical behavior snapshot once per process."""
    analytics = get_analytics()
    config = _get_behavior_config()
    events = prepare_purchase_events(analytics.orders)
    features = compute_behavior_features(events, PREDICTION_CUTOFF, config)
    scores = calculate_behavior_scores(
        features,
        {
            "feature_version": "behavior-monitor-v1",
            "policy_version": POLICY_VERSION,
            "ewma_lambda": config.ewma_lambda,
        },
    )
    model_fields = analytics.snapshot.loc[
        :,
        [
            "Customer ID",
            "cutoff_date",
            "Hist_Segment",
            "history_group",
            "Recency",
            "Frequency",
            "delay_ratio",
            "purchase_probability_30d",
            "purchase_probability_60d",
            "purchase_probability_90d",
        ],
    ]
    snapshot = features.merge(
        scores.drop(columns=["cutoff_date", "history_sufficiency"]),
        on="Customer ID",
        how="left",
        validate="one_to_one",
    ).merge(
        model_fields,
        on=["Customer ID", "cutoff_date"],
        how="inner",
        validate="one_to_one",
    )
    if len(snapshot) != len(features) or snapshot["Customer ID"].duplicated().any():
        raise AssertionError("Behavior and forecast-time customer cohorts do not align.")
    snapshot["cutoff_date"] = pd.to_datetime(snapshot["cutoff_date"])
    return BehaviorAnalyticsBundle(events=events, snapshot=snapshot, config=config)


def _nullable_number(value: Any) -> float | None:
    if pd.isna(value):
        return None
    result = float(value)
    return result if np.isfinite(result) else None


def _behavior_payload(row: pd.Series, *, detail: bool = False) -> dict[str, Any]:
    mapping = {
        "customer_id": ("Customer ID", int),
        "cutoff_date": ("cutoff_date", lambda value: pd.Timestamp(value).date()),
        "first_purchase_date": (
            "first_purchase_date",
            lambda value: pd.Timestamp(value).to_pydatetime(),
        ),
        "last_purchase_date": (
            "last_purchase_date",
            lambda value: pd.Timestamp(value).to_pydatetime(),
        ),
        "hist_segment": ("Hist_Segment", lambda value: None if pd.isna(value) else str(value)),
        "history_group": ("history_group", lambda value: None if pd.isna(value) else str(value)),
        "recency": ("Recency", _number),
        "frequency": ("Frequency", _number),
        "historical_order_count": ("historical_order_count", int),
        "completed_gap_count": ("completed_gap_count", int),
        "current_elapsed_gap_days": ("current_elapsed_gap_days", _number),
        "median_completed_gap_days": ("median_completed_gap_days", _nullable_number),
        "mean_completed_gap_days": ("mean_completed_gap_days", _nullable_number),
        "mad_completed_gap_days": ("mad_completed_gap_days", _nullable_number),
        "gap_deviation_score": ("gap_deviation_score", _nullable_number),
        "gap_deviation_method": ("gap_deviation_method", str),
        "recent_order_count": ("recent_order_count", int),
        "reference_order_count": ("reference_order_count", int),
        "recent_observed_days": ("recent_observed_days", _number),
        "reference_observed_days": ("reference_observed_days", _number),
        "recent_order_rate": ("recent_order_rate", _number),
        "reference_order_rate": ("reference_order_rate", _nullable_number),
        "purchase_rate_ratio": ("purchase_rate_ratio", _nullable_number),
        "purchase_rate_change": ("purchase_rate_change", _nullable_number),
        "raw_purchase_rate_ratio": ("raw_purchase_rate_ratio", _nullable_number),
        "recent_gross_revenue": ("recent_gross_revenue", _number),
        "reference_gross_revenue": ("reference_gross_revenue", _number),
        "recent_revenue_rate": ("recent_revenue_rate", _nullable_number),
        "reference_revenue_rate": ("reference_revenue_rate", _nullable_number),
        "revenue_rate_ratio": ("revenue_rate_ratio", _nullable_number),
        "revenue_rate_change": ("revenue_rate_change_per_day", _nullable_number),
        "recent_ewma_gap_days": ("recent_ewma_gap_days", _nullable_number),
        "reference_ewma_gap_days": ("reference_ewma_gap_days", _nullable_number),
        "ewma_gap_change_days": ("ewma_gap_change_days", _nullable_number),
        "ewma_gap_observation_count": ("ewma_gap_observation_count", int),
        "history_sufficiency": ("history_sufficiency", str),
        "personalized_delay_ratio": ("delay_ratio", _number),
        "purchase_probability_30d": ("purchase_probability_30d", _number),
        "purchase_probability_60d": ("purchase_probability_60d", _number),
        "purchase_probability_90d": ("purchase_probability_90d", _number),
        "available_indicator_count": ("available_indicator_count", int),
        "policy_version": ("policy_version", str),
        "policy_status": ("policy_status", str),
    }
    payload = {
        key: convert(row[column])
        for key, (column, convert) in mapping.items()
    }
    if detail:
        payload["alert_reasons"] = []
        explanations = []
        if pd.notna(row["gap_deviation_score"]):
            explanations.append(
                "Personal gap deviation is available using the median/MAD method; it is descriptive, not an alert."
            )
        else:
            explanations.append(
                f"Personal gap deviation is unavailable with {int(row['completed_gap_count'])} completed gaps."
            )
        if pd.notna(row["purchase_rate_ratio"]):
            explanations.append(
                "Purchase-rate ratio compares smoothed recent and reference rates with observed exposure."
            )
        else:
            explanations.append(
                "Purchase-rate comparison is unavailable because the observed reference period is too short."
            )
        if pd.notna(row["revenue_rate_ratio"]):
            explanations.append(
                "Revenue-rate ratio is available because reference revenue is positive and sufficiently observed."
            )
        else:
            explanations.append(
                "Revenue-rate ratio is unavailable because reference revenue is zero or insufficiently observed."
            )
        if pd.notna(row["ewma_gap_change_days"]):
            explanations.append(
                "EWMA gap change is shown only when both reference and recent periods have enough completed gaps."
            )
        payload["indicator_explanations"] = explanations
    return payload


def get_behavior_summary() -> dict[str, Any]:
    data = _get_behavior_analytics()
    snapshot = data.snapshot
    config = data.config
    history_counts = (
        snapshot["history_sufficiency"]
        .value_counts()
        .reindex(["sufficient", "limited", "insufficient"], fill_value=0)
    )
    distributions = []
    definitions = (
        ("current_elapsed_gap_days", "Current elapsed purchase gap"),
        ("gap_deviation_score", "Personal gap deviation (median/MAD)"),
        ("purchase_rate_ratio", "Smoothed purchase-rate ratio"),
        ("revenue_rate_ratio", "Observed revenue-rate ratio"),
        ("ewma_gap_change_days", "Recent versus reference EWMA gap"),
    )
    for field, label in definitions:
        values = pd.to_numeric(snapshot[field], errors="coerce").dropna()
        bins: list[dict[str, Any]] = []
        if not values.empty:
            bin_count = min(12, max(4, int(np.ceil(np.sqrt(len(values))))))
            counts, edges = np.histogram(values.to_numpy(dtype=float), bins=bin_count)
            for index, count in enumerate(counts):
                bins.append(
                    {
                        "label": f"{edges[index]:.2f}–{edges[index + 1]:.2f}",
                        "lower_bound": float(edges[index]),
                        "upper_bound": float(edges[index + 1]),
                        "customers": int(count),
                    }
                )
        distributions.append(
            {
                "field": field,
                "label": label,
                "available_customers": int(values.size),
                "median": _nullable_number(values.median()) if len(values) else None,
                "percentile_75": (
                    _nullable_number(values.quantile(0.75)) if len(values) else None
                ),
                "percentile_90": (
                    _nullable_number(values.quantile(0.90)) if len(values) else None
                ),
                "bins": bins,
            }
        )
    metadata = behavior_config_metadata(config)
    return {
        "cutoff_date": pd.Timestamp(PREDICTION_CUTOFF).date(),
        "eligible_customers": int(snapshot["Customer ID"].nunique()),
        "policy_version": metadata["policy_version"],
        "policy_status": metadata["policy_status"],
        "alert_policy_available": False,
        "history_sufficiency": [
            {"history_sufficiency": key, "customers": int(value)}
            for key, value in history_counts.items()
        ],
        "distributions": distributions,
    }


def get_behavior_customers(
    *,
    page: int = 1,
    page_size: int = 25,
    search: str | None = None,
    hist_segment: str | None = None,
    history_group: str | None = None,
    history_sufficiency: str | None = None,
    sort_by: str = "current_elapsed_gap_days",
    sort_direction: str = "desc",
) -> dict[str, Any]:
    snapshot = _get_behavior_analytics().snapshot
    allowed_sorts = {
        "current_elapsed_gap_days",
        "gap_deviation_score",
        "purchase_rate_ratio",
        "revenue_rate_ratio",
        "personalized_delay_ratio",
        "recency",
    }
    if sort_by not in allowed_sorts:
        raise ValueError(f"Unsupported behavior sort field: {sort_by}")
    if sort_direction not in {"asc", "desc"}:
        raise ValueError("sort_direction must be 'asc' or 'desc'.")
    if page < 1 or not 1 <= page_size <= 100:
        raise ValueError("page must be positive and page_size must be between 1 and 100.")
    filtered = snapshot
    if search:
        filtered = filtered.loc[
            filtered["Customer ID"].astype(str).str.contains(search.strip(), regex=False)
        ]
    if hist_segment:
        filtered = filtered.loc[filtered["Hist_Segment"].eq(hist_segment)]
    if history_group:
        filtered = filtered.loc[filtered["history_group"].eq(history_group)]
    if history_sufficiency:
        filtered = filtered.loc[
            filtered["history_sufficiency"].eq(history_sufficiency)
        ]
    total = int(len(filtered))
    sort_column = {
        "personalized_delay_ratio": "delay_ratio",
        "recency": "Recency",
    }.get(sort_by, sort_by)
    ordered = filtered.sort_values(
        [sort_column, "Customer ID"],
        ascending=[sort_direction == "asc", True],
        na_position="last",
        kind="mergesort",
    )
    start = (page - 1) * page_size
    records = [
        _behavior_payload(pd.Series(record))
        for record in ordered.iloc[start : start + page_size].to_dict(
            orient="records"
        )
    ]
    return {"items": records, "total": total, "page": page, "page_size": page_size}


def get_customer_behavior(customer_id: int) -> dict[str, Any]:
    snapshot = _get_behavior_analytics().snapshot
    match = snapshot.loc[snapshot["Customer ID"].eq(customer_id)]
    if match.empty:
        raise KeyError(customer_id)
    return _behavior_payload(match.iloc[0], detail=True)


def get_customer_behavior_trajectory(
    customer_id: int,
    *,
    window_days: int = 30,
) -> dict[str, Any]:
    data = _get_behavior_analytics()
    match = data.snapshot.loc[data.snapshot["Customer ID"].eq(customer_id)]
    if match.empty:
        raise KeyError(customer_id)
    row = match.iloc[0]
    trajectory = build_behavior_trajectory(
        data.events,
        customer_id,
        row["cutoff_date"],
        window_days=window_days,
    )
    return {
        "customer_id": int(customer_id),
        "cutoff_date": pd.Timestamp(row["cutoff_date"]).date(),
        "window_days": int(window_days),
        "policy_version": POLICY_VERSION,
        "items": [
            {
                "period_start": item["period_start"],
                "period_end": item["period_end"],
                "order_count": int(item["order_count"]),
                "gross_revenue": _number(item["gross_revenue"]),
                "observed_exposure_days": _number(item["observed_exposure_days"]),
                "order_rate": _number(item["order_rate_per_day"]),
                "revenue_rate": _number(item["revenue_rate_per_day"]),
            }
            for item in trajectory.to_dict(orient="records")
        ],
    }


def get_behavior_evaluation() -> dict[str, Any]:
    path = METRICS_DIR / "behavior_monitor_evaluation.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Saved behavior evaluation is unavailable: {path}"
        )
    with path.open(encoding="utf-8") as stream:
        result = json.load(stream)
    if result.get("feature_version") != "behavior-monitor-v1":
        raise ValueError("Saved behavior evaluation uses an unsupported feature version.")
    if result.get("policy_version") != POLICY_VERSION:
        raise ValueError("Saved behavior evaluation uses an unsupported policy version.")
    return result


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
