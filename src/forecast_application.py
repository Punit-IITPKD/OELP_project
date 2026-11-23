"""Cached application-level assembly for validated historical forecasts."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src import purchase_clock as pc
from src import spending_model as sm
from src import temporal_framework as tf
from src.customer_intelligence import CustomerIntelligence

CUSTOMER_ID = "Customer ID"
CUTOFF_DATE = "cutoff_date"
DEFAULT_CUTOFF = "2010-09-10"
DEFAULT_HORIZONS = (30, 60, 90)


def build_forecast_snapshot(
    transactions: pd.DataFrame,
    orders: pd.DataFrame,
    segments: pd.DataFrame,
    intelligence: CustomerIntelligence,
    cutoff_date: str = DEFAULT_CUTOFF,
) -> pd.DataFrame:
    """Build one validated, ID-aligned snapshot from saved model artifacts."""
    cutoff = pd.Timestamp(cutoff_date)
    features = tf.compute_historical_features(orders, cutoff)
    if features.empty:
        raise ValueError(f"No eligible customers exist before {cutoff.date()}.")

    predictions = intelligence.predict_customers(
        transactions,
        cutoff,
        horizons=DEFAULT_HORIZONS,
    )
    model_features = features.loc[:, list(sm.BASE_FEATURE_COLUMNS)].reset_index(
        drop=True
    )
    purchase_clock = pc.predict_purchase_clock(
        intelligence.purchase_bundle,
        model_features,
    )

    keys = [CUSTOMER_ID, CUTOFF_DATE]
    if predictions.duplicated(keys).any() or purchase_clock.duplicated(keys).any():
        raise AssertionError("Inference produced duplicate customer/cutoff rows.")

    snapshot = features.merge(
        predictions,
        on=keys,
        how="inner",
        validate="one_to_one",
        suffixes=("", "_prediction"),
    )
    snapshot = snapshot.merge(
        purchase_clock,
        on=keys,
        how="inner",
        validate="one_to_one",
        suffixes=("", "_clock"),
    )
    if len(snapshot) != len(features) or len(snapshot) != len(predictions):
        raise AssertionError("Feature and prediction cohorts do not align.")

    for horizon in DEFAULT_HORIZONS:
        probability_column = f"purchase_probability_{horizon}d"
        clock_column = f"personalized_P{horizon}"
        if not np.allclose(
            snapshot[probability_column].to_numpy(dtype=float),
            snapshot[clock_column].to_numpy(dtype=float),
            rtol=1e-10,
            atol=1e-12,
        ):
            raise AssertionError(
                f"Customer Intelligence and purchase-clock P{horizon} disagree."
            )

    descriptive_names = segments.set_index(CUSTOMER_ID)["Segment_Name"]
    snapshot["Descriptive_Segment"] = (
        snapshot[CUSTOMER_ID].map(descriptive_names).fillna("Not classified")
    )
    snapshot[CUTOFF_DATE] = pd.to_datetime(snapshot[CUTOFF_DATE])

    if not snapshot[CUTOFF_DATE].eq(cutoff).all():
        raise AssertionError("The forecast snapshot contains a mismatched cutoff.")
    if not (snapshot["LastPurchaseDate"] < cutoff).all():
        raise AssertionError("A forecast feature includes a purchase on/after cutoff.")
    if set(snapshot.columns).intersection(pc.TARGET_COLUMNS):
        raise AssertionError("Forecast snapshot contains future outcomes or labels.")
    if len(snapshot) != snapshot[CUSTOMER_ID].nunique():
        raise AssertionError("Forecast snapshot contains duplicate customers.")

    for horizon in DEFAULT_HORIZONS:
        values = snapshot[f"purchase_probability_{horizon}d"]
        if not values.between(0, 1).all():
            raise AssertionError(f"Invalid purchase probabilities for {horizon} days.")
    if not (
        snapshot["purchase_probability_30d"]
        <= snapshot["purchase_probability_60d"] + 1e-12
    ).all():
        raise AssertionError("P30 must not exceed P60.")
    if not (
        snapshot["purchase_probability_60d"]
        <= snapshot["purchase_probability_90d"] + 1e-12
    ).all():
        raise AssertionError("P60 must not exceed P90.")
    return snapshot.sort_values(CUSTOMER_ID).reset_index(drop=True)
