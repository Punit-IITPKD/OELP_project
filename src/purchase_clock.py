"""Leakage-conscious discrete-time purchase-clock models for Notebook 06.

The public inference API is :func:`predict_purchase_clock`. It accepts only
customer features available at a prediction cutoff and returns a customer-level
table with global, segment-aware, and personalized purchase probabilities.
Future outcomes are deliberately handled by the separate evaluation functions.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


MODEL_VERSION = "purchase-clock-v1"
CUSTOMER_ID = "Customer ID"
CUTOFF_COL = "cutoff_date"
INTERVAL_COL = "interval_index"
EVENT_COL = "event_in_interval"
EVENT_FLAG_COL = "Event_flag"
CENSOR_FLAG_COL = "Censor_flag"
EVENT_TIME_COL = "TimeToNext_days"
CENSOR_TIME_COL = "Survival_duration"
INTERVAL_DAYS = 10
N_INTERVALS = 9
HORIZONS = (30, 60, 90)
REGULARIZATION_CANDIDATES = (0.1, 1.0, 10.0)

NUMERIC_FEATURES = (
    "Recency",
    "Frequency",
    "Monetary_Gross",
    "AOV",
    "Tenure_obs_days",
    "PurchaseRate_per_obs_day",
    "SpendRate_per_obs_day",
    "Median_Gap_days",
    "Recent_Orders",
)
CATEGORICAL_FEATURES = ("Hist_Segment", INTERVAL_COL)
TARGET_COLUMNS = frozenset(
    {
        "NextPurchaseDate",
        EVENT_TIME_COL,
        EVENT_FLAG_COL,
        CENSOR_FLAG_COL,
        CENSOR_TIME_COL,
        "Purchased_30d",
        "Purchased_60d",
        "Purchased_90d",
        "FutureOrders_30d",
        "FutureOrders_60d",
        "FutureOrders_90d",
        "FutureRevenue_30d",
        "FutureRevenue_60d",
        "FutureRevenue_90d",
        "split_role",
        "horizon_days",
    }
)
FORBIDDEN_MODEL_FEATURES = frozenset({CUSTOMER_ID, CUTOFF_COL, "FirstPurchaseDate", "LastPurchaseDate"}) | TARGET_COLUMNS


@dataclass(frozen=True)
class PersonPeriodColumns:
    """Column mapping for the explicit event/censoring outcome contract."""

    customer_id: str = CUSTOMER_ID
    event_time: str = EVENT_TIME_COL
    event_flag: str = EVENT_FLAG_COL
    censor_flag: str = CENSOR_FLAG_COL
    censor_time: str = CENSOR_TIME_COL


def _require_columns(frame: pd.DataFrame, columns: Iterable[str], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def _validate_binary(values: pd.Series, name: str) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.isna().any() or not numeric.isin([0, 1]).all():
        raise ValueError(f"{name} must contain only explicit 0/1 values.")
    return numeric.astype(int)


def _validate_feature_table(
    customer_features: pd.DataFrame,
    *,
    require_cutoff: bool = True,
) -> pd.DataFrame:
    """Validate and normalize a customer feature table without using targets."""
    if not isinstance(customer_features, pd.DataFrame) or customer_features.empty:
        raise ValueError("customer_features must be a non-empty DataFrame.")
    required = [CUSTOMER_ID, *NUMERIC_FEATURES]
    if require_cutoff:
        required.append(CUTOFF_COL)
    _require_columns(customer_features, required, "customer_features")
    if "Hist_Segment" not in customer_features.columns:
        if "Hist_Cluster_id" not in customer_features.columns:
            raise ValueError("Historical segment is required as Hist_Segment or Hist_Cluster_id.")

    if customer_features[CUSTOMER_ID].isna().any():
        raise ValueError("Customer ID cannot be missing.")
    duplicate_key = [CUSTOMER_ID] + ([CUTOFF_COL] if require_cutoff else [])
    if customer_features.duplicated(duplicate_key).any():
        raise ValueError(f"Duplicate customer rows for key {duplicate_key}.")

    data = customer_features.copy()
    for column in NUMERIC_FEATURES:
        values = pd.to_numeric(data[column], errors="coerce")
        non_missing = values.dropna()
        if not np.isfinite(non_missing.to_numpy(dtype=float)).all():
            raise ValueError(f"{column} contains infinite values.")
        if (non_missing < 0).any():
            raise ValueError(f"{column} must be non-negative for the registered log1p transform.")
        data[column] = values

    if "Hist_Segment" not in data.columns:
        data["Hist_Segment"] = data["Hist_Cluster_id"].astype("string")
    data["Hist_Segment"] = data["Hist_Segment"].fillna("Unknown").astype(str)
    if require_cutoff:
        data[CUTOFF_COL] = pd.to_datetime(data[CUTOFF_COL], errors="raise")
    return data


def _validate_model_schema(columns: Sequence[str]) -> None:
    forbidden = sorted(set(columns).intersection(FORBIDDEN_MODEL_FEATURES))
    if forbidden:
        raise ValueError(f"Identifiers, dates, or outcomes cannot be model predictors: {forbidden}")


def _expand_person_period_features(customer_features: pd.DataFrame) -> pd.DataFrame:
    """Create the nine inference rows per customer, without outcome fields."""
    data = _validate_feature_table(customer_features)
    _validate_model_schema((*NUMERIC_FEATURES, *CATEGORICAL_FEATURES))
    expanded = data.loc[:, [CUSTOMER_ID, CUTOFF_COL, "Hist_Segment", *NUMERIC_FEATURES]].merge(
        pd.DataFrame({INTERVAL_COL: np.arange(1, N_INTERVALS + 1)}),
        how="cross",
    )
    expanded[INTERVAL_COL] = expanded[INTERVAL_COL].astype(str)
    return expanded


def make_person_period_data(
    customer_features: pd.DataFrame,
    outcomes: pd.DataFrame,
    *,
    columns: PersonPeriodColumns = PersonPeriodColumns(),
) -> pd.DataFrame:
    """Expand customers into discrete 10-day risk intervals.

    ``event_flag`` and ``censor_flag`` are required, explicit and mutually
    exclusive. Event times come from ``event_time``; censoring times come from
    ``censor_time``. A customer with an event after day 90 is observed to have
    no event in this forecast horizon and contributes nine zero-event rows.
    Censoring inside an interval contributes only fully observed earlier
    intervals; censoring exactly on a boundary includes that completed interval.
    """
    features = _validate_feature_table(customer_features)
    _require_columns(
        outcomes,
        [
            columns.customer_id,
            columns.event_time,
            columns.event_flag,
            columns.censor_flag,
            columns.censor_time,
        ],
        "outcomes",
    )
    if outcomes[columns.customer_id].isna().any() or outcomes[columns.customer_id].duplicated().any():
        raise ValueError("outcomes must have one non-missing row per customer.")

    event_flags = _validate_binary(outcomes[columns.event_flag], columns.event_flag)
    censor_flags = _validate_binary(outcomes[columns.censor_flag], columns.censor_flag)
    if (event_flags + censor_flags != 1).any():
        raise ValueError("Exactly one of event_flag or censor_flag must be 1 per customer.")

    outcome_data = outcomes.copy()
    outcome_data["_event_flag"] = event_flags.to_numpy()
    outcome_data["_censor_flag"] = censor_flags.to_numpy()
    outcome_data[columns.event_time] = pd.to_numeric(outcome_data[columns.event_time], errors="coerce")
    outcome_data[columns.censor_time] = pd.to_numeric(outcome_data[columns.censor_time], errors="coerce")
    event_missing = (outcome_data["_event_flag"].eq(1) & outcome_data[columns.event_time].isna())
    censor_missing = (outcome_data["_censor_flag"].eq(1) & outcome_data[columns.censor_time].isna())
    if event_missing.any() or censor_missing.any():
        raise ValueError("Event/censor times must be present for the corresponding explicit indicator.")

    outcome_data["_observed_time"] = np.where(
        outcome_data["_event_flag"].eq(1),
        outcome_data[columns.event_time],
        outcome_data[columns.censor_time],
    )
    observed_time = outcome_data["_observed_time"].astype(float)
    if not np.isfinite(observed_time.to_numpy()).all() or (observed_time < 0).any():
        raise ValueError("Observed event/censor times must be finite and non-negative.")
    if (outcome_data["_event_flag"].eq(1) & (observed_time <= 0)).any():
        raise ValueError("Observed event times must be strictly greater than zero.")

    outcome_indexed = outcome_data.set_index(columns.customer_id)
    feature_ids = set(features[CUSTOMER_ID])
    outcome_ids = set(outcome_indexed.index)
    if feature_ids != outcome_ids:
        raise ValueError(
            f"Feature/outcome customer sets differ (features={len(feature_ids)}, outcomes={len(outcome_ids)})."
        )

    records: list[dict[str, Any]] = []
    model_feature_columns = [CUSTOMER_ID, CUTOFF_COL, "Hist_Segment", *NUMERIC_FEATURES]
    for customer in features[model_feature_columns].to_dict("records"):
        outcome = outcome_indexed.loc[customer[CUSTOMER_ID]]
        is_event = int(outcome["_event_flag"])
        time = float(outcome["_observed_time"])
        within_horizon_event = bool(is_event and time <= N_INTERVALS * INTERVAL_DAYS)
        if within_horizon_event:
            stop_bin = min(int(math.ceil(time / INTERVAL_DAYS)), N_INTERVALS)
        else:
            stop_bin = min(int(math.floor(time / INTERVAL_DAYS)), N_INTERVALS)

        for interval in range(1, stop_bin + 1):
            row = dict(customer)
            row[INTERVAL_COL] = str(interval)
            row[EVENT_COL] = int(within_horizon_event and interval == stop_bin)
            records.append(row)
        if within_horizon_event and stop_bin == 0:
            raise ValueError("An event cannot occur at or before day zero.")

    result = pd.DataFrame(records)
    if result.empty:
        raise ValueError("No observable person-period rows were produced.")
    counts = result.groupby(CUSTOMER_ID, sort=False).size()
    event_counts = result.groupby(CUSTOMER_ID, sort=False)[EVENT_COL].sum()
    if counts.max() > N_INTERVALS or event_counts.max() > 1:
        raise AssertionError("Person-period expansion violated the nine-row/one-event invariant.")
    result[INTERVAL_COL] = result[INTERVAL_COL].astype(int)
    result[EVENT_COL] = result[EVENT_COL].astype(int)
    return result.reset_index(drop=True)


def _period_counts(person_period: pd.DataFrame, *, segment_col: str | None = None) -> pd.DataFrame:
    _require_columns(person_period, [INTERVAL_COL, EVENT_COL], "person_period")
    periods = person_period.copy()
    periods[INTERVAL_COL] = pd.to_numeric(periods[INTERVAL_COL], errors="raise").astype(int)
    periods[EVENT_COL] = _validate_binary(periods[EVENT_COL], EVENT_COL)
    if not periods[INTERVAL_COL].between(1, N_INTERVALS).all():
        raise ValueError("interval_index must be between 1 and 9.")
    grouped = [INTERVAL_COL] + ([segment_col] if segment_col else [])
    counts = (
        periods.groupby(grouped, dropna=False)[EVENT_COL]
        .agg(at_risk="size", events="sum")
        .reset_index()
    )
    return counts


def fit_global_hazard(training_person_period: pd.DataFrame) -> dict[str, Any]:
    """Estimate smoothed global interval hazards using the TRAIN rows only."""
    counts = _period_counts(training_person_period)
    counts = counts.set_index(INTERVAL_COL).reindex(range(1, N_INTERVALS + 1), fill_value=0)
    at_risk = counts["at_risk"].to_numpy(dtype=int)
    events = counts["events"].to_numpy(dtype=int)
    if np.any(events > at_risk):
        raise ValueError("An interval cannot contain more events than customers at risk.")
    hazards = (events + 1.0) / (at_risk + 2.0)
    return {
        "hazards": hazards,
        "at_risk": at_risk,
        "events": events,
        "smoothing": "Beta(1, 1) interval hazard prior",
        "training_customers": int(training_person_period[CUSTOMER_ID].nunique())
        if CUSTOMER_ID in training_person_period
        else None,
    }


def fit_segment_hazard(
    training_person_period: pd.DataFrame,
    global_model: Mapping[str, Any] | None = None,
    *,
    alpha: float = 20.0,
    min_at_risk: int | None = None,
    segment_col: str = "Hist_Cluster_id",
) -> dict[str, Any]:
    """Estimate segment interval hazards with shrinkage toward global hazards."""
    if alpha <= 0:
        raise ValueError("alpha must be positive.")
    if segment_col not in training_person_period.columns:
        segment_col = "Hist_Segment"
    _require_columns(training_person_period, [segment_col], "training_person_period")
    if global_model is None:
        global_model = fit_global_hazard(training_person_period)
    global_hazards = np.asarray(global_model["hazards"], dtype=float)
    if global_hazards.shape != (N_INTERVALS,):
        raise ValueError("global_model must contain exactly nine interval hazards.")

    counts = _period_counts(training_person_period, segment_col=segment_col)
    segments = sorted(training_person_period[segment_col].dropna().unique(), key=str)
    if min_at_risk is None:
        min_at_risk = int(alpha)
    models: dict[str, np.ndarray] = {}
    segment_counts: dict[str, dict[str, list[int]]] = {}
    for segment in segments:
        subset = counts[counts[segment_col] == segment].set_index(INTERVAL_COL)
        subset = subset.reindex(range(1, N_INTERVALS + 1), fill_value=0)
        at_risk = subset["at_risk"].to_numpy(dtype=int)
        events = subset["events"].to_numpy(dtype=int)
        if np.any(events > at_risk):
            raise ValueError(f"Segment {segment!r} has more events than customers at risk.")
        hazards = (events + alpha * global_hazards) / (at_risk + alpha)
        hazards[at_risk < min_at_risk] = global_hazards[at_risk < min_at_risk]
        key = str(segment)
        models[key] = hazards
        segment_counts[key] = {
            "at_risk": at_risk.tolist(),
            "events": events.tolist(),
        }
    return {
        "hazards_by_segment": models,
        "counts_by_segment": segment_counts,
        "global_hazards": global_hazards,
        "alpha": float(alpha),
        "min_at_risk": int(min_at_risk),
        "segment_column": segment_col,
    }


def _build_logistic_pipeline(c_value: float) -> Pipeline:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, list(NUMERIC_FEATURES)),
            ("categorical", categorical_pipeline, list(CATEGORICAL_FEATURES)),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                LogisticRegression(
                    C=float(c_value),
                    solver="lbfgs",
                    max_iter=2000,
                    class_weight=None,
                    random_state=42,
                ),
            ),
        ]
    )


def _model_matrix(person_period: pd.DataFrame) -> pd.DataFrame:
    _require_columns(person_period, [*NUMERIC_FEATURES, INTERVAL_COL], "person_period")
    data = person_period.copy()
    if "Hist_Segment" not in data.columns:
        _require_columns(data, ["Hist_Cluster_id"], "person_period")
        data["Hist_Segment"] = data["Hist_Cluster_id"].astype("string")
    data["Hist_Segment"] = data["Hist_Segment"].fillna("Unknown").astype(str)
    data[INTERVAL_COL] = data[INTERVAL_COL].astype(str)
    columns = [*NUMERIC_FEATURES, *CATEGORICAL_FEATURES]
    _validate_model_schema(columns)
    return data.loc[:, columns]


def fit_personalized_hazard(
    training_person_period: pd.DataFrame,
    validation_features: pd.DataFrame,
    validation_outcomes: pd.DataFrame,
    *,
    c_candidates: Sequence[float] = REGULARIZATION_CANDIDATES,
) -> dict[str, Any]:
    """Select L2 regularization on validation mean Brier across 30/60/90 days.

    The chosen pipeline is fitted on TRAIN only and is not refitted on VAL.
    TEST data must not be passed to this function.
    """
    if not c_candidates:
        raise ValueError("At least one regularization candidate is required.")
    _require_columns(training_person_period, [EVENT_COL], "training_person_period")
    y_train = _validate_binary(training_person_period[EVENT_COL], EVENT_COL).to_numpy()
    if len(np.unique(y_train)) < 2:
        raise ValueError("TRAIN person-period outcomes must contain both event classes.")

    candidates: list[dict[str, Any]] = []
    fitted: dict[float, Pipeline] = {}
    for c_value in c_candidates:
        pipeline = _build_logistic_pipeline(float(c_value))
        pipeline.fit(_model_matrix(training_person_period), y_train)
        hazards = predict_hazard_matrix(pipeline, validation_features)
        curves = hazards_to_cumulative_probabilities(hazards)
        val_predictions = _probability_frame(validation_features, curves, prefix="personalized")
        metrics, _ = evaluate_purchase_probabilities(
            val_predictions,
            validation_outcomes,
            model_columns={"Personalized": "personalized"},
        )
        brier_values = metrics["brier_score"].dropna()
        mean_brier = float(brier_values.mean()) if len(brier_values) else math.inf
        candidates.append(
            {
                "C": float(c_value),
                "mean_validation_brier_30_60_90": mean_brier,
                "validation_brier_30d": float(
                    metrics.loc[metrics["horizon_days"] == 30, "brier_score"].iloc[0]
                ),
            }
        )
        fitted[float(c_value)] = pipeline

    selection = pd.DataFrame(candidates).sort_values(
        ["mean_validation_brier_30_60_90", "C"], ascending=[True, True]
    ).reset_index(drop=True)
    chosen_c = float(selection.iloc[0]["C"])
    return {
        "pipeline": fitted[chosen_c],
        "selected_C": chosen_c,
        "selection_metrics": selection,
        "selection_rule": "Minimum mean validation Brier score across 30/60/90 days; tie-break toward lower C.",
        "training_rows": int(len(training_person_period)),
        "training_customers": int(training_person_period[CUSTOMER_ID].nunique())
        if CUSTOMER_ID in training_person_period
        else None,
    }


def predict_hazard_matrix(
    model: Pipeline | Mapping[str, Any],
    customer_features: pd.DataFrame,
) -> np.ndarray:
    """Predict all nine conditional hazards for every customer at one cutoff."""
    pipeline = model.get("personalized_pipeline") if isinstance(model, Mapping) else model
    if pipeline is None or not hasattr(pipeline, "predict_proba"):
        raise ValueError("A fitted personalized LogisticRegression pipeline is required.")
    expanded = _expand_person_period_features(customer_features)
    matrix = _model_matrix(expanded)
    probability = pipeline.predict_proba(matrix)[:, 1]
    hazards = probability.reshape(len(customer_features), N_INTERVALS)
    if not np.isfinite(hazards).all() or ((hazards < 0) | (hazards > 1)).any():
        raise ValueError("The fitted model produced hazards outside [0, 1].")
    return hazards


def hazards_to_cumulative_probabilities(hazards: np.ndarray | Sequence[float]) -> pd.DataFrame:
    """Convert nine conditional hazards to cumulative return and survival curves."""
    values = np.asarray(hazards, dtype=float)
    if values.ndim == 1:
        values = values.reshape(1, -1)
    if values.ndim != 2 or values.shape[1] != N_INTERVALS:
        raise ValueError(f"hazards must have shape (n, {N_INTERVALS}) or ({N_INTERVALS},).")
    if not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("All hazards must be finite probabilities in [0, 1].")
    survival = np.cumprod(1.0 - values, axis=1)
    purchase = 1.0 - survival
    data: dict[str, np.ndarray] = {}
    for interval in range(N_INTERVALS):
        day = (interval + 1) * INTERVAL_DAYS
        data[f"hazard_{day}d"] = values[:, interval]
        data[f"survival_{day}d"] = survival[:, interval]
        data[f"purchase_{day}d"] = purchase[:, interval]
    result = pd.DataFrame(data)
    probability_columns = [f"purchase_{day}d" for day in range(INTERVAL_DAYS, 91, INTERVAL_DAYS)]
    survival_columns = [f"survival_{day}d" for day in range(INTERVAL_DAYS, 91, INTERVAL_DAYS)]
    if ((result[probability_columns] < -1e-12) | (result[probability_columns] > 1 + 1e-12)).any().any():
        raise AssertionError("Cumulative probabilities left [0, 1].")
    if (result[probability_columns].diff(axis=1).iloc[:, 1:] < -1e-12).any().any():
        raise AssertionError("Cumulative purchase probabilities must be non-decreasing.")
    if (result[survival_columns].diff(axis=1).iloc[:, 1:] > 1e-12).any().any():
        raise AssertionError("Survival probabilities must be non-increasing.")
    return result


def _probability_frame(
    customer_features: pd.DataFrame,
    curves: pd.DataFrame,
    *,
    prefix: str,
) -> pd.DataFrame:
    result = customer_features[[CUSTOMER_ID]].reset_index(drop=True).copy()
    for horizon in HORIZONS:
        result[f"{prefix}_P{horizon}"] = curves[f"purchase_{horizon}d"].to_numpy()
    return result


def calculate_delay_ratio(
    customer_features: pd.DataFrame,
    population_median_gap: float,
) -> pd.DataFrame:
    """Calculate a regularized delay heuristic; it is not a churn probability."""
    if not np.isfinite(population_median_gap) or population_median_gap <= 0:
        raise ValueError("population_median_gap must be a finite positive TRAIN median.")
    data = _validate_feature_table(customer_features)
    n_gaps = (pd.to_numeric(data["Frequency"]) - 1).clip(lower=0)
    median_gap = pd.to_numeric(data["Median_Gap_days"], errors="coerce")
    valid_gap = median_gap.notna() & (n_gaps > 0)
    effective_gap = median_gap.where(valid_gap, float(population_median_gap))
    regularized = (n_gaps * effective_gap + 3.0 * population_median_gap) / (n_gaps + 3.0)
    recency = pd.to_numeric(data["Recency"], errors="coerce")
    ratio = recency / regularized
    return pd.DataFrame(
        {
            CUSTOMER_ID: data[CUSTOMER_ID].to_numpy(),
            "n_historical_gaps": n_gaps.to_numpy(),
            "regularized_expected_gap_days": regularized.to_numpy(),
            "delay_ratio": ratio.to_numpy(),
            "delay_interpretation": "Heuristic purchasing-delay ratio; not a calibrated churn probability.",
        }
    )


def _segment_key(row: pd.Series, segment_col: str) -> str:
    value = row.get(segment_col)
    if pd.isna(value):
        value = row.get("Hist_Segment", "Unknown")
    return str(value)


def _history_group(frequency: pd.Series) -> pd.Series:
    freq = pd.to_numeric(frequency, errors="coerce")
    return pd.Series(
        np.select(
            [freq.eq(1), freq.between(2, 4), freq.ge(5)],
            ["Exactly one purchase", "Two to four purchases", "Five or more purchases"],
            default="Unknown",
        ),
        index=frequency.index,
    )


def _median_interval(curves: pd.DataFrame) -> list[str]:
    labels = []
    for _, row in curves.iterrows():
        reached = next(
            (
                day
                for day in range(INTERVAL_DAYS, 91, INTERVAL_DAYS)
                if row[f"purchase_{day}d"] >= 0.5
            ),
            None,
        )
        labels.append(
            f"({reached - INTERVAL_DAYS}, {reached}] days" if reached else
            "Median return time not reached within the modeled 90-day horizon."
        )
    return labels


def predict_purchase_clock(
    model_bundle: Mapping[str, Any],
    customer_features: pd.DataFrame,
) -> pd.DataFrame:
    """Return inference-only purchase-clock predictions for the supplied cutoff.

    The output contains no observed future dates, targets, or evaluation labels.
    ``model_bundle`` is the object returned by ``load_purchase_clock_artifacts``.
    """
    features = _validate_feature_table(customer_features)
    _require_columns(features, ["Hist_Cluster_id"], "customer_features")
    bundle = model_bundle
    global_model = bundle["global"]
    segment_model = bundle["segment"]
    pipeline = bundle["personalized_pipeline"]
    pop_gap = float(bundle["metadata"]["population_median_gap_days"])

    global_hazards = np.asarray(global_model["hazards"], dtype=float)
    global_curve = hazards_to_cumulative_probabilities(
        np.repeat(global_hazards.reshape(1, -1), len(features), axis=0)
    )
    segment_col = segment_model.get("segment_column", "Hist_Cluster_id")
    segment_rows = []
    for _, row in features.iterrows():
        key = _segment_key(row, segment_col)
        hazard = np.asarray(
            segment_model["hazards_by_segment"].get(key, segment_model["global_hazards"]),
            dtype=float,
        )
        segment_rows.append(hazard)
    segment_curve = hazards_to_cumulative_probabilities(np.vstack(segment_rows))
    personalized_hazards = predict_hazard_matrix(pipeline, features)
    personalized_curve = hazards_to_cumulative_probabilities(personalized_hazards)

    output = features[
        [CUSTOMER_ID, CUTOFF_COL, "Hist_Cluster_id", "Hist_Segment", "Recency", "Frequency"]
    ].reset_index(drop=True).copy()
    output["history_group"] = _history_group(output["Frequency"])
    for prefix, curve in (
        ("global", global_curve),
        ("segment", segment_curve),
        ("personalized", personalized_curve),
    ):
        for horizon in HORIZONS:
            output[f"{prefix}_P{horizon}"] = curve[f"purchase_{horizon}d"].to_numpy()
    for day in range(INTERVAL_DAYS, 91, INTERVAL_DAYS):
        output[f"personalized_survival_{day}d"] = personalized_curve[
            f"survival_{day}d"
        ].to_numpy()
        output[f"personalized_purchase_{day}d"] = personalized_curve[
            f"purchase_{day}d"
        ].to_numpy()
    output["personalized_median_return_interval"] = _median_interval(personalized_curve)
    delay = calculate_delay_ratio(features, pop_gap)
    output = output.merge(
        delay[
            [
                CUSTOMER_ID,
                "n_historical_gaps",
                "regularized_expected_gap_days",
                "delay_ratio",
                "delay_interpretation",
            ]
        ],
        on=CUSTOMER_ID,
        how="left",
        validate="one_to_one",
    )
    output["history_sufficiency"] = output["history_group"]
    output["model_version"] = bundle["metadata"]["model_version"]
    output["forecast_horizons_days"] = "30,60,90"
    if set(output.columns).intersection(TARGET_COLUMNS):
        raise AssertionError("Production prediction output contains future target fields.")
    return output


def derive_horizon_outcomes(
    outcomes: pd.DataFrame,
    *,
    horizons: Sequence[int] = HORIZONS,
    customer_id_col: str = CUSTOMER_ID,
    event_time_col: str = EVENT_TIME_COL,
    event_flag_col: str = EVENT_FLAG_COL,
) -> pd.DataFrame:
    """Derive customer-level return indicators for 30/60/90-day evaluation."""
    _require_columns(outcomes, [customer_id_col, event_time_col, event_flag_col], "outcomes")
    if outcomes[customer_id_col].isna().any() or outcomes[customer_id_col].duplicated().any():
        raise ValueError("Evaluation outcomes must have one row per customer.")
    event_flag = _validate_binary(outcomes[event_flag_col], event_flag_col)
    event_time = pd.to_numeric(outcomes[event_time_col], errors="coerce")
    if (event_flag.eq(1) & event_time.isna()).any():
        raise ValueError("An observed event must have an event time.")
    result = pd.DataFrame({customer_id_col: outcomes[customer_id_col].to_numpy()})
    for horizon in horizons:
        if horizon <= 0:
            raise ValueError("Evaluation horizons must be positive.")
        result[f"Purchased_{horizon}d"] = (
            event_flag.eq(1) & event_time.le(float(horizon))
        ).astype(int).to_numpy()
    return result


def _calibration_table(
    y_true: np.ndarray,
    probability: np.ndarray,
    *,
    model: str,
    horizon: int,
    n_bins: int,
) -> pd.DataFrame:
    n = len(y_true)
    if n == 0:
        return pd.DataFrame()
    bin_count = min(int(n_bins), n)
    ranked_bins = pd.qcut(
        pd.Series(probability).rank(method="first"),
        q=bin_count,
        labels=False,
        duplicates="drop",
    )
    frame = pd.DataFrame(
        {
            "bin": ranked_bins.to_numpy(),
            "predicted_probability": probability,
            "observed_rate": y_true,
        }
    )
    table = (
        frame.groupby("bin", observed=True)
        .agg(
            n=("observed_rate", "size"),
            mean_predicted=("predicted_probability", "mean"),
            observed_rate=("observed_rate", "mean"),
        )
        .reset_index(drop=True)
    )
    table["model"] = model
    table["horizon_days"] = horizon
    table["calibration_error_component"] = (
        table["n"] / n * (table["mean_predicted"] - table["observed_rate"]).abs()
    )
    return table


def evaluate_purchase_probabilities(
    predictions: pd.DataFrame,
    outcomes: pd.DataFrame,
    *,
    model_columns: Mapping[str, str] | None = None,
    horizons: Sequence[int] = HORIZONS,
    n_bins: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate customer-level forecasts and return metrics plus reliability bins."""
    _require_columns(predictions, [CUSTOMER_ID], "predictions")
    _require_columns(outcomes, [CUSTOMER_ID], "outcomes")
    if model_columns is None:
        model_columns = {
            "Global": "global",
            "Segment-aware": "segment",
            "Personalized": "personalized",
        }
    actual = derive_horizon_outcomes(outcomes, horizons=horizons)
    if predictions[CUSTOMER_ID].duplicated().any() or actual[CUSTOMER_ID].duplicated().any():
        raise ValueError("Predictions and outcomes must each contain one row per customer.")
    joined = predictions.merge(
        actual,
        on=CUSTOMER_ID,
        how="inner",
        validate="one_to_one",
    )
    if len(joined) != len(predictions) or len(joined) != len(actual):
        raise ValueError("Predictions and outcomes must cover the exact same customer cohort.")

    metrics: list[dict[str, Any]] = []
    calibration: list[pd.DataFrame] = []
    for model_name, prefix in model_columns.items():
        for horizon in horizons:
            target_col = f"Purchased_{horizon}d"
            probability_col = f"{prefix}_P{horizon}"
            _require_columns(joined, [target_col, probability_col], "joined evaluation data")
            y = joined[target_col].to_numpy(dtype=int)
            p = np.clip(
                pd.to_numeric(joined[probability_col], errors="raise").to_numpy(dtype=float),
                1e-15,
                1 - 1e-15,
            )
            if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
                raise ValueError(f"{probability_col} must contain probabilities in [0, 1].")
            if len(np.unique(y)) < 2:
                auc = float("nan")
                average_precision = float("nan")
            else:
                auc = float(roc_auc_score(y, p))
                average_precision = float(average_precision_score(y, p))
            bins = _calibration_table(y, p, model=model_name, horizon=horizon, n_bins=n_bins)
            calibration.append(bins)
            metrics.append(
                {
                    "model": model_name,
                    "horizon_days": int(horizon),
                    "n_customers": int(len(y)),
                    "actual_purchase_rate": float(y.mean()),
                    "mean_predicted_probability": float(p.mean()),
                    "brier_score": float(brier_score_loss(y, p)),
                    "log_loss": float(log_loss(y, p, labels=[0, 1])),
                    "roc_auc": auc,
                    "average_precision": average_precision,
                    "calibration_error": float(bins["calibration_error_component"].sum()),
                }
            )
    return pd.DataFrame(metrics), pd.concat(calibration, ignore_index=True)


def performance_by_history_group(
    predictions: pd.DataFrame,
    outcomes: pd.DataFrame,
    *,
    model: str = "personalized",
    horizons: Sequence[int] = HORIZONS,
) -> pd.DataFrame:
    """Evaluate the personalized model by the three specified history groups."""
    target = derive_horizon_outcomes(outcomes, horizons=horizons)
    prefix = model.lower()
    joined = predictions.merge(target, on=CUSTOMER_ID, validate="one_to_one")
    if "history_group" not in joined:
        raise ValueError("Predictions must include history_group.")
    rows = []
    for group, frame in joined.groupby("history_group", dropna=False):
        for horizon in horizons:
            y = frame[f"Purchased_{horizon}d"].to_numpy(dtype=int)
            p = np.clip(frame[f"{prefix}_P{horizon}"].to_numpy(dtype=float), 1e-15, 1 - 1e-15)
            auc = (
                float(roc_auc_score(y, p))
                if len(np.unique(y)) > 1
                else float("nan")
            )
            rows.append(
                {
                    "history_group": group,
                    "horizon_days": int(horizon),
                    "n_customers": int(len(frame)),
                    "actual_purchase_rate": float(y.mean()),
                    "mean_predicted_probability": float(p.mean()),
                    "brier_score": float(brier_score_loss(y, p)),
                    "roc_auc": auc,
                }
            )
    return pd.DataFrame(rows)


def save_purchase_clock_artifacts(
    model_bundle: Mapping[str, Any],
    model_dir: str | Path,
) -> Path:
    """Persist fitted model objects and JSON metadata for notebook-free loading."""
    destination = Path(model_dir)
    destination.mkdir(parents=True, exist_ok=True)
    bundle_path = destination / "purchase_clock.joblib"
    temporary_bundle = destination / "purchase_clock.joblib.tmp"
    joblib.dump(dict(model_bundle), temporary_bundle)
    temporary_bundle.replace(bundle_path)
    metadata = dict(model_bundle["metadata"])
    metadata_path = destination / "metadata.json"
    temporary_metadata = destination / "metadata.json.tmp"
    temporary_metadata.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    temporary_metadata.replace(metadata_path)
    return bundle_path


def load_purchase_clock_artifacts(model_dir: str | Path) -> dict[str, Any]:
    """Load persisted models for inference without running Notebook 06."""
    source = Path(model_dir) / "purchase_clock.joblib"
    if not source.exists():
        raise FileNotFoundError(f"Purchase-clock model bundle not found: {source}")
    bundle = joblib.load(source)
    required = {"global", "segment", "personalized_pipeline", "metadata"}
    missing = required.difference(bundle)
    if missing:
        raise ValueError(f"Saved model bundle is missing required entries: {sorted(missing)}")
    if bundle["metadata"].get("model_version") != MODEL_VERSION:
        raise ValueError("Unsupported purchase-clock model version.")
    return bundle


def make_model_metadata(
    *,
    training_features: pd.DataFrame,
    training_person_period: pd.DataFrame,
    selected_c: float,
    cutoff_date: str,
    split_file: str,
    population_median_gap: float,
) -> dict[str, Any]:
    """Build JSON-safe metadata while keeping model parameters in joblib."""
    return {
        "model_version": MODEL_VERSION,
        "method": "Discrete-time purchase clock with 10-day logistic hazards",
        "forecast_horizons_days": list(HORIZONS),
        "interval_days": INTERVAL_DAYS,
        "n_intervals": N_INTERVALS,
        "training_cutoff": str(cutoff_date),
        "training_split_file": str(split_file),
        "training_customers": int(training_features[CUSTOMER_ID].nunique()),
        "training_person_period_rows": int(len(training_person_period)),
        "selected_regularization_C": float(selected_c),
        "population_median_gap_days": float(population_median_gap),
        "numeric_predictors": list(NUMERIC_FEATURES),
        "categorical_predictors": list(CATEGORICAL_FEATURES),
        "excluded_predictors": sorted(FORBIDDEN_MODEL_FEATURES),
        "training_only_preprocessing": True,
        "test_data_used_for_selection_or_training": False,
        "test_predictions_are_historical_not_real_time": True,
    }


def run_purchase_clock_tests() -> dict[str, str]:
    """Run a compact set of in-module mathematical smoke checks."""
    results: dict[str, str] = {}
    hazards = np.full((1, N_INTERVALS), 0.1)
    curves = hazards_to_cumulative_probabilities(hazards)
    p = curves[[f"purchase_{day}d" for day in range(10, 91, 10)]].iloc[0].to_numpy()
    s = curves[[f"survival_{day}d" for day in range(10, 91, 10)]].iloc[0].to_numpy()
    results["hazards_in_unit_interval"] = "PASS" if np.all((hazards >= 0) & (hazards <= 1)) else "FAIL"
    results["survival_nonincreasing"] = "PASS" if np.all(np.diff(s) <= 0) else "FAIL"
    results["purchase_probability_nondecreasing"] = "PASS" if np.all(np.diff(p) >= 0) else "FAIL"
    results["p30_le_p60_le_p90"] = "PASS" if p[2] <= p[5] <= p[8] else "FAIL"
    return results
