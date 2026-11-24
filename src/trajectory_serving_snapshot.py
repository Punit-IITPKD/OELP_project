"""Offline construction of the frozen, read-only trajectory serving snapshot."""

from __future__ import annotations

import json
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
from src.trajectory_snapshot_format import (
    SNAPSHOT_SCHEMA_VERSION,
    source_manifest,
)

MODEL_VERSION = "customer-trajectory-analysis-v2"
CUTOFF_DATE = pd.Timestamp("2010-09-10")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path.name}.")
    return value


def build_trajectory_bundle_from_sources(
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Recreate API-ready features from historical inputs and saved models only."""
    root = Path(root)
    orders_path = root / "data/processed/temporal/orders.csv"
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
    split_path = root / "data/processed/temporal/predictive_splits_30d.csv"
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
    curves = build_trajectory_curve_table(
        matrix, features, rate_column="purchase_rate_per_observed_day"
    )
    functional_scores = pd.DataFrame({CUSTOMER_ID: features[CUSTOMER_ID]})
    functional_status = pd.DataFrame(
        {
            CUSTOMER_ID: features[CUSTOMER_ID],
            "functional_analysis_status": "method_not_available",
        }
    )
    cluster_path = root / "models/trajectory_analysis/summary_clusters.joblib"
    shape_cluster_path = root / "models/trajectory_analysis/shape_clusters.joblib"
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
    functional_path = root / "models/trajectory_analysis/functional_pca.joblib"
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
    metrics = _load_json(root / "data/metrics/trajectory_analysis_evaluation.json")
    metadata = _load_json(root / "models/trajectory_analysis/metadata.json")
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


def dataframe_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    serialized = frame.to_json(
        orient="records",
        date_format="iso",
        double_precision=12,
    )
    return json.loads(serialized)


def create_snapshot_payload(
    bundle: dict[str, Any],
    *,
    root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Create only the historical, pre-cutoff fields used by trajectory APIs."""
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "source_manifest": source_manifest(root),
        "bundle": {
            "matrix": dataframe_records(bundle["matrix"]),
            "features": dataframe_records(bundle["features"]),
            "curves": dataframe_records(bundle["curves"]),
            "functional_scores": dataframe_records(bundle["functional_scores"]),
            "metrics": bundle["metrics"],
            "metadata": bundle["metadata"],
            "model_version": bundle["model_version"],
            "cutoff_date": CUTOFF_DATE.date().isoformat(),
            "cluster_model_available": bundle["cluster_model_available"],
            "cluster_representation": bundle["cluster_representation"],
            "functional_model_available": bundle["functional_model_available"],
        },
    }
