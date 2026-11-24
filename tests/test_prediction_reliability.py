from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.prediction_reliability import (
    ReliabilityConfig,
    assess_distribution_support,
    attach_customer_reliability_context,
    build_reliability_artifact,
    compute_calibration_bins,
    compute_probability_metrics,
    compute_subgroup_reliability,
    estimate_group_metric_intervals,
)


def test_calibration_bins_handle_boundaries_and_empty_bins():
    bins = compute_calibration_bins(
        [0.0, 0.5, 1.0],
        [0, 0, 1],
        [0.0, 0.25, 0.5, 0.75, 1.0],
    )
    assert bins["customer_count"].tolist() == [1, 0, 1, 1]
    assert bins.loc[1, "mean_predicted_probability"] is None or pd.isna(
        bins.loc[1, "mean_predicted_probability"]
    )
    assert bins.loc[2, "mean_predicted_probability"] == 0.5
    assert bins.loc[3, "observed_purchase_rate"] == 1.0


def test_probability_metrics_match_known_values_and_single_class_is_nullable():
    metrics = compute_probability_metrics(
        [0.0, 0.5, 1.0], [0, 0, 1], [0.0, 0.5, 1.0]
    )
    assert metrics["brier_score"] == pytest.approx(1.0 / 12.0)
    assert metrics["mean_predicted_probability"] == pytest.approx(0.5)
    assert metrics["observed_purchase_rate"] == pytest.approx(1.0 / 3.0)
    assert metrics["expected_calibration_error"] == pytest.approx(1.0 / 6.0)
    assert metrics["maximum_calibration_error"] == pytest.approx(0.25)
    single = compute_probability_metrics([0.1, 0.2], [0, 0])
    assert single["roc_auc"] is None
    assert single["average_precision"] is None
    assert single["average_precision_reason"]


@pytest.mark.parametrize(
    ("predictions", "outcomes", "edges"),
    [
        ([np.nan], [0], [0.0, 1.0]),
        ([1.1], [1], [0.0, 1.0]),
        ([0.5], [2], [0.0, 1.0]),
        ([0.5], [1], [0.0, 0.0, 1.0]),
    ],
)
def test_invalid_probability_inputs_are_rejected(predictions, outcomes, edges):
    with pytest.raises(ValueError):
        compute_calibration_bins(predictions, outcomes, edges)


def _evaluation_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "horizon_days": [30, 30, 30, 30],
            "predicted_probability": [0.1, 0.3, 0.7, 0.9],
            "observed_outcome": [0, 0, 1, 1],
            "history_group": ["one", "one", "many", "many"],
            "actual_revenue": [0.0, 10.0, 20.0, 30.0],
            "predicted_revenue": [1.0, 12.0, 19.0, 35.0],
        }
    )


def test_subgroup_support_and_single_class_metrics_are_explicit():
    frame = _evaluation_frame()
    result = compute_subgroup_reliability(
        frame,
        ["history_group"],
        ReliabilityConfig(minimum_group_support=3, bootstrap_resamples=20),
    )
    assert set(result["status"]) == {"insufficient_evaluation_support"}
    assert result["customer_count"].tolist() == [2, 2]
    assert result["average_precision"].isna().all()

    single = frame.copy()
    single.loc[single["history_group"].eq("one"), "observed_outcome"] = 0
    single.loc[single["history_group"].eq("one"), "predicted_probability"] = 0.0
    summary = compute_subgroup_reliability(
        single,
        ["history_group"],
        ReliabilityConfig(minimum_group_support=1, bootstrap_resamples=20),
    )
    one = summary.loc[summary["group"].eq("one")].iloc[0]
    assert one["status"] == "single_outcome_class"
    assert one["average_precision"] is None


def test_customer_bootstrap_is_deterministic_and_cluster_safe():
    frame = _evaluation_frame()
    config = ReliabilityConfig(
        minimum_group_support=1,
        bootstrap_resamples=100,
        random_seed=17,
    )
    first = estimate_group_metric_intervals(frame, "brier_score", config)
    second = estimate_group_metric_intervals(frame, "brier_score", config)
    pd.testing.assert_frame_equal(first, second)
    assert first.iloc[0]["successful_bootstrap_samples"] == 100
    assert first.iloc[0]["lower"] <= first.iloc[0]["upper"]
    repeated = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="one row per customer"):
        estimate_group_metric_intervals(repeated, "brier_score", config)


def test_distribution_support_flags_are_train_reference_diagnostics():
    profile = {
        "numeric_bounds": {
            "Recency": {"lower": 1.0, "upper": 90.0},
            "Frequency": {"lower": 1.0, "upper": 10.0},
        },
        "categorical_values": {"Hist_Segment": ["Active", "At-risk"]},
    }
    result = assess_distribution_support(
        {"Recency": 120, "Frequency": 4, "Hist_Segment": "New"},
        profile,
    )
    assert result["atypical_feature_count"] == 2
    assert {flag["feature"] for flag in result["flags"]} == {
        "Recency",
        "Hist_Segment",
    }
    assert "not probabilities" in result["interpretation"]


def test_artifact_metadata_and_customer_reliability_attachment():
    metadata = {
        "purchase_clock_model_version": "purchase-clock-v2",
        "spending_model_version": "spending-forecast-v2",
        "forecast_cutoff": "2010-09-10",
        "TRAIN_source": "train.csv",
        "VAL_source": "val.csv",
        "TEST_source": "test.csv",
        "calibration_binning_method": {"30": "validation_quantile"},
        "minimum_group_support": 100,
        "bootstrap_method": "customer-level",
        "bootstrap_resamples": 500,
        "reference_profile_definition": "training-only medians",
        "known_limitations": [],
    }
    artifact = build_reliability_artifact(
        {"bin_selection_by_horizon": {}},
        {
            "metadata": metadata,
            "subgroups": [
                {
                    "group_type": "history_group",
                    "group": "Exactly one purchase",
                    "horizon_days": 30,
                    "customer_count": 120,
                    "brier_score": 0.2,
                    "calibration_gap": 0.03,
                    "status": "well_supported_historical_evaluation_group",
                }
            ],
        },
        ReliabilityConfig(),
    )
    assert artifact["metadata"]["artifact_version"] == "prediction-reliability-v1"
    attached = attach_customer_reliability_context(
        pd.DataFrame(
            {"history_group": ["Exactly one purchase"], "horizon_days": [30]}
        ),
        artifact,
    )
    assert attached.loc[0, "evaluation_group_count"] == 120
    assert attached.loc[0, "group_calibration_gap"] == 0.03
    assert attached.loc[0, "reliability_status"] == (
        "well_supported_historical_evaluation_group"
    )
