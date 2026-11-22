from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.config import (
    PREDICTION_CUTOFF,
    PREDICTION_HORIZONS,
    PROCESSED_DIR,
    PROJECT_ROOT,
)
from src.customer_intelligence import CustomerIntelligence
from src.forecast_application import build_forecast_snapshot

CUSTOMER_ID = "Customer ID"
CUTOFF_DATE = "cutoff_date"
ALL_ELIGIBLE_CUSTOMERS = "All eligible customers"


def filter_forecast_cohort(
    snapshot: pd.DataFrame,
    segment: str | None = None,
) -> pd.DataFrame:
    """Filter forecasts only by the saved model's pre-cutoff segment labels."""
    if "Hist_Segment" not in snapshot:
        raise ValueError("Forecast snapshot is missing its historical segment labels.")
    if segment is None or segment == ALL_ELIGIBLE_CUSTOMERS:
        return snapshot.copy()
    if segment not in set(snapshot["Hist_Segment"].dropna().unique()):
        return snapshot.iloc[0:0].copy()
    return snapshot.loc[snapshot["Hist_Segment"].eq(segment)].copy()


def summarize_forecast_cohort(
    snapshot: pd.DataFrame,
    segment: str | None = None,
) -> dict[str, object]:
    """Return the filtered customers and reconciled probability/revenue totals."""
    cohort = filter_forecast_cohort(snapshot, segment)
    required = [
        column
        for horizon in PREDICTION_HORIZONS
        for column in (
            f"purchase_probability_{horizon}d",
            f"personalized_expected_revenue_{horizon}d",
        )
        if column not in cohort
    ]
    if required:
        raise ValueError(f"Forecast snapshot is missing required fields: {required}")
    return {
        "cohort": cohort,
        "eligible_customer_count": int(cohort[CUSTOMER_ID].nunique()),
        "expected_returners": {
            horizon: float(cohort[f"purchase_probability_{horizon}d"].sum())
            for horizon in PREDICTION_HORIZONS
        },
        "expected_revenue": {
            horizon: float(
                cohort[f"personalized_expected_revenue_{horizon}d"].sum()
            )
            for horizon in PREDICTION_HORIZONS
        },
    }


def lookup_customer_record(
    snapshot: pd.DataFrame,
    customer_id_input: str | int | None,
) -> pd.Series | None:
    """Find one eligible customer by whole-number ID, without a default selection."""
    if customer_id_input is None:
        return None
    text = str(customer_id_input).strip()
    if not text.isdecimal():
        return None
    customer_id = int(text)
    match = snapshot.loc[snapshot[CUSTOMER_ID].eq(customer_id)]
    return None if match.empty else match.iloc[0]


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
