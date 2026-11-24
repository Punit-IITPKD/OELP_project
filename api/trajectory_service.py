"""Cached, inference-only access to Notebook 11 trajectory outputs."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from app.config import METRICS_DIR, PROCESSED_DIR, PROJECT_ROOT
from src.customer_trajectories import (
    CUSTOMER_ID,
    TrajectoryConfig,
    build_customer_trajectory_matrix,
    calculate_trajectory_features,
)
from src.functional_trajectory_analysis import transform_functional_representation
from src.trajectory_clustering import assign_trajectory_clusters
from src.trajectory_clustering import (
    TrajectoryClusteringConfig,
    build_shape_trajectory_features,
    prepare_trajectory_features,
)
from src.trajectory_research import build_trajectory_curve_table

CUTOFF_DATE = pd.Timestamp("2010-09-10")
MODEL_VERSION = "customer-trajectory-analysis-v2"
_MODEL_DIR = PROJECT_ROOT / "models" / "trajectory_analysis"


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path.name}.")
    return value


@lru_cache(maxsize=1)
def _get_trajectory_bundle() -> dict[str, Any]:
    """Load canonical data and frozen models; never fit a model in the API."""
    orders_path = PROCESSED_DIR / "temporal" / "orders.csv"
    if not orders_path.is_file():
        raise FileNotFoundError("Canonical historical order data is unavailable.")
    events = pd.read_csv(orders_path, parse_dates=["PurchaseDate"])
    config = TrajectoryConfig()
    matrix = build_customer_trajectory_matrix(
        events,
        CUTOFF_DATE,
        window_days=config.window_days,
        lookback_days=config.lookback_days,
    )
    features = calculate_trajectory_features(matrix, config)
    shape_features = build_shape_trajectory_features(matrix)
    shape_support = shape_features[
        [CUSTOMER_ID, "cluster_eligible", "shape_transform_status"]
    ].rename(
        columns={
            "cluster_eligible": "shape_cluster_eligible",
            "shape_transform_status": "shape_cluster_eligibility_status",
        }
    )
    features = features.merge(
        shape_support,
        on=CUSTOMER_ID,
        how="left",
        validate="one_to_one",
    )
    split_path = PROCESSED_DIR / "temporal" / "predictive_splits_30d.csv"
    historical_segments = pd.DataFrame(columns=[CUSTOMER_ID, "Hist_Segment", "Recency"])
    if split_path.is_file():
        splits = pd.read_csv(split_path, parse_dates=["cutoff_date"])
        test = splits.loc[splits["split_role"].eq("TEST")]
        available = [
            column for column in (CUSTOMER_ID, "Hist_Segment", "Recency")
            if column in test
        ]
        if CUSTOMER_ID in available:
            historical_segments = test[available].drop_duplicates(CUSTOMER_ID)
    features = features.merge(
        historical_segments,
        on=CUSTOMER_ID,
        how="left",
        validate="one_to_one",
    )
    assignments = pd.DataFrame(
        {
            CUSTOMER_ID: features[CUSTOMER_ID],
            "trajectory_cluster_id": pd.array(
                [pd.NA] * len(features), dtype="Int64"
            ),
            "cluster_assignment_status": "model_not_available",
            "distance_to_cluster_center": np.nan,
        }
    )
    curves = build_trajectory_curve_table(matrix, features, rate_column="purchase_rate_per_observed_day")
    functional_scores = pd.DataFrame({CUSTOMER_ID: features[CUSTOMER_ID]})
    functional_status = pd.DataFrame(
        {
            CUSTOMER_ID: features[CUSTOMER_ID],
            "functional_analysis_status": "method_not_available",
        }
    )
    cluster_path = _MODEL_DIR / "summary_clusters.joblib"
    shape_cluster_path = _MODEL_DIR / "shape_clusters.joblib"
    cluster_representation = None
    if cluster_path.is_file():
        fitted = joblib.load(cluster_path)
        assignments = assign_trajectory_clusters(fitted, features)
        cluster_representation = "summary_features"
    elif shape_cluster_path.is_file():
        fitted = joblib.load(shape_cluster_path)
        cluster_config = TrajectoryClusteringConfig(
            **{
                **fitted["config"],
                "feature_columns": tuple(fitted["config"]["feature_columns"]),
            }
        )
        prepared_shape_features = prepare_trajectory_features(
            shape_features, cluster_config
        )
        assignments = assign_trajectory_clusters(fitted, prepared_shape_features)
        cluster_representation = "standardized_curve_shape"
    functional_path = _MODEL_DIR / "functional_pca.joblib"
    if functional_path.is_file():
        fitted_functional = joblib.load(functional_path)
        functional_scores = transform_functional_representation(
            fitted_functional, curves
        )
        functional_status = functional_scores[
            [CUSTOMER_ID, "functional_analysis_status"]
        ].copy()
    features = features.merge(
        assignments,
        on=CUSTOMER_ID,
        how="left",
        validate="one_to_one",
    ).merge(
        functional_status,
        on=CUSTOMER_ID,
        how="left",
        validate="one_to_one",
    )
    metrics = _load_json(METRICS_DIR / "trajectory_analysis_evaluation.json")
    metadata = _load_json(_MODEL_DIR / "metadata.json")
    return {
        "events": events,
        "matrix": matrix,
        "features": features,
        "curves": curves,
        "functional_scores": functional_scores,
        "metrics": metrics,
        "metadata": metadata,
        "model_version": metadata.get("model_version", MODEL_VERSION),
        "cutoff_date": CUTOFF_DATE,
        "cluster_model_available": cluster_path.is_file() or shape_cluster_path.is_file(),
        "cluster_representation": cluster_representation,
        "functional_model_available": functional_path.is_file(),
    }


def get_trajectory_summary() -> dict[str, Any]:
    data = _get_trajectory_bundle()
    features = data["features"]
    counts = (
        features["history_sufficiency"]
        .value_counts()
        .reindex(
            [
                "sufficient_for_functional_analysis",
                "sufficient_for_summary_trajectory",
                "limited_history",
                "insufficient_history",
            ],
            fill_value=0,
        )
    )
    assigned = int(features["trajectory_cluster_id"].notna().sum())
    functional = int(features["eligible_for_functional_analysis"].sum())
    cluster_available = bool(data["cluster_model_available"])
    functional_available = bool(data["functional_model_available"])
    return {
        "cutoff_date": data["cutoff_date"].date(),
        "summary_trajectory_eligible_customers": int(
            features["eligible_for_summary_trajectory"].sum()
        ),
        "shape_cluster_eligible_customers": int(
            features["shape_cluster_eligible"].sum()
        ),
        "total_customers": int(features[CUSTOMER_ID].nunique()),
        "history_sufficiency_counts": {
            str(key): int(value) for key, value in counts.items()
        },
        "clustered_customer_count": assigned,
        "unassigned_customer_count": int(len(features) - assigned),
        "functional_eligible_customers": functional,
        "available_trajectory_methods": [
            "exposure_adjusted_30_day_rolling_trajectories",
            *(
                [
                    "train_fitted_curve_shape_clustering"
                    if data["cluster_representation"] == "standardized_curve_shape"
                    else "train_fitted_summary_feature_clustering"
                ]
                if cluster_available
                else []
            ),
            *(
                ["train_fitted_grid_based_functional_pca"]
                if functional_available
                else []
            ),
        ],
        "selected_representation": (
            (
                "standardized_curve_shape_clustering_and_grid_based_functional_pca"
                if data["cluster_representation"] == "standardized_curve_shape"
                else "summary_features_and_grid_based_functional_pca"
            )
            if cluster_available and functional_available
            else (
                (
                    f"{data['cluster_representation']}_clustering_and_descriptive_rolling_trajectories"
                    if cluster_available
                    else "descriptive_rolling_trajectories_and_grid_based_functional_pca"
                )
                if functional_available
                else (
                    (
                        f"{data['cluster_representation']}_clustering_and_descriptive_rolling_trajectories"
                    )
                    if cluster_available
                    else "descriptive_rolling_trajectories"
                )
            )
        ),
        "model_version": data["model_version"],
        "limitations": list(
            data["metadata"].get(
                "api_limitations",
                [
                    "Available customer histories are left-truncated.",
                    "Unfitted or unsupported clustering/FDA methods are not assigned.",
                ],
            )
        ),
    }


def get_trajectory_clusters() -> dict[str, Any]:
    data = _get_trajectory_bundle()
    features = data["features"]
    if not data["cluster_model_available"]:
        return {
            "cutoff_date": data["cutoff_date"].date(),
            "available": False,
            "assignment_coverage": 0.0,
            "clusters": [],
            "limitations": [
                "No statistically supported TRAIN-fitted cluster model is available.",
                "No customer is assigned a fabricated or fallback cluster.",
            ],
        }
    matrix = data["matrix"]
    curve_lookup = {
        "purchase_rate": "purchase_rate_per_observed_day",
        "revenue_rate": "revenue_rate_per_observed_day",
    }
    total = int(features[CUSTOMER_ID].nunique())
    assigned = features.dropna(subset=["trajectory_cluster_id"])
    summaries: list[dict[str, Any]] = []
    for cluster_id, group in assigned.groupby("trajectory_cluster_id", sort=True):
        customer_ids = group[CUSTOMER_ID].tolist()
        cluster_matrix = matrix.loc[matrix[CUSTOMER_ID].isin(customer_ids)]
        means: dict[str, list[dict[str, Any]]] = {}
        for series_name, column in curve_lookup.items():
            grouped = cluster_matrix.groupby("window_index")[column].mean()
            means[series_name] = [
                {"window_index": int(index), "mean_rate": float(value)}
                for index, value in grouped.items()
                if pd.notna(value)
            ]
        segment_distribution = (
            group["Hist_Segment"].fillna("unavailable").value_counts().to_dict()
            if "Hist_Segment" in group
            else {}
        )
        summaries.append(
            {
                "cluster_id": int(cluster_id),
                "cluster_label": f"Trajectory group {int(cluster_id)}",
                "customer_count": int(len(group)),
                "cluster_share": float(len(group) / total) if total else 0.0,
                "mean_purchase_rate_curve": means["purchase_rate"],
                "mean_revenue_rate_curve": means["revenue_rate"],
                "historical_segment_distribution": {
                    str(key): int(value)
                    for key, value in segment_distribution.items()
                },
                "observed_purchasing_statistics": {
                    "mean_active_windows": float(
                        group["active_purchase_windows"].mean()
                    ),
                    "median_history_days": float(group["history_length_days"].median()),
                },
            }
        )
    return {
        "cutoff_date": data["cutoff_date"].date(),
        "available": True,
        "assignment_coverage": float(len(assigned) / total) if total else 0.0,
        "clusters": summaries,
        "limitations": [
            "Cluster identifiers are arbitrary empirical labels, not risk ranks.",
            "Displayed profiles are descriptive and do not imply causal effects.",
        ],
    }


def get_trajectory_customers(
    *,
    page: int,
    page_size: int,
    search: str | None,
    history_sufficiency: str | None,
    hist_segment: str | None,
    cluster_id: int | None,
) -> dict[str, Any]:
    features = _get_trajectory_bundle()["features"]
    filtered = features
    if search:
        filtered = filtered.loc[
            filtered[CUSTOMER_ID].astype("string").str.contains(
                search.strip(), regex=False, na=False
            )
        ]
    if history_sufficiency:
        filtered = filtered.loc[
            filtered["history_sufficiency"].eq(history_sufficiency)
        ]
    if hist_segment:
        filtered = filtered.loc[filtered["Hist_Segment"].eq(hist_segment)]
    if cluster_id is not None:
        filtered = filtered.loc[
            filtered["trajectory_cluster_id"].eq(cluster_id)
        ]
    total = int(len(filtered))
    ordered = filtered.sort_values(CUSTOMER_ID, kind="mergesort")
    start = (page - 1) * page_size
    columns = [
        CUSTOMER_ID,
        "history_sufficiency",
        "eligible_for_summary_trajectory",
        "shape_cluster_eligible",
        "shape_cluster_eligibility_status",
        "eligible_for_functional_analysis",
        "observed_windows",
        "active_purchase_windows",
        "completed_purchase_gaps",
        "trajectory_cluster_id",
        "cluster_assignment_status",
        "functional_analysis_status",
        "Hist_Segment",
        "history_length_days",
    ]
    items = _records(
        ordered.iloc[start : start + page_size][columns].rename(
            columns={
                CUSTOMER_ID: "customer_id",
                "eligible_for_summary_trajectory": "summary_trajectory_eligible",
                "eligible_for_functional_analysis": "functional_eligible",
                "Hist_Segment": "hist_segment",
                "trajectory_cluster_id": "trajectory_cluster_id",
            }
        )
    )
    for item in items:
        item["trajectory_cluster_label"] = (
            f"Trajectory group {item['trajectory_cluster_id']}"
            if item["trajectory_cluster_id"] is not None
            else None
        )
    return {
        "cutoff_date": _get_trajectory_bundle()["cutoff_date"].date(),
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "model_version": _get_trajectory_bundle()["model_version"],
    }


def get_customer_trajectory(customer_id: int) -> dict[str, Any]:
    data = _get_trajectory_bundle()
    features = data["features"]
    match = features.loc[features[CUSTOMER_ID].eq(customer_id)]
    if match.empty:
        raise KeyError(customer_id)
    row = match.iloc[0]
    matrix = data["matrix"].loc[
        data["matrix"][CUSTOMER_ID].eq(customer_id)
    ].sort_values("window_index", kind="mergesort")
    points = _records(
        matrix[
            [
                "window_index",
                "window_start",
                "window_end",
                "observed_exposure_days",
                "purchase_count",
                "gross_revenue",
                "purchase_rate_per_observed_day",
                "revenue_rate_per_observed_day",
                "window_has_purchase",
                "window_observation_status",
            ]
        ].rename(
            columns={
                "purchase_rate_per_observed_day": "purchase_rate",
                "revenue_rate_per_observed_day": "revenue_rate",
            }
        )
    )
    scores = data["functional_scores"].loc[
        data["functional_scores"][CUSTOMER_ID].eq(customer_id)
    ]
    score_values: dict[str, float | None] = {}
    if not scores.empty:
        for column in scores.columns:
            if column.startswith("functional_component_"):
                value = scores.iloc[0][column]
                score_values[column] = (
                    float(value) if pd.notna(value) else None
                )
    cluster_id = (
        int(row["trajectory_cluster_id"])
        if pd.notna(row["trajectory_cluster_id"])
        else None
    )
    return {
        "customer_id": int(customer_id),
        "cutoff_date": data["cutoff_date"].date(),
        "history_sufficiency": str(row["history_sufficiency"]),
        "summary_trajectory_eligible": bool(
            row["eligible_for_summary_trajectory"]
        ),
        "shape_cluster_eligible": bool(row["shape_cluster_eligible"]),
        "shape_cluster_eligibility_status": str(
            row["shape_cluster_eligibility_status"]
        ),
        "functional_eligible": bool(row["eligible_for_functional_analysis"]),
        "history_support_details": {
            "observed_windows": int(row["observed_windows"]),
            "active_purchase_windows": int(row["active_purchase_windows"]),
            "completed_purchase_gaps": int(row["completed_purchase_gaps"]),
            "history_length_days": float(row["history_length_days"]),
            "first_observed_purchase_date": pd.Timestamp(
                row["first_observed_purchase_date"]
            ).date(),
        },
        "purchase_rate_trajectory": points,
        "revenue_rate_trajectory": points,
        "trajectory_cluster_id": cluster_id,
        "trajectory_cluster_label": (
            f"Trajectory group {cluster_id}" if cluster_id is not None else None
        ),
        "cluster_assignment_status": str(row["cluster_assignment_status"]),
        "functional_component_scores": score_values,
        "functional_analysis_status": str(row["functional_analysis_status"]),
        "model_version": data["model_version"],
        "limitations": list(row["limitations"]),
    }


def get_customer_trajectory_explanation(customer_id: int) -> dict[str, Any]:
    detail = get_customer_trajectory(customer_id)
    features = _get_trajectory_bundle()["features"]
    row = features.loc[features[CUSTOMER_ID].eq(customer_id)].iloc[0]
    return {
        "customer_id": int(customer_id),
        "cutoff_date": detail["cutoff_date"],
        "history_sufficiency": detail["history_sufficiency"],
        "summary_trajectory_eligible": detail["summary_trajectory_eligible"],
        "shape_cluster_eligible": detail["shape_cluster_eligible"],
        "shape_cluster_eligibility_status": detail[
            "shape_cluster_eligibility_status"
        ],
        "functional_eligible": detail["functional_eligible"],
        "supported_features": {
            "purchase_rate_slope_per_window": (
                float(row["purchase_rate_slope_per_window"])
                if pd.notna(row["purchase_rate_slope_per_window"])
                else None
            ),
            "revenue_rate_slope_per_window": (
                float(row["revenue_rate_slope_per_window"])
                if pd.notna(row["revenue_rate_slope_per_window"])
                else None
            ),
            "active_purchase_windows": int(row["active_purchase_windows"]),
            "longest_observed_inactive_run": int(
                row["longest_observed_inactive_run"]
            ),
            "completed_gap_slope_days_per_gap": (
                float(row["completed_gap_slope_days_per_gap"])
                if pd.notna(row["completed_gap_slope_days_per_gap"])
                else None
            ),
        },
        "cluster_assignment_status": detail["cluster_assignment_status"],
        "functional_analysis_status": detail["functional_analysis_status"],
        "interpretation": (
            "These are descriptive summaries of the recorded pre-cutoff history. "
            "They do not establish customer intent, churn, or causal effects."
        ),
        "limitations": detail["limitations"],
    }


def get_trajectory_evaluation() -> dict[str, Any]:
    data = _get_trajectory_bundle()
    if not data["metrics"]:
        return {
            "status": "evaluation_not_available",
            "model_version": data["model_version"],
            "results": {},
            "limitations": [
                "Notebook 11 evaluation results have not been generated.",
                "The API does not fit models or compute future outcome labels.",
            ],
        }
    return {
        "status": str(data["metrics"].get("status", "available")),
        "model_version": data["model_version"],
        "results": data["metrics"],
        "limitations": list(data["metrics"].get("limitations", [])),
    }
