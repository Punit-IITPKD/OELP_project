"""Conservative grid-based functional trajectory analysis.

The implementation is explicitly a PCA approximation on a common discrete
time grid, not a specialized functional-data estimator.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.decomposition import PCA

CUSTOMER_ID = "Customer ID"


@dataclass(frozen=True)
class FunctionalTrajectoryConfig:
    """PCA settings for curves whose observation support was assessed upstream."""

    curve_columns: tuple[str, ...]
    max_components: int = 3
    smoothing_method: str = "none"
    smoothing_window: int = 3
    min_train_curves: int = 30

    def __post_init__(self) -> None:
        if not self.curve_columns or len(set(self.curve_columns)) != len(
            self.curve_columns
        ):
            raise ValueError("curve_columns must be non-empty and unique.")
        if self.max_components < 1:
            raise ValueError("max_components must be positive.")
        if self.smoothing_method not in {"none", "moving_average"}:
            raise ValueError("smoothing_method must be 'none' or 'moving_average'.")
        if self.smoothing_window < 2:
            raise ValueError("smoothing_window must be at least 2.")
        if self.min_train_curves < 3:
            raise ValueError("min_train_curves must be at least 3.")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["curve_columns"] = list(self.curve_columns)
        return result


def _validate_curve_table(
    curves: pd.DataFrame, curve_columns: Sequence[str]
) -> None:
    if CUSTOMER_ID not in curves:
        raise ValueError(f"Curves must include {CUSTOMER_ID!r}.")
    if curves[CUSTOMER_ID].isna().any() or curves[CUSTOMER_ID].duplicated().any():
        raise ValueError("Curve table must contain one non-null row per customer.")
    missing = sorted(set(curve_columns).difference(curves.columns))
    if missing:
        raise ValueError(f"Curve table is missing grid columns: {missing}")


def _smooth(values: np.ndarray, method: str, window: int) -> np.ndarray:
    if method == "none":
        return values.copy()
    radius_left = (window - 1) // 2
    radius_right = window - 1 - radius_left
    padded = np.pad(values, ((0, 0), (radius_left, radius_right)), mode="edge")
    kernel = np.ones(window, dtype=float) / window
    return np.vstack(
        [np.convolve(row, kernel, mode="valid") for row in padded]
    )


def _log_curve_values(values: np.ndarray) -> np.ndarray:
    if not np.isfinite(values).all():
        raise ValueError("Functional fitting requires complete finite curves.")
    if (values < 0).any():
        raise ValueError("Purchase-rate curves cannot contain negative values.")
    return np.log1p(values)


def fit_functional_representation(
    train_curves: pd.DataFrame,
    config: FunctionalTrajectoryConfig,
) -> dict[str, Any]:
    """Fit log transform, optional smoothing, and PCA using TRAIN curves only."""
    _validate_curve_table(train_curves, config.curve_columns)
    eligible = np.ones(len(train_curves), dtype=bool)
    if "functional_eligible" in train_curves:
        eligible &= train_curves["functional_eligible"].fillna(False).to_numpy(
            dtype=bool
        )
    values = train_curves.loc[:, config.curve_columns].to_numpy(dtype=float)
    eligible &= np.isfinite(values).all(axis=1)
    supported = values[eligible]
    if len(supported) < config.min_train_curves:
        raise ValueError(
            "Insufficient supported TRAIN curves for functional PCA: "
            f"{len(supported)} < {config.min_train_curves}."
        )
    logged = _log_curve_values(supported)
    smoothed = _smooth(
        logged,
        config.smoothing_method,
        config.smoothing_window,
    )
    component_count = min(
        config.max_components,
        smoothed.shape[0] - 1,
        smoothed.shape[1],
    )
    if component_count < 1:
        raise ValueError("At least two TRAIN curves and one time window are required.")
    pca = PCA(n_components=component_count, svd_solver="full")
    scores = pca.fit_transform(smoothed)
    return {
        "fit_role": "TRAIN",
        "fit_customer_count": int(len(supported)),
        "method": "grid_based_functional_pca_approximation",
        "curve_columns": list(config.curve_columns),
        "config": config.to_dict(),
        "pca": pca,
        "mean_log_curve": np.mean(smoothed, axis=0),
        "explained_variance_ratio": pca.explained_variance_ratio_.astype(float),
        "training_reconstruction_rmse": float(
            np.sqrt(np.mean((smoothed - pca.inverse_transform(scores)) ** 2))
        ),
    }


def transform_functional_representation(
    fitted_bundle: dict[str, Any],
    customer_curves: pd.DataFrame,
) -> pd.DataFrame:
    """Apply frozen TRAIN PCA; incomplete or unsupported curves receive null scores."""
    if fitted_bundle.get("fit_role") != "TRAIN":
        raise ValueError("Functional transforms must come from a TRAIN-fitted bundle.")
    columns = list(fitted_bundle["curve_columns"])
    _validate_curve_table(customer_curves, columns)
    values = customer_curves.loc[:, columns].to_numpy(dtype=float)
    eligible = np.isfinite(values).all(axis=1)
    if "functional_eligible" in customer_curves:
        eligible &= customer_curves["functional_eligible"].fillna(False).to_numpy(
            dtype=bool
        )
    component_count = int(fitted_bundle["pca"].n_components_)
    scores = np.full((len(customer_curves), component_count), np.nan, dtype=float)
    if eligible.any():
        logged = _log_curve_values(values[eligible])
        config = fitted_bundle["config"]
        transformed_curves = _smooth(
            logged,
            config["smoothing_method"],
            int(config["smoothing_window"]),
        )
        scores[eligible] = fitted_bundle["pca"].transform(transformed_curves)
    result = pd.DataFrame({CUSTOMER_ID: customer_curves[CUSTOMER_ID].to_numpy()})
    for index in range(component_count):
        result[f"functional_component_{index + 1}"] = scores[:, index]
    result["functional_analysis_status"] = np.where(
        eligible, "scored", "insufficient_history"
    )
    return result


def evaluate_functional_representation(
    fitted_bundle: dict[str, Any],
    curves: pd.DataFrame,
) -> dict[str, Any]:
    """Evaluate reconstruction and return fitted curve/component summaries."""
    columns = list(fitted_bundle["curve_columns"])
    _validate_curve_table(curves, columns)
    values = curves.loc[:, columns].to_numpy(dtype=float)
    eligible = np.isfinite(values).all(axis=1)
    if "functional_eligible" in curves:
        eligible &= curves["functional_eligible"].fillna(False).to_numpy(dtype=bool)
    supported = _smooth(
        _log_curve_values(values[eligible]),
        fitted_bundle["config"]["smoothing_method"],
        int(fitted_bundle["config"]["smoothing_window"]),
    )
    if not len(supported):
        return {
            "method": fitted_bundle["method"],
            "evaluated_curves": 0,
            "reconstruction_rmse": None,
            "limitations": ["no_complete_curves_in_evaluation_set"],
        }
    scores = fitted_bundle["pca"].transform(supported)
    reconstruction = fitted_bundle["pca"].inverse_transform(scores)
    return {
        "method": fitted_bundle["method"],
        "evaluated_curves": int(len(supported)),
        "component_count": int(fitted_bundle["pca"].n_components_),
        "explained_variance_ratio": [
            float(value)
            for value in fitted_bundle["pca"].explained_variance_ratio_
        ],
        "cumulative_explained_variance": float(
            fitted_bundle["pca"].explained_variance_ratio_.sum()
        ),
        "reconstruction_rmse": float(
            np.sqrt(np.mean((supported - reconstruction) ** 2))
        ),
        "mean_log_curve": [
            float(value) for value in fitted_bundle["mean_log_curve"]
        ],
        "component_shapes": [
            [float(value) for value in component]
            for component in fitted_bundle["pca"].components_
        ],
        "limitations": [
            "grid_based_pca_approximation_not_specialized_functional_estimator",
            "principal_components_describe_associations_not_causal_mechanisms",
        ],
    }


def evaluate_functional_component_stability(
    train_curves: pd.DataFrame,
    fitted_bundle: dict[str, Any],
    *,
    random_state: int = 42,
    n_resamples: int = 50,
    resample_fraction: float = 0.8,
) -> dict[str, Any]:
    """Assess PCA direction stability on TRAIN subsamples using aligned cosines.

    Principal-component signs and ordering are arbitrary. Each resample's
    directions are therefore optimally aligned to the frozen TRAIN solution,
    and absolute cosine similarity is reported. This is a sensitivity measure,
    not an inferential confidence interval.
    """
    if fitted_bundle.get("fit_role") != "TRAIN":
        raise ValueError("Functional component stability requires a TRAIN fit.")
    if isinstance(n_resamples, bool) or n_resamples < 2:
        raise ValueError("n_resamples must be at least 2.")
    if not 0.5 <= resample_fraction < 1:
        raise ValueError("resample_fraction must be in [0.5, 1).")
    columns = list(fitted_bundle["curve_columns"])
    _validate_curve_table(train_curves, columns)
    values = train_curves.loc[:, columns].to_numpy(dtype=float)
    eligible = np.isfinite(values).all(axis=1)
    if "functional_eligible" in train_curves:
        eligible &= train_curves["functional_eligible"].fillna(False).to_numpy(
            dtype=bool
        )
    supported = values[eligible]
    component_count = int(fitted_bundle["pca"].n_components_)
    sample_size = int(len(supported) * resample_fraction)
    if sample_size < max(3, component_count):
        raise ValueError("Too few TRAIN curves for component stability resampling.")
    config = fitted_bundle["config"]
    logged = _log_curve_values(supported)
    transformed = _smooth(
        logged,
        config["smoothing_method"],
        int(config["smoothing_window"]),
    )
    reference = fitted_bundle["pca"].components_
    rng = np.random.default_rng(random_state)
    alignments = np.empty((n_resamples, component_count), dtype=float)
    for resample in range(n_resamples):
        indices = np.sort(
            rng.choice(len(transformed), size=sample_size, replace=False)
        )
        candidate = PCA(n_components=component_count, svd_solver="full")
        candidate.fit(transformed[indices])
        similarity = np.abs(candidate.components_ @ reference.T)
        rows, columns_match = linear_sum_assignment(-similarity)
        aligned = np.empty(component_count, dtype=float)
        aligned[columns_match] = similarity[rows, columns_match]
        alignments[resample] = aligned
    return {
        "fit_role": "TRAIN",
        "metric": "absolute_cosine_similarity_after_optimal_component_alignment",
        "n_resamples": int(n_resamples),
        "resample_fraction": float(resample_fraction),
        "resample_size": int(sample_size),
        "component_alignment_mean": [
            float(value) for value in alignments.mean(axis=0)
        ],
        "component_alignment_min": [
            float(value) for value in alignments.min(axis=0)
        ],
        "component_alignment_95_percentile_interval": [
            [
                float(np.quantile(alignments[:, component], 0.025)),
                float(np.quantile(alignments[:, component], 0.975)),
            ]
            for component in range(component_count)
        ],
        "interpretation": (
            "Higher aligned absolute cosine indicates more similar component "
            "directions across TRAIN customer subsamples; it is not a causal or "
            "inferential confidence interval."
        ),
    }
