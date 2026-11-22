import numpy as np
import pandas as pd
import pytest

from src import spending_model as sm


def make_features(n=60, *, cutoff="2010-06-01", offset=0):
    rows = []
    for index in range(n):
        frequency = 1 + index % 8
        tenure = 0.5 + (index % 24) * 8
        gross = 30.0 + frequency * 37.0 + (index % 7) * 19.0
        rows.append(
            {
                "Customer ID": offset + 1000 + index,
                "cutoff_date": pd.Timestamp(cutoff),
                "Recency": float(1 + index % 110),
                "Frequency": float(frequency),
                "Monetary_Gross": gross,
                "AOV": gross / frequency,
                "Tenure_obs_days": tenure,
                "PurchaseRate_per_obs_day": frequency / tenure,
                "SpendRate_per_obs_day": gross / tenure,
                "Median_Gap_days": np.nan if frequency == 1 else float(5 + index % 45),
                "Recent_Orders": float(index % 5),
                "Recent_Revenue": float((index % 5) * 31),
                "Hist_Segment": "Recent / Active" if index % 2 else "Lapsed / At-Risk",
                "Hist_Cluster_id": index % 2,
            }
        )
    return pd.DataFrame(rows)


def make_targets(features, horizon=30, *, offset=0):
    rows = []
    for index, customer_id in enumerate(features["Customer ID"]):
        purchaser = index % 3 != 0
        revenue = 75.0 + (index % 11) * 42.0 + (index % 5) * 21.0 if purchaser else 0.0
        rows.append(
            {
                "Customer ID": customer_id,
                f"FutureOrders_{horizon}d": 1 if purchaser else 0,
                f"FutureRevenue_{horizon}d": revenue + offset if purchaser else 0.0,
            }
        )
    return pd.DataFrame(rows)


def fitted_bundle(tmp_path):
    train = make_features(60, cutoff="2010-06-01")
    val = make_features(24, cutoff="2010-08-01", offset=2000)
    train_targets = make_targets(train)
    val_targets = make_targets(val, offset=15.0)
    horizon_model = sm.fit_horizon_models(
        train,
        train_targets,
        val,
        val_targets,
        30,
        alpha_candidates=(0.1, 1.0, 10.0, 100.0),
    )
    bundle = {
        "metadata": {"model_version": sm.MODEL_VERSION},
        "horizon_models": {30: horizon_model},
    }
    return bundle, val


def test_future_outcomes_are_rejected_as_predictors():
    features = make_features(5)
    features["FutureRevenue_30d"] = 0.0
    with pytest.raises(ValueError, match="cannot be predictors"):
        sm.validate_features(features)


def test_rate_baseline_shrinks_short_tenure_and_caps_training_extreme():
    train = make_features(30)
    train.loc[0, "Tenure_obs_days"] = 0.01
    train.loc[0, "Monetary_Gross"] = 1_000_000.0
    baseline = sm.fit_rate_baseline(train)
    predictions = sm.predict_rate_baseline(baseline, train, 30)
    assert np.isfinite(predictions).all()
    assert (predictions >= 0).all()
    assert predictions[0] <= baseline["rate_cap"] * 30
    assert baseline["prior_exposure_days"] == 30.0


def test_segment_model_shrinks_small_groups_to_global_and_falls_back_unknown():
    train = make_features(12)
    targets = make_targets(train)
    model = sm.fit_segment_conditional(train, targets, 30, prior_purchasers=20)
    new = make_features(3)
    new.loc[:, "Hist_Segment"] = ["Recent / Active", "Lapsed / At-Risk", "New Segment"]
    predictions = sm.predict_segment_conditional(model, new)
    assert np.isfinite(predictions).all()
    assert predictions[2] == pytest.approx(model["global_conditional_mean"])


def test_personalized_training_uses_buyers_and_handles_missing_gap_features():
    train = make_features(60)
    val = make_features(24, cutoff="2010-08-01", offset=2000)
    train_targets, val_targets = make_targets(train), make_targets(val)
    fitted = sm.fit_personalized_conditional(
        train, train_targets, val, val_targets, 30, alpha_candidates=(0.1, 1, 10, 100)
    )
    predictions = sm.predict_personalized_conditional(fitted, val)
    assert fitted["training_purchasers"] == int((train_targets["FutureOrders_30d"] > 0).sum())
    assert set(fitted["selection_metrics"]["alpha"]) == {0.1, 1.0, 10.0, 100.0}
    assert np.isfinite(predictions).all()
    assert (predictions >= 0).all()
    assert fitted["smearing_factor"] > 0
    assert "OOF" in fitted["retransformation"]
    extreme = val.iloc[:2].copy()
    extreme["Tenure_obs_days"] = 0.01
    extreme["PurchaseRate_per_obs_day"] = 1e9
    extreme["SpendRate_per_obs_day"] = 1e9
    extreme["Monetary_Gross"] = 1e9
    extreme["AOV"] = 1e9
    assert sm.predict_personalized_conditional(fitted, extreme).max() < 100_000


def test_joint_inference_multiplies_conditional_amounts_by_aligned_probabilities(tmp_path):
    bundle, val = fitted_bundle(tmp_path)
    probabilities = pd.DataFrame(
        {
            "Customer ID": val["Customer ID"],
            "cutoff_date": val["cutoff_date"],
            "personalized_P30": np.linspace(0.1, 0.9, len(val)),
        }
    )
    predictions = sm.predict_expected_revenue(bundle, val, probabilities)
    np.testing.assert_allclose(
        predictions["segment_expected_revenue_30d"],
        predictions["purchase_probability_30d"]
        * predictions["segment_conditional_revenue_30d"],
    )
    np.testing.assert_allclose(
        predictions["personalized_expected_revenue_30d"],
        predictions["purchase_probability_30d"]
        * predictions["personalized_conditional_revenue_30d"],
    )
    assert np.isfinite(predictions.select_dtypes("number").to_numpy()).all()
    assert not any(column.startswith("Future") for column in predictions.columns)


def test_joint_inference_rejects_mismatched_customer_or_cutoff():
    features = make_features(6)
    probabilities = pd.DataFrame(
        {
            "Customer ID": features["Customer ID"],
            "cutoff_date": features["cutoff_date"] + pd.Timedelta(days=1),
            "personalized_P30": 0.5,
        }
    )
    with pytest.raises(ValueError, match="do not match"):
        sm._align_purchase_probabilities(features, probabilities, (30,))


def test_saved_model_reloads_with_same_inference(tmp_path):
    bundle, val = fitted_bundle(tmp_path)
    probability_frame = pd.DataFrame(
        {
            "Customer ID": val["Customer ID"],
            "cutoff_date": val["cutoff_date"],
            "personalized_P30": 0.4,
        }
    )
    before = sm.predict_expected_revenue(bundle, val, probability_frame)
    sm.save_spending_artifacts(bundle, tmp_path)
    loaded = sm.load_spending_artifacts(tmp_path)
    after = sm.predict_expected_revenue(loaded, val, probability_frame)
    numeric = [column for column in before if column not in ("Customer ID", "cutoff_date")]
    np.testing.assert_allclose(before[numeric], after[numeric], rtol=0, atol=1e-12)


def test_evaluation_metrics_use_all_customers_and_report_aggregate_calibration():
    actual = np.array([0.0, 100.0, 250.0])
    predicted = np.array([10.0, 90.0, 300.0])
    metrics = sm.evaluate_expected_revenue(actual, predicted)
    assert metrics["n_customers"] == 3
    assert metrics["total_predicted_revenue"] == pytest.approx(400.0)
    assert metrics["total_actual_revenue"] == pytest.approx(350.0)
    assert metrics["aggregate_calibration_ratio"] == pytest.approx(400 / 350)
    conditional = sm.evaluate_conditional_spending(actual[1:], predicted[1:])
    assert conditional["n_purchasers"] == 2
