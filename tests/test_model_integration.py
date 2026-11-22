import numpy as np
import pandas as pd

from src import purchase_clock as pc
from src import spending_model as sm
from src import temporal_framework as tf


def _raw_features(count, cutoff, *, offset=0):
    rows = []
    for index in range(count):
        frequency = 1 + index % 6
        tenure = 30.0 + 7.0 * index
        gross = 40.0 + 18.0 * index + 11.0 * (index % 4)
        rows.append(
            {
                "Customer ID": offset + 1000 + index,
                "cutoff_date": pd.Timestamp(cutoff),
                "Recency": float(2 + (index * 13) % 105),
                "Frequency": float(frequency),
                "Monetary_Gross": gross,
                "AOV": gross / frequency,
                "Tenure_obs_days": tenure,
                "PurchaseRate_per_obs_day": frequency / tenure,
                "SpendRate_per_obs_day": gross / tenure,
                "Median_Gap_days": np.nan if frequency == 1 else float(9 + index % 35),
                "Recent_Orders": float(index % 5),
                "Recent_Revenue": float((index % 5) * 25),
            }
        )
    return pd.DataFrame(rows)


def _purchase_outcomes(features):
    rows = []
    for index, customer_id in enumerate(features["Customer ID"]):
        event = index % 5 != 0
        event_time = float(8 + (index % 9) * 10) if event else np.nan
        rows.append(
            {
                "Customer ID": customer_id,
                "TimeToNext_days": event_time,
                "Event_flag": int(event),
                "Censor_flag": int(not event),
                "Survival_duration": event_time if event else 90.0,
            }
        )
    return pd.DataFrame(rows)


def _spending_targets(features, horizon):
    rows = []
    for index, customer_id in enumerate(features["Customer ID"]):
        orders = int(index % 4 != 0)
        revenue = float(60 + (index % 11) * 23 + horizon * 0.4) if orders else 0.0
        rows.append(
            {
                "Customer ID": customer_id,
                f"FutureOrders_{horizon}d": orders,
                f"FutureRevenue_{horizon}d": revenue,
            }
        )
    return pd.DataFrame(rows)


def test_loaded_purchase_and_spending_artifacts_share_one_customer_snapshot(tmp_path):
    purchase_train_raw = _raw_features(36, "2010-03-01")
    purchase_val_raw = _raw_features(18, "2010-06-01", offset=2000)
    purchase_transform = tf.fit_historical_segmentation_transform(purchase_train_raw)
    purchase_train = tf.apply_historical_segmentation_transform(
        purchase_train_raw, purchase_transform
    )
    purchase_val = tf.apply_historical_segmentation_transform(
        purchase_val_raw, purchase_transform
    )
    train_outcomes = _purchase_outcomes(purchase_train)
    val_outcomes = _purchase_outcomes(purchase_val)
    train_person_period = pc.make_person_period_data(purchase_train, train_outcomes)
    global_model = pc.fit_global_hazard(train_person_period)
    segment_model = pc.fit_segment_hazard(train_person_period, global_model)
    selected = pc.fit_personalized_hazard(
        train_person_period,
        purchase_val,
        val_outcomes,
        c_candidates=(0.1, 1.0),
    )
    purchase_bundle = {
        "global": global_model,
        "segment": segment_model,
        "personalized_pipeline": selected["pipeline"],
        "segment_transform": purchase_transform,
        "metadata": {
            "model_version": pc.MODEL_VERSION,
            "population_median_gap_days": 20.0,
            "segmentation_transform": {
                "transform_version": purchase_transform["transform_version"],
                "fit_role": purchase_transform["fit_role"],
                "fit_cutoff": purchase_transform["fit_cutoff"],
            },
        },
    }
    purchase_dir = tmp_path / "purchase_clock"
    pc.save_purchase_clock_artifacts(purchase_bundle, purchase_dir)
    loaded_purchase = pc.load_purchase_clock_artifacts(purchase_dir)

    spending_train_raw = _raw_features(48, "2010-06-01", offset=3000)
    spending_val_raw = _raw_features(24, "2010-08-01", offset=5000)
    horizon_models = {}
    segment_transforms = {}
    for horizon in sm.HORIZONS:
        transform = tf.fit_historical_segmentation_transform(spending_train_raw)
        train_features = tf.apply_historical_segmentation_transform(
            spending_train_raw, transform
        )
        val_features = tf.apply_historical_segmentation_transform(
            spending_val_raw, transform
        )
        horizon_models[horizon] = sm.fit_horizon_models(
            train_features,
            _spending_targets(train_features, horizon),
            val_features,
            _spending_targets(val_features, horizon),
            horizon,
            alpha_candidates=(0.1, 1.0, 10.0),
        )
        segment_transforms[horizon] = transform

    spending_bundle = {
        "metadata": {"model_version": sm.MODEL_VERSION},
        "horizon_models": horizon_models,
        "segment_transforms": segment_transforms,
    }
    spending_dir = tmp_path / "spending_model"
    sm.save_spending_artifacts(spending_bundle, spending_dir)
    loaded_spending = sm.load_spending_artifacts(spending_dir)

    snapshot = _raw_features(12, "2010-09-10", offset=9000)
    purchase_predictions = pc.predict_purchase_clock(loaded_purchase, snapshot)
    expected_purchase_segments = tf.apply_historical_segmentation_transform(
        snapshot, loaded_purchase["segment_transform"]
    )
    assert purchase_predictions["Customer ID"].tolist() == snapshot["Customer ID"].tolist()
    assert purchase_predictions["cutoff_date"].tolist() == snapshot["cutoff_date"].tolist()
    assert purchase_predictions["Hist_Cluster_id"].tolist() == expected_purchase_segments[
        "Hist_Cluster_id"
    ].tolist()

    for horizon in sm.HORIZONS:
        horizon_segments = sm.apply_spending_segmentation(
            loaded_spending, snapshot, horizon
        )
        assert horizon_segments["Customer ID"].tolist() == snapshot["Customer ID"].tolist()
        assert horizon_segments["cutoff_date"].tolist() == snapshot["cutoff_date"].tolist()

    forecasts = sm.predict_expected_revenue(
        loaded_spending, snapshot, purchase_predictions
    )
    assert forecasts[["Customer ID", "cutoff_date"]].equals(
        snapshot[["Customer ID", "cutoff_date"]].reset_index(drop=True)
    )
    for horizon in sm.HORIZONS:
        np.testing.assert_allclose(
            forecasts[f"purchase_probability_{horizon}d"],
            purchase_predictions[f"personalized_P{horizon}"],
        )
        assert (
            forecasts[f"purchase_probability_{horizon}d"].between(0, 1).all()
        )
    assert (
        forecasts["purchase_probability_30d"]
        <= forecasts["purchase_probability_60d"]
    ).all()
    assert (
        forecasts["purchase_probability_60d"]
        <= forecasts["purchase_probability_90d"]
    ).all()
    assert not any(column.startswith("Future") for column in forecasts.columns)
