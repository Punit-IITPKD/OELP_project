from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.trajectory_clustering import (
    TrajectoryClusteringConfig,
    assign_trajectory_clusters,
    build_shape_trajectory_features,
    compare_static_dynamic_segments,
    evaluate_cluster_stability,
    fit_trajectory_clusters,
    prepare_trajectory_features,
)

FEATURES = (
    "purchase_rate_slope_per_window",
    "revenue_rate_slope_per_window",
    "purchase_rate_recent_minus_early",
    "revenue_rate_recent_minus_early",
    "purchase_rate_volatility",
    "revenue_rate_volatility",
    "active_purchase_windows",
    "longest_observed_inactive_run",
    "completed_gap_slope_days_per_gap",
)


def _feature_table(rows: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(18)
    labels = np.arange(rows) % 3
    frame = pd.DataFrame({"Customer ID": np.arange(100, 100 + rows)})
    for column_index, column in enumerate(FEATURES):
        frame[column] = labels * (column_index + 1) + rng.normal(0, 0.2, rows)
    frame["eligible_for_summary_trajectory"] = True
    return frame


def test_clustering_transform_and_assignments_are_frozen_from_train() -> None:
    train = _feature_table()
    config = TrajectoryClusteringConfig(
        n_clusters=3,
        stability_runs=3,
        n_init=5,
    )
    prepared = prepare_trajectory_features(train, config)
    fitted = fit_trajectory_clusters(prepared, config)
    assigned = assign_trajectory_clusters(fitted, prepared)
    evaluation = evaluate_cluster_stability(prepared, fitted, config)

    assert fitted["fit_role"] == "TRAIN"
    assert fitted["transform"]["fit_customer_count"] == len(train)
    assert assigned["trajectory_cluster_id"].notna().all()
    assert assigned["trajectory_cluster_id"].nunique() == 3
    assert evaluation["eligible_train_customers"] == len(train)
    assert evaluation["seed_adjusted_rand_mean"] is not None


def test_unsupported_customers_remain_unassigned() -> None:
    train = _feature_table()
    config = TrajectoryClusteringConfig(n_clusters=3, stability_runs=1, n_init=3)
    prepared = prepare_trajectory_features(train, config)
    fitted = fit_trajectory_clusters(prepared, config)
    new_rows = _feature_table(2)
    new_rows["Customer ID"] += 1000
    new_rows["eligible_for_summary_trajectory"] = False
    assigned = assign_trajectory_clusters(
        fitted, prepare_trajectory_features(new_rows, config)
    )

    assert assigned["trajectory_cluster_id"].isna().all()
    assert assigned["cluster_assignment_status"].eq("insufficient_history").all()


def test_outcome_features_are_rejected_before_fit() -> None:
    frame = _feature_table()
    frame["future_purchase_count"] = 1
    with pytest.raises(ValueError, match="Outcome/target"):
        prepare_trajectory_features(frame)

    with pytest.raises(ValueError, match="forbidden"):
        TrajectoryClusteringConfig(
            feature_columns=("purchase_rate_slope_per_window", "future_revenue")
        )


def test_shape_curves_require_a_complete_observation_grid() -> None:
    matrix = pd.DataFrame(
        [
            (1, 0, 30, 1, 0.1),
            (1, 1, 30, 0, 0.0),
            (1, 2, 30, 2, 0.2),
            (2, 0, 30, 1, 0.1),
            (2, 1, 0, np.nan, np.nan),
            (2, 2, 0, np.nan, np.nan),
        ],
        columns=[
            "Customer ID",
            "window_index",
            "observed_exposure_days",
            "purchase_count",
            "purchase_rate_per_observed_day",
        ],
    )
    matrix["completed_purchase_gaps"] = matrix["Customer ID"].map({1: 1, 2: 1})

    shapes = build_shape_trajectory_features(matrix).set_index("Customer ID")

    assert shapes.loc[1, "cluster_eligible"]
    assert shapes.loc[1, "shape_transform_status"] == "standardized_shape"
    assert not shapes.loc[2, "cluster_eligible"]
    assert pd.isna(shapes.loc[2, "shape_window_1"])


def test_shape_cluster_assignments_require_repeated_activity_and_a_completed_gap() -> None:
    rows = []
    for customer_id in range(1, 34):
        if customer_id == 1:
            counts, completed_gaps = [1, 0, 0, 0, 0, 0], 1
        elif customer_id == 2:
            counts, completed_gaps = [1, 0, 1, 0, 0, 0], 0
        else:
            first_active = customer_id % 6
            second_active = (first_active + 2) % 6
            counts = [
                (1 + customer_id % 3) if index == first_active
                else 1 if index == second_active
                else 0
                for index in range(6)
            ]
            completed_gaps = 1 + customer_id % 2
        for window_index, purchase_count in enumerate(counts):
            rows.append(
                {
                    "Customer ID": customer_id,
                    "window_index": window_index,
                    "observed_exposure_days": 30,
                    "purchase_count": purchase_count,
                    "purchase_rate_per_observed_day": purchase_count / 30,
                    "completed_purchase_gaps": completed_gaps,
                }
            )
    matrix = pd.DataFrame(rows)
    shapes = build_shape_trajectory_features(matrix)
    shape_columns = tuple(
        column for column in shapes if column.startswith("shape_window_")
    )
    config = TrajectoryClusteringConfig(
        feature_columns=shape_columns,
        eligible_column="cluster_eligible",
        n_clusters=2,
        stability_runs=1,
        n_init=3,
    )
    prepared = prepare_trajectory_features(shapes, config)
    fitted = fit_trajectory_clusters(prepared, config)
    assigned = assign_trajectory_clusters(fitted, prepared).set_index("Customer ID")
    support = shapes.set_index("Customer ID")

    assert not support.loc[1, "cluster_eligible"]
    assert support.loc[1, "active_purchase_windows"] == 1
    assert support.loc[1, "shape_transform_status"] == "insufficient_active_purchase_windows"
    assert assigned.loc[1, "trajectory_cluster_id"] is pd.NA or pd.isna(
        assigned.loc[1, "trajectory_cluster_id"]
    )
    assert not support.loc[2, "cluster_eligible"]
    assert support.loc[2, "active_purchase_windows"] == 2
    assert support.loc[2, "completed_purchase_gaps"] == 0
    assert pd.isna(assigned.loc[2, "trajectory_cluster_id"])


def test_static_dynamic_comparison_uses_only_customers_with_both_labels() -> None:
    static = pd.DataFrame(
        {
            "Customer ID": [1, 2, 3, 4],
            "Hist_Segment": ["A", "A", "B", "B"],
        }
    )
    dynamic = pd.DataFrame(
        {
            "Customer ID": [1, 2, 3, 4],
            "trajectory_cluster_id": pd.array([0, 0, 1, pd.NA], dtype="Int64"),
        }
    )

    result = compare_static_dynamic_segments(static, dynamic)

    assert result["comparable_customers"] == 3
    assert result["adjusted_rand_index"] == pytest.approx(1.0)
