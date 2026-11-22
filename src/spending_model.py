"""Leakage-aware future spending forecasts for Notebook 07.

The module estimates total gross revenue from every valid order in a forecast
horizon. Conditional-spending models are fitted only to TRAIN customers who
made at least one purchase in that horizon. Validation and test purchase
probabilities are supplied separately and are joined by customer and cutoff;
they are never learned from spending outcomes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


MODEL_VERSION = "spending-forecast-v1"
CUSTOMER_ID = "Customer ID"
CUTOFF_COL = "cutoff_date"
HORIZONS = (30, 60, 90)

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
    "Recent_Revenue",
)
CATEGORICAL_FEATURES = ("Hist_Segment",)
FEATURE_COLUMNS = (
    CUSTOMER_ID,
    CUTOFF_COL,
    *NUMERIC_FEATURES,
    *CATEGORICAL_FEATURES,
    "Hist_Cluster_id",
)
FORBIDDEN_FEATURES = frozenset(
    {
        "NextPurchaseDate",
        "TimeToNext_days",
        "Event_flag",
        "Censor_flag",
        "Survival_duration",
        "split_role",
        "horizon_days",
        *(f"Purchased_{h}d" for h in HORIZONS),
        *(f"FutureOrders_{h}d" for h in HORIZONS),
        *(f"FutureRevenue_{h}d" for h in HORIZONS),
    }
)
DEFAULT_ALPHA_CANDIDATES = (0.1, 1.0, 10.0, 100.0)


class TrainQuantileClipper(BaseEstimator, TransformerMixin):
    """Clip transformed numeric predictors to quantiles learned on TRAIN only."""

    def __init__(self, lower_quantile: float = 0.01, upper_quantile: float = 0.99):
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    def fit(self, values: np.ndarray, y: Any = None) -> "TrainQuantileClipper":
        array = np.asarray(values, dtype=float)
        if array.ndim != 2 or array.shape[0] == 0:
            raise ValueError("TrainQuantileClipper expects a non-empty 2D matrix.")
        if not 0.0 <= self.lower_quantile < self.upper_quantile <= 1.0:
            raise ValueError("Clipping quantiles must satisfy 0 <= lower < upper <= 1.")
        self.lower_bounds_ = np.quantile(array, self.lower_quantile, axis=0)
        self.upper_bounds_ = np.quantile(array, self.upper_quantile, axis=0)
        return self

    def transform(self, values: np.ndarray) -> np.ndarray:
        if not hasattr(self, "lower_bounds_"):
            raise ValueError("TrainQuantileClipper must be fitted before transform.")
        array = np.asarray(values, dtype=float)
        return np.clip(array, self.lower_bounds_, self.upper_bounds_)


def _require_columns(frame: pd.DataFrame, columns: Iterable[str], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def validate_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate and return only cutoff-time predictors."""
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError("customer_features must be a non-empty DataFrame.")
    leaked = sorted(set(frame.columns).intersection(FORBIDDEN_FEATURES))
    if leaked:
        raise ValueError(f"Future outcomes or split labels cannot be predictors: {leaked}")
    _require_columns(frame, FEATURE_COLUMNS, "customer_features")
    data = frame.loc[:, FEATURE_COLUMNS].copy()
    if data[CUSTOMER_ID].isna().any():
        raise ValueError("Customer ID cannot be missing.")
    data[CUTOFF_COL] = pd.to_datetime(data[CUTOFF_COL], errors="raise")
    if data.duplicated([CUSTOMER_ID, CUTOFF_COL]).any():
        raise ValueError("Customer features must be unique by Customer ID and cutoff_date.")
    for column in NUMERIC_FEATURES:
        data[column] = pd.to_numeric(data[column], errors="coerce")
        values = data[column].dropna().to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"{column} contains non-finite values.")
    for column in ("Frequency", "Monetary_Gross", "Tenure_obs_days"):
        values = data[column].dropna()
        if (values < 0).any():
            raise ValueError(f"{column} must be non-negative.")
    if data["Tenure_obs_days"].isna().any() or (data["Tenure_obs_days"] <= 0).any():
        raise ValueError("Tenure_obs_days must be finite and positive.")
    data["Hist_Segment"] = data["Hist_Segment"].fillna("Unknown").astype(str)
    return data


def _validate_targets(
    features: pd.DataFrame,
    targets: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:
    if horizon not in HORIZONS:
        raise ValueError(f"Unsupported forecast horizon: {horizon}")
    revenue_col = f"FutureRevenue_{horizon}d"
    orders_col = f"FutureOrders_{horizon}d"
    _require_columns(targets, [CUSTOMER_ID, revenue_col, orders_col], "targets")
    if targets[CUSTOMER_ID].isna().any() or targets[CUSTOMER_ID].duplicated().any():
        raise ValueError("Targets must contain one non-missing row per customer.")
    left_ids = set(features[CUSTOMER_ID])
    right_ids = set(targets[CUSTOMER_ID])
    if left_ids != right_ids:
        raise ValueError("Feature and target customer cohorts do not match exactly.")
    aligned = features[[CUSTOMER_ID]].merge(
        targets[[CUSTOMER_ID, revenue_col, orders_col]],
        on=CUSTOMER_ID,
        how="left",
        validate="one_to_one",
        sort=False,
    )
    revenue = pd.to_numeric(aligned[revenue_col], errors="coerce")
    order_count = pd.to_numeric(aligned[orders_col], errors="coerce")
    if revenue.isna().any() or order_count.isna().any():
        raise ValueError("Future revenue and order counts must be observed for the full horizon.")
    if not np.isfinite(revenue.to_numpy(dtype=float)).all():
        raise ValueError("Future revenue contains non-finite values.")
    if (revenue < 0).any() or (order_count < 0).any():
        raise ValueError("Gross future revenue and order counts cannot be negative.")
    if not np.equal(order_count, np.floor(order_count)).all():
        raise ValueError("Future order counts must be whole numbers.")
    aligned[revenue_col] = revenue.astype(float)
    aligned[orders_col] = order_count.astype(int)
    return aligned


def _purchaser_mask(targets: pd.DataFrame, horizon: int) -> np.ndarray:
    return targets[f"FutureOrders_{horizon}d"].to_numpy(dtype=int) > 0


def _numeric_matrix(features: pd.DataFrame) -> pd.DataFrame:
    return features.loc[:, NUMERIC_FEATURES]


def _build_ridge_pipeline(alpha: float) -> Pipeline:
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("log1p", FunctionTransformer(np.log1p)),
            ("train_quantile_clipper", TrainQuantileClipper(0.01, 0.99)),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    preprocess = ColumnTransformer(
        transformers=[
            ("numeric", numeric, list(NUMERIC_FEATURES)),
            ("categorical", categorical, list(CATEGORICAL_FEATURES)),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("ridge", Ridge(alpha=float(alpha))),
        ]
    )


def _smearing_factor(
    pipeline: Pipeline,
    features: pd.DataFrame,
    log_target: np.ndarray,
    *,
    random_state: int = 42,
) -> float:
    """Estimate Duan's factor from out-of-fold TRAIN-only log residuals."""
    if len(log_target) < 2:
        fitted = pipeline.predict(features)
        residuals = log_target - fitted
    else:
        n_splits = min(5, len(log_target))
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        oof = cross_val_predict(
            _build_ridge_pipeline(pipeline.named_steps["ridge"].alpha),
            features,
            log_target,
            cv=cv,
            method="predict",
        )
        residuals = log_target - oof
    factor = float(np.exp(np.clip(residuals, -20.0, 20.0)).mean())
    if not np.isfinite(factor) or factor <= 0:
        raise ValueError("Training-derived smearing factor must be finite and positive.")
    return factor


def _inverse_log_mean(log_prediction: np.ndarray, smearing_factor: float) -> np.ndarray:
    prediction = np.exp(np.clip(np.asarray(log_prediction, dtype=float), -30.0, 30.0))
    amounts = prediction * float(smearing_factor) - 1.0
    return np.clip(np.nan_to_num(amounts, nan=0.0, posinf=1e15, neginf=0.0), 0.0, 1e15)


def _conditional_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | int]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if len(actual) == 0:
        return {"n_purchasers": 0, "mae": np.nan, "rmse": np.nan, "bias": np.nan, "wape": np.nan}
    errors = predicted - actual
    return {
        "n_purchasers": int(len(actual)),
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(np.square(errors)))),
        "bias": float(np.mean(errors)),
        "wape": float(np.sum(np.abs(errors)) / np.sum(np.abs(actual)))
        if np.sum(np.abs(actual)) > 0
        else np.nan,
    }


def _expected_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | int]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    errors = predicted - actual
    total_actual = float(actual.sum())
    total_predicted = float(predicted.sum())
    return {
        "n_customers": int(len(actual)),
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(np.square(errors)))),
        "mean_forecast_bias": float(np.mean(errors)),
        "total_predicted_revenue": total_predicted,
        "total_actual_revenue": total_actual,
        "total_revenue_bias": total_predicted - total_actual,
        "aggregate_calibration_ratio": total_predicted / total_actual
        if total_actual > 0
        else np.nan,
    }


def fit_rate_baseline(
    train_features: pd.DataFrame,
    *,
    prior_exposure_days: float = 30.0,
    cap_quantile: float = 0.99,
) -> dict[str, Any]:
    """Fit a pooled historical revenue rate and a shrunk customer-rate baseline.

    A 30-day pooled-rate pseudo-exposure stabilizes short-tenure histories. The
    cap is a TRAIN-only quantile of shrunk rates; it controls unstable extreme
    histories without deleting those customers or their future outcomes.
    """
    features = validate_features(train_features)
    if prior_exposure_days <= 0:
        raise ValueError("prior_exposure_days must be positive.")
    if not 0.5 <= cap_quantile <= 1.0:
        raise ValueError("cap_quantile must be between 0.5 and 1.")
    exposure = features["Tenure_obs_days"].to_numpy(dtype=float)
    gross = np.maximum(features["Monetary_Gross"].to_numpy(dtype=float), 0.0)
    total_exposure = float(exposure.sum())
    if total_exposure <= 0:
        raise ValueError("TRAIN customers must have positive observation exposure.")
    pooled_rate = float(gross.sum() / total_exposure)
    shrunk = (gross + prior_exposure_days * pooled_rate) / (
        exposure + prior_exposure_days
    )
    cap = float(np.quantile(shrunk, cap_quantile))
    return {
        "pooled_rate_per_day": pooled_rate,
        "prior_exposure_days": float(prior_exposure_days),
        "rate_cap": max(cap, 0.0),
        "rate_cap_quantile": float(cap_quantile),
        "training_customers": int(len(features)),
    }


def predict_rate_baseline(
    rate_model: Mapping[str, Any],
    customer_features: pd.DataFrame,
    horizon: int,
) -> np.ndarray:
    features = validate_features(customer_features)
    if horizon not in HORIZONS:
        raise ValueError(f"Unsupported forecast horizon: {horizon}")
    prior = float(rate_model["prior_exposure_days"])
    pooled = float(rate_model["pooled_rate_per_day"])
    exposure = features["Tenure_obs_days"].to_numpy(dtype=float)
    gross = np.maximum(features["Monetary_Gross"].to_numpy(dtype=float), 0.0)
    rate = (gross + prior * pooled) / (exposure + prior)
    rate = np.minimum(np.maximum(rate, 0.0), float(rate_model["rate_cap"]))
    return rate * float(horizon)


def fit_segment_conditional(
    train_features: pd.DataFrame,
    train_targets: pd.DataFrame,
    horizon: int,
    *,
    prior_purchasers: float = 20.0,
) -> dict[str, Any]:
    """Estimate purchaser-only segment means, shrunk toward the TRAIN global mean."""
    features = validate_features(train_features)
    targets = _validate_targets(features, train_targets, horizon)
    if prior_purchasers < 0:
        raise ValueError("prior_purchasers must be non-negative.")
    purchaser_mask = _purchaser_mask(targets, horizon)
    revenue_col = f"FutureRevenue_{horizon}d"
    if not purchaser_mask.any():
        raise ValueError(f"TRAIN has no purchasers for the {horizon}-day horizon.")
    purchaser_features = features.loc[purchaser_mask].reset_index(drop=True)
    purchaser_targets = targets.loc[purchaser_mask].reset_index(drop=True)
    amounts = purchaser_targets[revenue_col].to_numpy(dtype=float)
    global_mean = float(amounts.mean())
    segment_means: dict[str, float] = {}
    segment_counts: dict[str, int] = {}
    for segment, positions in purchaser_features.groupby("Hist_Segment", sort=False).indices.items():
        indices = np.asarray(positions, dtype=int)
        count = int(len(indices))
        segment_total = float(amounts[indices].sum())
        segment_counts[str(segment)] = count
        segment_means[str(segment)] = float(
            (segment_total + prior_purchasers * global_mean) / (count + prior_purchasers)
            if count + prior_purchasers > 0
            else global_mean
        )
    return {
        "horizon_days": int(horizon),
        "global_conditional_mean": global_mean,
        "segment_conditional_means": segment_means,
        "segment_purchaser_counts": segment_counts,
        "prior_purchasers": float(prior_purchasers),
        "training_purchasers": int(purchaser_mask.sum()),
    }


def predict_segment_conditional(
    segment_model: Mapping[str, Any],
    customer_features: pd.DataFrame,
) -> np.ndarray:
    features = validate_features(customer_features)
    global_mean = float(segment_model["global_conditional_mean"])
    means = segment_model["segment_conditional_means"]
    predictions = features["Hist_Segment"].map(means).fillna(global_mean).to_numpy(dtype=float)
    return np.clip(np.nan_to_num(predictions, nan=global_mean), 0.0, 1e15)


def fit_personalized_conditional(
    train_features: pd.DataFrame,
    train_targets: pd.DataFrame,
    validation_features: pd.DataFrame,
    validation_targets: pd.DataFrame,
    horizon: int,
    *,
    alpha_candidates: Sequence[float] = DEFAULT_ALPHA_CANDIDATES,
) -> dict[str, Any]:
    """Select Ridge alpha on VAL purchasers, then fit on TRAIN purchasers only."""
    train_x = validate_features(train_features)
    val_x = validate_features(validation_features)
    train_y = _validate_targets(train_x, train_targets, horizon)
    val_y = _validate_targets(val_x, validation_targets, horizon)
    candidates = tuple(sorted({float(alpha) for alpha in alpha_candidates}))
    if not candidates or any(alpha <= 0 for alpha in candidates):
        raise ValueError("Ridge alpha candidates must be positive.")

    train_mask = _purchaser_mask(train_y, horizon)
    val_mask = _purchaser_mask(val_y, horizon)
    if train_mask.sum() < 2:
        raise ValueError("At least two TRAIN purchasers are required for personalized fitting.")
    if not val_mask.any():
        raise ValueError(f"VAL has no purchasers for the {horizon}-day horizon.")

    train_x_buyers = train_x.loc[train_mask].reset_index(drop=True)
    val_x_buyers = val_x.loc[val_mask].reset_index(drop=True)
    revenue_col = f"FutureRevenue_{horizon}d"
    train_amounts = train_y.loc[train_mask, revenue_col].to_numpy(dtype=float)
    val_amounts = val_y.loc[val_mask, revenue_col].to_numpy(dtype=float)
    log_train = np.log1p(train_amounts)
    rows: list[dict[str, Any]] = []
    fitted_candidates: dict[float, tuple[Pipeline, float]] = {}

    for alpha in candidates:
        pipeline = _build_ridge_pipeline(alpha)
        pipeline.fit(train_x_buyers, log_train)
        smearing = _smearing_factor(pipeline, train_x_buyers, log_train)
        val_log_prediction = pipeline.predict(val_x_buyers)
        val_prediction = _inverse_log_mean(val_log_prediction, smearing)
        metrics = _conditional_metrics(val_amounts, val_prediction)
        rows.append(
            {
                "horizon_days": int(horizon),
                "alpha": float(alpha),
                "n_validation_purchasers": int(len(val_amounts)),
                "validation_mae": metrics["mae"],
                "validation_rmse": metrics["rmse"],
                "validation_bias": metrics["bias"],
                "validation_wape": metrics["wape"],
                "smearing_factor": smearing,
            }
        )
        fitted_candidates[alpha] = (pipeline, smearing)

    selection = pd.DataFrame(rows).sort_values(
        ["validation_rmse", "alpha"], ascending=[True, False]
    ).reset_index(drop=True)
    selected_alpha = float(selection.iloc[0]["alpha"])
    selected_pipeline = _build_ridge_pipeline(selected_alpha)
    selected_pipeline.fit(train_x_buyers, log_train)
    selected_smearing = _smearing_factor(selected_pipeline, train_x_buyers, log_train)
    return {
        "horizon_days": int(horizon),
        "pipeline": selected_pipeline,
        "alpha": selected_alpha,
        "smearing_factor": selected_smearing,
        "selection_metric": "minimum VAL conditional-purchaser RMSE; tie-break toward larger alpha",
        "selection_metrics": selection,
        "training_purchasers": int(train_mask.sum()),
        "validation_purchasers": int(val_mask.sum()),
        "training_log_target": "log1p(FutureRevenue_Hd)",
        "retransformation": "expm1-scale conditional mean via TRAIN-only 5-fold OOF Duan smearing",
    }


def predict_personalized_conditional(
    personalized_model: Mapping[str, Any],
    customer_features: pd.DataFrame,
) -> np.ndarray:
    features = validate_features(customer_features)
    log_prediction = personalized_model["pipeline"].predict(features)
    return _inverse_log_mean(log_prediction, float(personalized_model["smearing_factor"]))


def fit_horizon_models(
    train_features: pd.DataFrame,
    train_targets: pd.DataFrame,
    validation_features: pd.DataFrame,
    validation_targets: pd.DataFrame,
    horizon: int,
    *,
    alpha_candidates: Sequence[float] = DEFAULT_ALPHA_CANDIDATES,
) -> dict[str, Any]:
    """Fit the three spending methods without accepting or inspecting TEST data."""
    train_x = validate_features(train_features)
    val_x = validate_features(validation_features)
    _validate_targets(train_x, train_targets, horizon)
    _validate_targets(val_x, validation_targets, horizon)
    rate_model = fit_rate_baseline(train_x)
    segment_model = fit_segment_conditional(train_x, train_targets, horizon)
    personalized_model = fit_personalized_conditional(
        train_x,
        train_targets,
        val_x,
        validation_targets,
        horizon,
        alpha_candidates=alpha_candidates,
    )
    return {
        "horizon_days": int(horizon),
        "historical_rate": rate_model,
        "segment_conditional": segment_model,
        "personalized_conditional": personalized_model,
    }


def _align_purchase_probabilities(
    customer_features: pd.DataFrame,
    purchase_probabilities: pd.DataFrame,
    horizons: Sequence[int],
) -> pd.DataFrame:
    required = [CUSTOMER_ID, CUTOFF_COL, *(f"personalized_P{h}" for h in horizons)]
    _require_columns(purchase_probabilities, required, "purchase_probabilities")
    probs = purchase_probabilities.loc[:, required].copy()
    probs[CUTOFF_COL] = pd.to_datetime(probs[CUTOFF_COL], errors="raise")
    if probs.duplicated([CUSTOMER_ID, CUTOFF_COL]).any():
        raise ValueError("Purchase probabilities must be unique by customer and cutoff.")
    expected_keys = customer_features[[CUSTOMER_ID, CUTOFF_COL]].sort_values(
        [CUSTOMER_ID, CUTOFF_COL]
    ).reset_index(drop=True)
    actual_keys = probs[[CUSTOMER_ID, CUTOFF_COL]].sort_values(
        [CUSTOMER_ID, CUTOFF_COL]
    ).reset_index(drop=True)
    if not expected_keys.equals(actual_keys):
        raise ValueError("Purchase probabilities do not match the customer/cutoff cohort.")
    aligned = customer_features[[CUSTOMER_ID, CUTOFF_COL]].merge(
        probs, on=[CUSTOMER_ID, CUTOFF_COL], how="left", validate="one_to_one", sort=False
    )
    for horizon in horizons:
        column = f"personalized_P{horizon}"
        values = pd.to_numeric(aligned[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
            raise ValueError(f"{column} must contain finite purchase probabilities.")
        if not values.between(0.0, 1.0).all():
            raise ValueError(f"{column} must be between zero and one.")
        aligned[column] = values.astype(float)
    return aligned


def predict_expected_revenue(
    spending_bundle: Mapping[str, Any] | str | Path,
    customer_features: pd.DataFrame,
    purchase_probabilities: pd.DataFrame,
) -> pd.DataFrame:
    """Return inference-only rate and two-stage expected revenue forecasts.

    Purchase probabilities must come from the same customer and cutoff rows.
    The returned table contains no realized future outcomes.
    """
    bundle = (
        load_spending_artifacts(spending_bundle)
        if isinstance(spending_bundle, (str, Path))
        else dict(spending_bundle)
    )
    features = validate_features(customer_features)
    horizon_models = bundle.get("horizon_models", {})
    supported = tuple(sorted(int(h) for h in horizon_models))
    if not supported:
        raise ValueError("Spending bundle does not contain fitted horizon models.")
    aligned_probs = _align_purchase_probabilities(features, purchase_probabilities, supported)
    output = features[[CUSTOMER_ID, CUTOFF_COL]].reset_index(drop=True).copy()
    for horizon in supported:
        models = horizon_models[horizon]
        probability = aligned_probs[f"personalized_P{horizon}"].to_numpy(dtype=float)
        rate_forecast = predict_rate_baseline(
            models["historical_rate"], features, horizon
        )
        segment_amount = predict_segment_conditional(
            models["segment_conditional"], features
        )
        personalized_amount = predict_personalized_conditional(
            models["personalized_conditional"], features
        )
        output[f"purchase_probability_{horizon}d"] = probability
        output[f"historical_rate_expected_{horizon}d"] = rate_forecast
        output[f"segment_conditional_revenue_{horizon}d"] = segment_amount
        output[f"segment_expected_revenue_{horizon}d"] = probability * segment_amount
        output[f"personalized_conditional_revenue_{horizon}d"] = personalized_amount
        output[f"personalized_expected_revenue_{horizon}d"] = probability * personalized_amount
    prediction_columns = [c for c in output if c not in (CUSTOMER_ID, CUTOFF_COL)]
    values = output[prediction_columns].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Inference produced non-finite or negative revenue forecasts.")
    return output


def evaluate_conditional_spending(
    actual_revenue: Sequence[float],
    predicted_conditional_revenue: Sequence[float],
) -> dict[str, float | int]:
    """Score conditional amounts only among customers with future orders."""
    actual = np.asarray(actual_revenue, dtype=float)
    predicted = np.asarray(predicted_conditional_revenue, dtype=float)
    if actual.shape != predicted.shape:
        raise ValueError("Conditional actual and predicted amounts must have equal shape.")
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Conditional spending metrics require finite values.")
    return _conditional_metrics(actual, predicted)


def evaluate_expected_revenue(
    actual_revenue: Sequence[float],
    predicted_expected_revenue: Sequence[float],
) -> dict[str, float | int]:
    """Score unconditional expected revenue across the complete cohort."""
    actual = np.asarray(actual_revenue, dtype=float)
    predicted = np.asarray(predicted_expected_revenue, dtype=float)
    if actual.shape != predicted.shape:
        raise ValueError("Expected-revenue actual and predicted arrays must have equal shape.")
    if len(actual) == 0 or not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Expected-revenue metrics require non-empty finite values.")
    if (predicted < 0).any():
        raise ValueError("Expected revenue forecasts cannot be negative.")
    return _expected_metrics(actual, predicted)


def save_spending_artifacts(
    spending_bundle: Mapping[str, Any],
    model_dir: str | Path,
) -> Path:
    destination = Path(model_dir)
    destination.mkdir(parents=True, exist_ok=True)
    bundle_path = destination / "spending_models.joblib"
    temporary = destination / "spending_models.joblib.tmp"
    joblib.dump(dict(spending_bundle), temporary)
    temporary.replace(bundle_path)
    metadata = dict(spending_bundle["metadata"])
    metadata_path = destination / "metadata.json"
    metadata_tmp = destination / "metadata.json.tmp"
    metadata_tmp.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    metadata_tmp.replace(metadata_path)
    return bundle_path


def load_spending_artifacts(model_dir: str | Path) -> dict[str, Any]:
    source = Path(model_dir) / "spending_models.joblib"
    if not source.exists():
        raise FileNotFoundError(f"Spending model bundle not found: {source}")
    bundle = joblib.load(source)
    if bundle.get("metadata", {}).get("model_version") != MODEL_VERSION:
        raise ValueError("Unsupported spending-model bundle version.")
    if not bundle.get("horizon_models"):
        raise ValueError("Saved spending-model bundle has no fitted horizons.")
    return bundle


def make_metadata(
    horizon_models: Mapping[int, Mapping[str, Any]],
    *,
    purchase_model_metadata: Mapping[str, Any],
    split_files: Mapping[int, str],
) -> dict[str, Any]:
    """Build compact model metadata without storing future evaluation outcomes."""
    return {
        "model_version": MODEL_VERSION,
        "forecast_horizons_days": sorted(int(h) for h in horizon_models),
        "target_definition": "Total gross revenue from all valid orders in (cutoff, cutoff + H].",
        "conditional_target": "log1p(FutureRevenue_Hd) among TRAIN customers with FutureOrders_Hd > 0.",
        "conditional_selection": "Minimum validation conditional-purchaser RMSE; tie-break toward larger Ridge alpha.",
        "retransformation": "Duan smearing estimated from out-of-fold TRAIN log residuals.",
        "rate_baseline": {
            "prior_exposure_days": 30,
            "rate_cap_quantile": 0.99,
            "cap_fit_on": "TRAIN historical customer rates only",
        },
        "segment_smoothing_prior_purchasers": 20,
        "numeric_predictors": list(NUMERIC_FEATURES),
        "numeric_preprocessing": (
            "TRAIN-fitted median imputation and missingness indicators, log1p, "
            "TRAIN-only 1st/99th percentile clipping, then StandardScaler"
        ),
        "categorical_predictors": list(CATEGORICAL_FEATURES),
        "excluded_predictors": sorted(FORBIDDEN_FEATURES),
        "training_only_preprocessing": True,
        "test_data_used_for_selection_or_training": False,
        "split_files": {str(h): str(path) for h, path in split_files.items()},
        "purchase_probability_source_model": {
            "model_version": purchase_model_metadata.get("model_version"),
            "training_cutoff": purchase_model_metadata.get("training_cutoff"),
            "training_split_file": purchase_model_metadata.get("training_split_file"),
            "training_customers": purchase_model_metadata.get("training_customers"),
            "test_predictions_file_not_reused": True,
            "used_for_spending_fit": False,
            "used_for_joint_validation_and_test_forecasts": True,
        },
        "horizon_training": {
            str(horizon): {
                "training_customers": int(models["historical_rate"]["training_customers"]),
                "training_purchasers": int(
                    models["personalized_conditional"]["training_purchasers"]
                ),
                "validation_purchasers": int(
                    models["personalized_conditional"]["validation_purchasers"]
                ),
                "selected_alpha": float(models["personalized_conditional"]["alpha"]),
                "smearing_factor": float(
                    models["personalized_conditional"]["smearing_factor"]
                ),
            }
            for horizon, models in horizon_models.items()
        },
    }
