from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.trajectory_research import (
    analyze_future_purchase_associations,
    assess_purchase_clock_vintage_availability,
    build_future_purchase_outcomes,
    build_trajectory_feasibility_report,
    compute_binary_prediction_metrics,
    fit_trajectory_purchase_model,
    analyze_trajectory_feature_outcome_associations,
    paired_brier_difference_interval,
    predict_trajectory_purchase_probability,
)


def _orders(rows: list[tuple[int, str, str, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=["Customer ID", "Invoice", "PurchaseDate", "GrossRevenue"],
    )


def test_feasibility_report_counts_customers_and_reports_method_coverage() -> None:
    orders = _orders(
        [
            (1, "1001", "2020-01-02", 10),
            (1, "1002", "2020-01-20", 15),
            (1, "1003", "2020-02-10", 12),
            (1, "1004", "2020-03-10", 14),
            (1, "1005", "2020-04-10", 16),
            (2, "2001", "2020-04-12", 8),
        ]
    )
    splits = {
        30: {
            "train": pd.Timestamp("2020-04-01"),
            "val": pd.Timestamp("2020-04-15"),
            "test": pd.Timestamp("2020-05-01"),
        }
    }

    report = build_trajectory_feasibility_report(
        orders,
        split_specs=splits,
    )

    train = next(
        item for item in report["cutoffs"] if item["role"] == "TRAIN"
    )
    assert train["customer_count"] == 1
    assert train["valid_invoice_count"] == 4
    assert train["one_time_customers"] == 0
    methods = [item["method"] for item in report["feasibility"]]
    assert "Functional PCA" in methods
    assert all(item["coverage_percentage"] is not None for item in report["feasibility"])


def test_future_purchase_outcomes_require_mature_horizons_and_exclude_cutoff() -> None:
    orders = _orders(
        [
            (1, "1001", "2020-02-01", 10),
            (1, "1002", "2020-03-01", 12),
            (2, "2001", "2020-02-15", 8),
            (2, "2002", "2020-03-31", 100),
        ]
    )
    outcomes = build_future_purchase_outcomes(
        orders,
        [1, 2, 3],
        cutoff_date="2020-03-01",
        horizon_days=30,
        dataset_end="2020-03-31",
    ).set_index("Customer ID")

    assert outcomes.loc[1, "purchased_within_horizon"] == 0
    assert outcomes.loc[2, "purchased_within_horizon"] == 1
    assert outcomes.loc[2, "future_gross_revenue"] == 100
    assert outcomes.loc[3, "future_gross_revenue"] == 0
    with pytest.raises(ValueError, match="not fully observable"):
        build_future_purchase_outcomes(
            orders, [1], "2020-03-15", 30, "2020-04-01"
        )


def test_cluster_associations_include_uncertainty_and_fdr_adjustment() -> None:
    ids = np.arange(80)
    features = pd.DataFrame(
        {
            "Customer ID": ids,
            "history_length_days": 120 + ids,
            "Recency": ids % 40,
        }
    )
    assignments = pd.DataFrame(
        {
            "Customer ID": ids,
            "trajectory_cluster_id": (ids % 2).astype(int),
        }
    )
    outcomes = pd.DataFrame(
        {
            "Customer ID": ids,
            "purchased_within_horizon": (ids % 2).astype(int),
            "future_purchase_count": (ids % 2).astype(int),
        }
    )
    results = analyze_future_purchase_associations(
        features,
        assignments,
        {30: outcomes},
        n_bootstrap=200,
    )
    clusters = results["horizons"]["30"]["clusters"]

    assert len(clusters) == 2
    assert clusters[0]["difference_ci_95"] is not None
    assert clusters[0]["fdr_adjusted_q_value"] >= clusters[0]["fisher_exact_p_value"]
    assert "not causal" in results["horizons"]["30"]["interpretation"]


def test_feature_outcome_associations_cover_matured_horizons_with_uncertainty() -> None:
    ids = np.arange(120)
    features = pd.DataFrame(
        {
            "Customer ID": ids,
            "purchase_rate_slope_per_window": ids.astype(float),
            "active_purchase_windows": ids % 6,
        }
    )
    outcomes = {
        horizon: pd.DataFrame(
            {
                "Customer ID": ids,
                "purchased_within_horizon": (ids >= threshold).astype(int),
            }
        )
        for horizon, threshold in ((30, 95), (60, 80), (90, 65))
    }

    result = analyze_trajectory_feature_outcome_associations(
        features,
        outcomes,
        feature_columns=("purchase_rate_slope_per_window", "active_purchase_windows"),
        n_bootstrap=200,
    )

    assert set(result["horizons"]) == {"30", "60", "90"}
    for horizon in result["horizons"].values():
        association = horizon["feature_associations"][0]
        assert association["eligible_customers"] == 120
        assert association["point_biserial_correlation"] > 0
        assert association["bootstrap_ci_95"] is not None
        assert association["fdr_adjusted_q_value"] >= association["p_value"]
        assert "not establish independent predictive value" in horizon["interpretation"]


def test_saved_purchase_clock_vintages_are_blocked_for_official_train_cutoffs() -> None:
    metadata = {
        "available_for_test_by": "2010-08-30",
        "validation_vintage": {
            "first_usable_forecast_cutoff": "2010-07-01",
        },
    }

    report = assess_purchase_clock_vintage_availability(metadata)

    assert report["incremental_purchase_clock_plus_trajectory"] == (
        "not_fitted_due_to_vintage_unavailability"
    )
    assert all(
        item["status"] == "not_fitted_due_to_vintage_unavailability"
        for item in report["model_vintage_checks"].values()
    )
    assert report["retrained_saved_models"] is False


def test_trajectory_purchase_model_selects_on_validation_and_predicts() -> None:
    rng = np.random.default_rng(10)

    def data(ids: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
        risk = rng.normal(size=len(ids))
        labels = (risk > 0).astype(int)
        features = pd.DataFrame(
            {
                "Customer ID": ids,
                "purchase_rate_slope_per_window": risk,
                "active_purchase_windows": np.maximum(0, 3 + risk),
            }
        )
        targets = pd.DataFrame(
            {"Customer ID": ids, "purchased_within_horizon": labels}
        )
        return features, targets

    train_features, train_targets = data(np.arange(100, 220))
    val_features, val_targets = data(np.arange(300, 360))
    test_features, test_targets = data(np.arange(500, 560))
    fitted = fit_trajectory_purchase_model(
        train_features,
        train_targets,
        val_features,
        val_targets,
        feature_columns=(
            "purchase_rate_slope_per_window",
            "active_purchase_windows",
        ),
    )
    predictions = predict_trajectory_purchase_probability(fitted, test_features)
    joined = predictions.merge(test_targets, on="Customer ID", validate="one_to_one")
    metrics = compute_binary_prediction_metrics(
        joined["purchased_within_horizon"],
        joined["trajectory_purchase_probability"],
    )

    assert fitted["fit_role"] == "TRAIN"
    assert fitted["selection_role"] == "VAL"
    assert fitted["test_outcomes_used_for_selection_or_training"] is False
    assert len(predictions) == len(test_features)
    assert metrics["roc_auc"] > 0.9
    assert 0 <= metrics["brier_score"] <= 1
    with pytest.raises(ValueError, match="forbidden"):
        fit_trajectory_purchase_model(
            train_features,
            train_targets,
            val_features,
            val_targets,
            feature_columns=("future_purchase_count",),
        )


def test_paired_brier_difference_reports_same_customer_interval() -> None:
    y = np.array([0, 1, 0, 1, 1, 0] * 10)
    first = np.where(y == 1, 0.8, 0.2)
    second = np.full_like(first, 0.5, dtype=float)

    result = paired_brier_difference_interval(
        y, first, second, n_bootstrap=200
    )

    assert result["n_customers"] == len(y)
    assert result["difference_first_minus_second"] < 0
    assert result["ci_95"][1] < 0
    assert "not a causal" in result["interpretation"]
