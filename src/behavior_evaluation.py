"""Validation-only model selection helpers for Notebook 08."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.behavior_monitor import evaluate_binary_risk, probability_metrics

REGULARIZATION_CANDIDATES = (0.1, 1.0, 10.0)
BEHAVIOR_FEATURE_FAMILIES = {
    "personalized_gap": ("gap_deviation_score",),
    "frequency_change": (
        "purchase_rate_ratio",
        "purchase_rate_change_per_day",
        "raw_purchase_rate_ratio",
    ),
    "spending_change": (
        "revenue_rate_ratio",
        "revenue_rate_change_per_day",
    ),
    "trajectory_change": ("ewma_gap_change_days",),
}
BEHAVIOR_MODEL_FEATURES = tuple(
    column
    for columns in BEHAVIOR_FEATURE_FAMILIES.values()
    for column in columns
)


@dataclass(frozen=True)
class SelectedBehaviorModel:
    """A TRAIN-fitted estimator selected using validation metrics only."""

    estimator: Pipeline
    feature_columns: tuple[str, ...]
    regularization_c: float
    validation_metrics: dict[str, float | int]
    validation_probability_metrics: dict[str, float]


def _validate_xy(
    features: pd.DataFrame,
    outcomes: pd.Series | np.ndarray,
    *,
    name: str,
) -> tuple[pd.DataFrame, np.ndarray]:
    if not isinstance(features, pd.DataFrame) or features.empty:
        raise ValueError(f"{name} features must be a non-empty DataFrame.")
    y = np.asarray(outcomes, dtype=int)
    if y.ndim != 1 or len(y) != len(features) or not np.isin(y, (0, 1)).all():
        raise ValueError(f"{name} outcomes must be aligned binary values.")
    if np.unique(y).size != 2:
        raise ValueError(f"{name} requires both outcome classes.")
    data = features.apply(pd.to_numeric, errors="coerce")
    data = data.replace([np.inf, -np.inf], np.nan)
    return data, y


def _pipeline(c_value: float) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "impute",
                SimpleImputer(strategy="median", add_indicator=True),
            ),
            ("scale", StandardScaler()),
            (
                "logistic",
                LogisticRegression(
                    C=float(c_value),
                    penalty="l2",
                    solver="liblinear",
                    max_iter=2_000,
                    random_state=42,
                ),
            ),
        ]
    )


def select_behavior_model(
    train_features: pd.DataFrame,
    train_outcomes: pd.Series | np.ndarray,
    validation_features: pd.DataFrame,
    validation_outcomes: pd.Series | np.ndarray,
    feature_columns: Iterable[str],
    *,
    regularization_candidates: Iterable[float] = REGULARIZATION_CANDIDATES,
) -> SelectedBehaviorModel:
    """Fit candidates on TRAIN and select C on VAL by AP, then Brier score.

    TEST data and labels are not accepted by this function by design. Features
    that are entirely missing in TRAIN are omitted before fitting.
    """
    train, y_train = _validate_xy(train_features, train_outcomes, name="TRAIN")
    validation, y_validation = _validate_xy(
        validation_features, validation_outcomes, name="VAL"
    )
    requested = tuple(feature_columns)
    missing_train = [column for column in requested if column not in train]
    missing_validation = [column for column in requested if column not in validation]
    if missing_train or missing_validation:
        raise ValueError(
            f"Candidate feature columns are missing: TRAIN={missing_train}, "
            f"VAL={missing_validation}"
        )
    active_columns = tuple(
        column for column in requested if train[column].notna().any()
    )
    if not active_columns:
        raise ValueError("No requested behavior features are observed in TRAIN.")
    train = train.loc[:, active_columns]
    validation = validation.loc[:, active_columns]

    candidates: list[tuple[float, float, float, Pipeline, dict, dict]] = []
    values = tuple(float(value) for value in regularization_candidates)
    if not values or any(not np.isfinite(value) or value <= 0 for value in values):
        raise ValueError("regularization_candidates must contain positive finite C values.")
    for c_value in values:
        estimator = _pipeline(c_value)
        estimator.fit(train, y_train)
        validation_probability = estimator.predict_proba(validation)[:, 1]
        ranking = evaluate_binary_risk(y_validation, validation_probability)
        probability = probability_metrics(y_validation, validation_probability)
        candidates.append(
            (
                -float(ranking["average_precision"]),
                float(probability["brier_score"]),
                c_value,
                estimator,
                ranking,
                probability,
            )
        )
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    _, _, selected_c, selected_model, ranking, probability = candidates[0]
    return SelectedBehaviorModel(
        estimator=selected_model,
        feature_columns=active_columns,
        regularization_c=float(selected_c),
        validation_metrics=ranking,
        validation_probability_metrics=probability,
    )


def predict_nonpurchase_probability(
    selected_model: SelectedBehaviorModel,
    features: pd.DataFrame,
) -> np.ndarray:
    """Score behavior rows with the selected TRAIN-fitted estimator."""
    missing = [
        column
        for column in selected_model.feature_columns
        if column not in features
    ]
    if missing:
        raise ValueError(f"Prediction features are missing columns: {missing}")
    matrix = (
        features.loc[:, selected_model.feature_columns]
        .apply(pd.to_numeric, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
    )
    probabilities = selected_model.estimator.predict_proba(matrix)[:, 1]
    if not np.isfinite(probabilities).all() or (
        (probabilities < 0) | (probabilities > 1)
    ).any():
        raise ValueError("Behavior model returned invalid nonpurchase probabilities.")
    return probabilities
