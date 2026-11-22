import inspect
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import purchase_clock as pc


def make_features(n=12, *, cutoff="2010-03-01"):
    rows = []
    for index in range(n):
        frequency = 1 if index % 3 == 0 else 2 + index % 5
        rows.append(
            {
                "Customer ID": 1000 + index,
                "cutoff_date": pd.Timestamp(cutoff),
                "Hist_Cluster_id": index % 2,
                "Hist_Segment": "Recent / Active" if index % 2 else "Lapsed / At-Risk",
                "Recency": float(5 + index * 3),
                "Frequency": float(frequency),
                "Monetary_Gross": float(20 + index * 12),
                "AOV": float((20 + index * 12) / frequency),
                "Tenure_obs_days": float(30 + index * 10),
                "PurchaseRate_per_obs_day": float(frequency / (30 + index * 10)),
                "SpendRate_per_obs_day": float((20 + index * 12) / (30 + index * 10)),
                "Median_Gap_days": np.nan if frequency == 1 else float(10 + index * 2),
                "Recent_Orders": float(min(frequency, 4)),
            }
        )
    return pd.DataFrame(rows)


def make_outcomes(features, event_times, *, censor_at=90.0):
    rows = []
    for customer_id, event_time in zip(features["Customer ID"], event_times):
        occurred = event_time is not None
        rows.append(
            {
                "Customer ID": customer_id,
                "TimeToNext_days": float(event_time) if occurred else np.nan,
                "Event_flag": int(occurred),
                "Censor_flag": int(not occurred),
                "Survival_duration": float(event_time) if occurred else float(censor_at),
            }
        )
    return pd.DataFrame(rows)


def small_trained_bundle(tmp_path):
    features = make_features(24)
    event_times = [
        10, 10.5, 23, 31, 45, 58, 67, 80, 90, 95, 120, None,
        8, 18, 28, 38, 48, 58, 68, 78, 88, None, None, None,
    ]
    outcomes = make_outcomes(features, event_times)
    train_features, val_features = features.iloc[:18].copy(), features.iloc[18:].copy()
    train_outcomes = outcomes.iloc[:18].copy()
    val_outcomes = outcomes.iloc[18:].copy()
    train_pp = pc.make_person_period_data(train_features, train_outcomes)
    val_pp = pc.make_person_period_data(val_features, val_outcomes)
    global_model = pc.fit_global_hazard(train_pp)
    segment_model = pc.fit_segment_hazard(train_pp, global_model)
    fit = pc.fit_personalized_hazard(
        train_pp,
        val_features,
        val_outcomes,
        c_candidates=(0.1, 1.0),
    )
    metadata = {
        "model_version": pc.MODEL_VERSION,
        "population_median_gap_days": 20.0,
    }
    bundle = {
        "global": global_model,
        "segment": segment_model,
        "personalized_pipeline": fit["pipeline"],
        "metadata": metadata,
    }
    return bundle, train_pp, val_features, val_outcomes


def test_event_at_day_23_contributes_three_rows():
    features = make_features(1)
    pp = pc.make_person_period_data(features, make_outcomes(features, [23.0]))
    assert len(pp) == 3
    assert pp[pc.INTERVAL_COL].tolist() == [1, 2, 3]
    assert pp[pc.EVENT_COL].tolist() == [0, 0, 1]


@pytest.mark.parametrize(
    ("event_time", "expected_bin"),
    [(10.0, 1), (10.5, 2), (90.0, 9)],
)
def test_boundary_events_are_assigned_to_expected_bin(event_time, expected_bin):
    features = make_features(1)
    pp = pc.make_person_period_data(features, make_outcomes(features, [event_time]))
    assert len(pp) == expected_bin
    assert pp.loc[pp[pc.EVENT_COL].eq(1), pc.INTERVAL_COL].tolist() == [expected_bin]


def test_event_after_day_90_is_not_an_event_in_the_forecast_horizon():
    features = make_features(1)
    pp = pc.make_person_period_data(features, make_outcomes(features, [90.01]))
    assert len(pp) == 9
    assert pp[pc.EVENT_COL].sum() == 0


def test_nonreturning_customer_contributes_nine_zero_event_rows():
    features = make_features(1)
    outcomes = make_outcomes(features, [None], censor_at=120.0)
    pp = pc.make_person_period_data(features, outcomes)
    assert len(pp) == 9
    assert pp[pc.EVENT_COL].sum() == 0


def test_each_customer_has_at_most_nine_rows_and_one_event():
    features = make_features(4)
    outcomes = make_outcomes(features, [23.0, 90.0, None, 100.0])
    pp = pc.make_person_period_data(features, outcomes)
    assert pp.groupby("Customer ID").size().max() <= 9
    assert pp.groupby("Customer ID")[pc.EVENT_COL].sum().max() <= 1


def test_event_and_censor_indicators_are_required_and_validated():
    features = make_features(1)
    outcomes = make_outcomes(features, [20.0]).drop(columns="Censor_flag")
    with pytest.raises(ValueError, match="Censor_flag"):
        pc.make_person_period_data(features, outcomes)
    outcomes["Censor_flag"] = 1
    with pytest.raises(ValueError, match="Exactly one"):
        pc.make_person_period_data(features, outcomes)


def test_missing_time_for_declared_event_is_rejected():
    features = make_features(1)
    outcomes = make_outcomes(features, [20.0])
    outcomes.loc[0, "TimeToNext_days"] = np.nan
    with pytest.raises(ValueError, match="times must be present"):
        pc.make_person_period_data(features, outcomes)


def test_hazards_are_probabilities():
    pp = pd.DataFrame(
        {
            "Customer ID": [1, 1, 2, 2],
            "interval_index": [1, 2, 1, 2],
            "event_in_interval": [0, 1, 0, 0],
        }
    )
    model = pc.fit_global_hazard(pp)
    assert len(model["hazards"]) == 9
    assert np.all((model["hazards"] >= 0) & (model["hazards"] <= 1))


def test_survival_is_nonincreasing_and_purchase_probability_nondecreasing():
    curves = pc.hazards_to_cumulative_probabilities(np.linspace(0.01, 0.5, 9))
    survival = curves[[f"survival_{day}d" for day in range(10, 91, 10)]].iloc[0]
    purchase = curves[[f"purchase_{day}d" for day in range(10, 91, 10)]].iloc[0]
    assert np.all(np.diff(survival) <= 0)
    assert np.all(np.diff(purchase) >= 0)


def test_p30_is_never_greater_than_p60_or_p90():
    curves = pc.hazards_to_cumulative_probabilities(np.full((4, 9), 0.2))
    assert (curves["purchase_30d"] <= curves["purchase_60d"]).all()
    assert (curves["purchase_60d"] <= curves["purchase_90d"]).all()


def test_customer_id_is_not_in_registered_predictors():
    predictors = set(pc.NUMERIC_FEATURES).union(pc.CATEGORICAL_FEATURES)
    assert "Customer ID" not in predictors
    assert "cutoff_date" not in predictors


def test_future_target_fields_are_not_in_registered_predictors():
    predictors = set(pc.NUMERIC_FEATURES).union(pc.CATEGORICAL_FEATURES)
    assert not predictors.intersection(pc.TARGET_COLUMNS)
    with pytest.raises(ValueError, match="cannot be model predictors"):
        pc._validate_model_schema(["Recency", "Purchased_90d"])


def test_preprocessing_is_fitted_on_train_only(tmp_path):
    bundle, train_pp, val_features, _ = small_trained_bundle(tmp_path)
    pipeline = bundle["personalized_pipeline"]
    train_medians = train_pp[list(pc.NUMERIC_FEATURES)].median().to_numpy()
    imputer = pipeline.named_steps["preprocess"].named_transformers_["numeric"].named_steps["imputer"]
    assert np.allclose(imputer.statistics_, train_medians, equal_nan=True)
    scaler = pipeline.named_steps["preprocess"].named_transformers_["numeric"].named_steps["scaler"]
    assert scaler.n_samples_seen_ == len(train_pp)
    assert len(val_features) > 0


def test_single_purchase_customer_gets_valid_predictions(tmp_path):
    bundle, _, val_features, _ = small_trained_bundle(tmp_path)
    one_purchase = val_features.iloc[[0]].copy()
    one_purchase["Frequency"] = 1.0
    one_purchase["Median_Gap_days"] = np.nan
    hazards = pc.predict_hazard_matrix(bundle, one_purchase)
    assert hazards.shape == (1, 9)
    assert np.isfinite(hazards).all()
    assert ((hazards >= 0) & (hazards <= 1)).all()


def test_prediction_export_has_no_future_labels_and_same_cutoff(tmp_path):
    bundle, _, val_features, _ = small_trained_bundle(tmp_path)
    predictions = pc.predict_purchase_clock(bundle, val_features)
    assert len(predictions) == len(val_features)
    assert not set(predictions.columns).intersection(pc.TARGET_COLUMNS)
    assert predictions["cutoff_date"].nunique() == 1
    assert predictions["forecast_horizons_days"].eq("30,60,90").all()


def test_prediction_export_has_all_three_coherent_horizons(tmp_path):
    bundle, _, val_features, _ = small_trained_bundle(tmp_path)
    predictions = pc.predict_purchase_clock(bundle, val_features)
    for prefix in ("global", "segment", "personalized"):
        assert (predictions[f"{prefix}_P30"] <= predictions[f"{prefix}_P60"]).all()
        assert (predictions[f"{prefix}_P60"] <= predictions[f"{prefix}_P90"]).all()


def test_model_reload_produces_identical_predictions(tmp_path):
    bundle, _, val_features, _ = small_trained_bundle(tmp_path)
    path = pc.save_purchase_clock_artifacts(bundle, tmp_path)
    reloaded = pc.load_purchase_clock_artifacts(tmp_path)
    assert path.exists()
    original = pc.predict_purchase_clock(bundle, val_features)
    restored = pc.predict_purchase_clock(reloaded, val_features)
    probability_columns = [column for column in original if "_P" in column]
    np.testing.assert_allclose(
        original[probability_columns].to_numpy(),
        restored[probability_columns].to_numpy(),
        rtol=0,
        atol=1e-12,
    )


def test_selection_api_uses_validation_but_has_no_test_parameter():
    parameters = inspect.signature(pc.fit_personalized_hazard).parameters
    assert "validation_features" in parameters
    assert "validation_outcomes" in parameters
    assert "test_features" not in parameters
    assert "test_outcomes" not in parameters


def test_prediction_count_matches_input_cohort(tmp_path):
    bundle, _, val_features, _ = small_trained_bundle(tmp_path)
    predictions = pc.predict_purchase_clock(bundle, val_features)
    assert predictions["Customer ID"].nunique() == val_features["Customer ID"].nunique()


def test_delay_ratio_uses_train_population_median_for_sparse_history():
    features = make_features(1)
    features.loc[0, "Frequency"] = 1
    features.loc[0, "Median_Gap_days"] = np.nan
    result = pc.calculate_delay_ratio(features, population_median_gap=20.0)
    assert result.loc[0, "regularized_expected_gap_days"] == pytest.approx(20.0)
    assert result.loc[0, "delay_ratio"] == pytest.approx(features.loc[0, "Recency"] / 20.0)


def test_median_return_interval_is_not_extrapolated_beyond_day_90():
    curves = pc.hazards_to_cumulative_probabilities(np.full((1, 9), 0.01))
    labels = pc._median_interval(curves)
    assert labels == ["Median return time not reached within the modeled 90-day horizon."]


def test_test_outcomes_are_not_required_or_used_for_selection_or_training(tmp_path):
    bundle, _, val_features, _ = small_trained_bundle(tmp_path)
    assert bundle["personalized_pipeline"] is not None
    assert "test_features" not in inspect.signature(pc.fit_personalized_hazard).parameters
    assert "test_outcomes" not in inspect.signature(pc.fit_personalized_hazard).parameters


def test_exactly_nine_inference_rows_per_customer():
    features = make_features(3)
    expanded = pc._expand_person_period_features(features)
    assert len(expanded) == 27
    assert expanded.groupby("Customer ID").size().eq(9).all()
