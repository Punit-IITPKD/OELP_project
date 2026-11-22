from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from app.config import (
    PREDICTION_CUTOFF,
    PREDICTION_HORIZONS,
    PROCESSED_DIR,
    PROJECT_ROOT,
)
from src import purchase_clock as pc
from src import spending_model as sm
from src import temporal_framework as tf
from src.customer_intelligence import CustomerIntelligence

CUSTOMER_ID = "Customer ID"
CUTOFF_DATE = "cutoff_date"


def _require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Required project data was not found: {path}")
    return path


@st.cache_resource(show_spinner=False)
def load_customer_intelligence() -> CustomerIntelligence:
    """Load the saved model artifacts once for this Streamlit process."""
    return CustomerIntelligence.from_artifacts(PROJECT_ROOT)


@st.cache_data(show_spinner="Loading the historical retail dataset…")
def load_transactions() -> pd.DataFrame:
    path = _require_file(PROCESSED_DIR / "online_retail_cleaned_data.csv")
    return pd.read_csv(path, parse_dates=["InvoiceDate"])


@st.cache_data(show_spinner=False)
def load_order_history() -> pd.DataFrame:
    path = _require_file(PROCESSED_DIR / "temporal" / "orders.csv")
    orders = pd.read_csv(path, parse_dates=["PurchaseDate"])
    if orders["PurchaseDate"].isna().any():
        raise ValueError("The saved order history contains invalid purchase dates.")
    return orders


@st.cache_data(show_spinner=False)
def load_descriptive_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_path = _require_file(PROCESSED_DIR / "customer_features.csv")
    segment_path = _require_file(PROCESSED_DIR / "customer_segments.csv")
    features = pd.read_csv(feature_path)
    segments = pd.read_csv(segment_path)
    for frame in (features, segments):
        frame[CUSTOMER_ID] = pd.to_numeric(
            frame[CUSTOMER_ID], errors="raise"
        ).astype("int64")
    return features, segments


def build_forecast_snapshot(
    transactions: pd.DataFrame,
    orders: pd.DataFrame,
    segments: pd.DataFrame,
    intelligence: CustomerIntelligence,
    cutoff_date: str = PREDICTION_CUTOFF,
) -> pd.DataFrame:
    """Build one validated, ID-aligned historical inference snapshot."""
    cutoff = pd.Timestamp(cutoff_date)
    features = tf.compute_historical_features(orders, cutoff)
    if features.empty:
        raise ValueError(f"No eligible customers exist before {cutoff.date()}.")

    predictions = intelligence.predict_customers(
        transactions,
        cutoff,
        horizons=PREDICTION_HORIZONS,
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

    # Merge on explicit customer/cutoff keys; never rely on row order.
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

    for horizon in PREDICTION_HORIZONS:
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
    snapshot["cutoff_date"] = pd.to_datetime(snapshot["cutoff_date"])

    if not snapshot["cutoff_date"].eq(cutoff).all():
        raise AssertionError("The forecast snapshot contains a mismatched cutoff.")
    if not (snapshot["LastPurchaseDate"] < cutoff).all():
        raise AssertionError("A forecast feature includes a purchase on/after cutoff.")
    if set(snapshot.columns).intersection(pc.TARGET_COLUMNS):
        raise AssertionError("Forecast snapshot contains future outcomes or labels.")
    if len(snapshot) != snapshot[CUSTOMER_ID].nunique():
        raise AssertionError("Forecast snapshot contains duplicate customers.")

    for horizon in PREDICTION_HORIZONS:
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


@st.cache_data(show_spinner="Preparing the September 10 historical forecast…")
def load_forecast_snapshot(
    cutoff_date: str = PREDICTION_CUTOFF,
) -> pd.DataFrame:
    transactions = load_transactions()
    orders = load_order_history()
    _, segments = load_descriptive_tables()
    intelligence = load_customer_intelligence()
    return build_forecast_snapshot(
        transactions,
        orders,
        segments,
        intelligence,
        cutoff_date,
    )
