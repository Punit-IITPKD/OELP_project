"""TRAIN-fitted trajectory clustering and validation utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    normalized_mutual_info_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

CUSTOMER_ID = "Customer ID"

DEFAULT_CLUSTER_FEATURES = (
    "purchase_rate_slope_per_window",
    "revenue_rate_slope_per_window",
    "purchase_rate_recent_minus_early",
    "revenue_rate_recent_minus_early",
    "purchase_rate_volatility",
    "revenue_rate_volatility",
    "active_purchase_windows",
    "longest_observed_inactive_run",
    "completed_gap_slope_days_per_gap",
)
TARGET_COLUMN_TOKENS = (
    "future",
    "target",
    "purchased_",
    "nextpurchase",
    "next_purchase",
    "test_outcome",
    "expected_revenue",
)


@dataclass(frozen=True)
class TrajectoryClusteringConfig:
    """Fixed clustering choices; all transforms are fitted on TRAIN rows."""

    feature_columns: tuple[str, ...] = DEFAULT_CLUSTER_FEATURES
    n_clusters: int = 3
    random_state: int = 42
    n_init: int = 20
    max_iter: int = 500
    eligible_column: str = "cluster_eligible"
    stability_runs: int = 12
    stability_fraction: float = 0.8

    def __post_init__(self) -> None:
        if not self.feature_columns or len(set(self.feature_columns)) != len(
            self.feature_columns
        ):
            raise ValueError("feature_columns must be non-empty and unique.")
        if (
            isinstance(self.n_clusters, bool)
            or not isinstance(self.n_clusters, int)
            or not 2 <= self.n_clusters <= 6
        ):
            raise ValueError("n_clusters must be an integer between 2 and 6.")
        if (
            isinstance(self.n_init, bool)
            or not isinstance(self.n_init, int)
            or self.n_init < 1
            or isinstance(self.max_iter, bool)
            or not isinstance(self.max_iter, int)
            or self.max_iter < 1
        ):
            raise ValueError("n_init and max_iter must be positive.")
        if self.stability_runs < 1:
            raise ValueError("stability_runs must be positive.")
        if not 0.5 <= self.stability_fraction < 1:
            raise ValueError("stability_fraction must be in [0.5, 1).")
        for column in self.feature_columns:
            if any(token in column.lower() for token in TARGET_COLUMN_TOKENS):
                raise ValueError(f"Outcome-derived feature is forbidden: {column}")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["feature_columns"] = list(self.feature_columns)
        return result


DEFAULT_CLUSTER_CONFIG = TrajectoryClusteringConfig()


def _validate_customer_rows(frame: pd.DataFrame) -> None:
    if CUSTOMER_ID not in frame:
        raise ValueError(f"Features must include {CUSTOMER_ID!r}.")
    if frame[CUSTOMER_ID].isna().any():
        raise ValueError("Customer IDs cannot be missing.")
    if frame[CUSTOMER_ID].duplicated().any():
        raise ValueError("Features must contain one row per customer and cutoff.")


def _eligibility_mask(
    frame: pd.DataFrame, eligible_column: str
) -> pd.Series:
    if eligible_column not in frame:
        if "eligible_for_summary_trajectory" in frame:
            return frame["eligible_for_summary_trajectory"].fillna(False).astype(bool)
        if "history_sufficiency" in frame:
            return frame["history_sufficiency"].eq(
                "sufficient_for_summary_trajectory"
            ) | frame["history_sufficiency"].eq(
                "sufficient_for_functional_analysis"
            )
        raise ValueError(f"Features are missing eligibility field {eligible_column!r}.")
    return frame[eligible_column].fillna(False).astype(bool)


def prepare_trajectory_features(
    trajectory_table: pd.DataFrame,
    config: TrajectoryClusteringConfig | None = None,
) -> pd.DataFrame:
    """Select documented, target-free numeric features and support status."""
    config = config or DEFAULT_CLUSTER_CONFIG
    _validate_customer_rows(trajectory_table)
    forbidden = [
        column
        for column in trajectory_table.columns
        if any(token in column.lower() for token in TARGET_COLUMN_TOKENS)
    ]
    if forbidden:
        raise ValueError(
            "Outcome/target columns cannot enter trajectory features: "
            f"{sorted(forbidden)}"
        )
    missing = sorted(set(config.feature_columns).difference(trajectory_table.columns))
    if missing:
        raise ValueError(f"Trajectory features are missing columns: {missing}")
    result = trajectory_table.loc[:, [CUSTOMER_ID, *config.feature_columns]].copy()
    result[config.eligible_column] = _eligibility_mask(
        trajectory_table, config.eligible_column
    ).to_numpy()
    return result


def fit_trajectory_transform(
    train_trajectories: pd.DataFrame,
    config: TrajectoryClusteringConfig | None = None,
) -> dict[str, Any]:
    """Fit median imputation and standardization on TRAIN customers only."""
    config = config or DEFAULT_CLUSTER_CONFIG
    _validate_customer_rows(train_trajectories)
    missing = sorted(set(config.feature_columns).difference(train_trajectories.columns))
    if missing:
        raise ValueError(f"TRAIN features are missing columns: {missing}")
    eligible = _eligibility_mask(train_trajectories, config.eligible_column)
    values = train_trajectories.loc[eligible, config.feature_columns].to_numpy(
        dtype=float
    )
    if values.shape[0] < config.n_clusters:
        raise ValueError("Not enough eligible TRAIN customers for the requested clusters.")
    if not np.isfinite(values[~np.isnan(values)]).all():
        raise ValueError("TRAIN feature values must be finite or missing.")
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    imputed = imputer.fit_transform(values)
    scaler = StandardScaler()
    scaler.fit(imputed)
    return {
        "fit_role": "TRAIN",
        "fit_customer_count": int(values.shape[0]),
        "feature_columns": list(config.feature_columns),
        "imputer": imputer,
        "scaler": scaler,
        "config": config.to_dict(),
    }


def _transform_values(
    transform_bundle: dict[str, Any],
    features: pd.DataFrame,
) -> np.ndarray:
    columns = list(transform_bundle["feature_columns"])
    missing = sorted(set(columns).difference(features.columns))
    if missing:
        raise ValueError(f"Features are missing fitted columns: {missing}")
    values = features.loc[:, columns].to_numpy(dtype=float)
    if not np.isfinite(values[~np.isnan(values)]).all():
        raise ValueError("Feature values must be finite or missing.")
    return transform_bundle["scaler"].transform(
        transform_bundle["imputer"].transform(values)
    )


def transform_trajectory_features(
    transform_bundle: dict[str, Any],
    features: pd.DataFrame,
) -> pd.DataFrame:
    """Apply frozen TRAIN imputation/scaling and retain support statuses."""
    if transform_bundle.get("fit_role") != "TRAIN":
        raise ValueError("Trajectory preprocessing must be fitted on TRAIN.")
    _validate_customer_rows(features)
    config = TrajectoryClusteringConfig(
        **{
            **transform_bundle["config"],
            "feature_columns": tuple(transform_bundle["config"]["feature_columns"]),
        }
    )
    eligible = _eligibility_mask(features, config.eligible_column)
    result = pd.DataFrame(
        {
            CUSTOMER_ID: features[CUSTOMER_ID].to_numpy(),
            "transform_status": np.where(
                eligible, "transformed", "insufficient_history"
            ),
        }
    )
    for column in config.feature_columns:
        result[f"scaled_{column}"] = np.nan
    if eligible.any():
        transformed = _transform_values(
            transform_bundle,
            features.loc[eligible].reset_index(drop=True),
        )
        result.loc[eligible.to_numpy(), [
            f"scaled_{column}" for column in config.feature_columns
        ]] = transformed
    return result


def fit_trajectory_clusters(
    train_features: pd.DataFrame,
    config: TrajectoryClusteringConfig | None = None,
) -> dict[str, Any]:
    """Fit the preprocessing transform and K-Means centers on TRAIN only."""
    config = config or DEFAULT_CLUSTER_CONFIG
    transform = fit_trajectory_transform(train_features, config)
    eligible = _eligibility_mask(train_features, config.eligible_column)
    transformed = _transform_values(
        transform, train_features.loc[eligible].reset_index(drop=True)
    )
    model = KMeans(
        n_clusters=config.n_clusters,
        random_state=config.random_state,
        n_init=config.n_init,
        max_iter=config.max_iter,
    ).fit(transformed)
    return {
        "fit_role": "TRAIN",
        "cluster_count": config.n_clusters,
        "random_state": config.random_state,
        "config": config.to_dict(),
        "transform": transform,
        "model": model,
    }


def assign_trajectory_clusters(
    fitted_bundle: dict[str, Any],
    features: pd.DataFrame,
) -> pd.DataFrame:
    """Assign with frozen TRAIN preprocessing and centers; unsupported stay null."""
    _validate_customer_rows(features)
    config_dict = fitted_bundle["config"]
    eligible_column = config_dict["eligible_column"]
    eligible = _eligibility_mask(features, eligible_column)
    result = pd.DataFrame(
        {
            CUSTOMER_ID: features[CUSTOMER_ID].to_numpy(),
            "trajectory_cluster_id": pd.Series(
                pd.array([pd.NA] * len(features), dtype="Int64")
            ),
            "cluster_assignment_status": np.where(
                eligible, "assigned", "insufficient_history"
            ),
            "distance_to_cluster_center": np.nan,
        }
    )
    if eligible.any():
        transformed = _transform_values(
            fitted_bundle["transform"],
            features.loc[eligible].reset_index(drop=True),
        )
        labels = fitted_bundle["model"].predict(transformed)
        centers = fitted_bundle["model"].cluster_centers_
        distances = np.linalg.norm(transformed - centers[labels], axis=1)
        result.loc[eligible.to_numpy(), "trajectory_cluster_id"] = labels.astype(int)
        result.loc[eligible.to_numpy(), "distance_to_cluster_center"] = distances
    return result


def evaluate_cluster_stability(
    train_features: pd.DataFrame,
    fitted_bundle: dict[str, Any],
    config: TrajectoryClusteringConfig | None = None,
) -> dict[str, Any]:
    """Measure seed and customer-resampling stability on TRAIN, never TEST."""
    config = config or TrajectoryClusteringConfig(**fitted_bundle["config"])
    eligible = _eligibility_mask(train_features, config.eligible_column)
    eligible_features = train_features.loc[eligible].reset_index(drop=True)
    transformed = _transform_values(fitted_bundle["transform"], eligible_features)
    n_customers = len(eligible_features)
    reference_labels = fitted_bundle["model"].labels_
    if len(reference_labels) != n_customers:
        reference_labels = fitted_bundle["model"].predict(transformed)

    seed_scores: list[float] = []
    for offset in range(config.stability_runs):
        candidate = KMeans(
            n_clusters=config.n_clusters,
            random_state=config.random_state + offset + 1,
            n_init=config.n_init,
            max_iter=config.max_iter,
        ).fit(transformed)
        seed_scores.append(
            float(adjusted_rand_score(reference_labels, candidate.labels_))
        )

    bootstrap_scores: list[float] = []
    rng = np.random.default_rng(config.random_state)
    sample_size = max(config.n_clusters + 1, int(n_customers * config.stability_fraction))
    if sample_size < n_customers:
        for offset in range(config.stability_runs):
            sample_indices = np.sort(
                rng.choice(n_customers, size=sample_size, replace=False)
            )
            candidate = KMeans(
                n_clusters=config.n_clusters,
                random_state=config.random_state + 1000 + offset,
                n_init=config.n_init,
                max_iter=config.max_iter,
            ).fit(transformed[sample_indices])
            bootstrap_scores.append(
                float(
                    adjusted_rand_score(
                        reference_labels[sample_indices], candidate.labels_
                    )
                )
            )

    labels = fitted_bundle["model"].predict(transformed)
    unique_labels = np.unique(labels)
    metric_values: dict[str, float | None] = {
        "silhouette_score": None,
        "davies_bouldin_index": None,
        "calinski_harabasz_index": None,
    }
    if 1 < len(unique_labels) < n_customers:
        metric_values = {
            "silhouette_score": float(silhouette_score(transformed, labels)),
            "davies_bouldin_index": float(
                davies_bouldin_score(transformed, labels)
            ),
            "calinski_harabasz_index": float(
                calinski_harabasz_score(transformed, labels)
            ),
        }
    sizes = pd.Series(labels).value_counts().sort_index().to_dict()
    return {
        "fit_role": "TRAIN",
        "eligible_train_customers": n_customers,
        "cluster_sizes": {str(int(key)): int(value) for key, value in sizes.items()},
        **metric_values,
        "seed_adjusted_rand_mean": (
            float(np.mean(seed_scores)) if seed_scores else None
        ),
        "seed_adjusted_rand_min": (
            float(np.min(seed_scores)) if seed_scores else None
        ),
        "resample_adjusted_rand_mean": (
            float(np.mean(bootstrap_scores)) if bootstrap_scores else None
        ),
        "resample_adjusted_rand_min": (
            float(np.min(bootstrap_scores)) if bootstrap_scores else None
        ),
        "stability_runs": config.stability_runs,
        "resample_fraction": config.stability_fraction,
        "resample_size": sample_size if bootstrap_scores else 0,
        "limitations": (
            []
            if bootstrap_scores
            else ["too_few_train_customers_for_resampling_stability"]
        ),
    }


def build_shape_trajectory_features(
    trajectory_matrix: pd.DataFrame,
    *,
    rate_column: str = "purchase_rate_per_observed_day",
) -> pd.DataFrame:
    """Return per-customer standardized shape curves with full-grid support."""
    required = {
        CUSTOMER_ID,
        "window_index",
        "observed_exposure_days",
        "purchase_count",
        rate_column,
    }
    missing = sorted(required.difference(trajectory_matrix.columns))
    if missing:
        raise ValueError(f"trajectory_matrix is missing columns: {missing}")
    if trajectory_matrix.empty:
        return pd.DataFrame(columns=[CUSTOMER_ID, "cluster_eligible"])
    window_count = int(trajectory_matrix["window_index"].max()) + 1
    support = trajectory_matrix.groupby(CUSTOMER_ID, sort=False).agg(
        observed_windows=("observed_exposure_days", lambda v: int(v.gt(0).sum())),
        active_windows=("purchase_count", lambda v: int(v.fillna(0).gt(0).sum())),
    )
    curves = trajectory_matrix.pivot(
        index=CUSTOMER_ID, columns="window_index", values=rate_column
    ).reindex(columns=range(window_count))
    values = curves.to_numpy(dtype=float)
    eligible = (
        np.isfinite(values).all(axis=1)
        & support["observed_windows"].reindex(curves.index).eq(window_count).to_numpy()
    )
    shape = np.full_like(values, np.nan, dtype=float)
    statuses: list[str] = []
    for index, row in enumerate(values):
        if not eligible[index]:
            statuses.append("insufficient_observed_windows")
            continue
        standard_deviation = float(np.std(row, ddof=0))
        if standard_deviation <= np.finfo(float).eps:
            shape[index] = 0.0
            statuses.append("constant_curve")
        else:
            shape[index] = (row - float(np.mean(row))) / standard_deviation
            statuses.append("standardized_shape")
    result = pd.DataFrame(
        shape,
        index=curves.index,
        columns=[f"shape_window_{i}" for i in range(window_count)],
    ).reset_index()
    result["cluster_eligible"] = eligible
    result["shape_transform_status"] = statuses
    result["active_purchase_windows"] = support["active_windows"].reindex(
        curves.index
    ).to_numpy()
    return result


def compare_static_dynamic_segments(
    static_segments: pd.DataFrame,
    trajectory_assignments: pd.DataFrame,
) -> dict[str, Any]:
    """Compare historically valid static labels with assigned dynamic clusters."""
    _validate_customer_rows(static_segments)
    _validate_customer_rows(trajectory_assignments)
    static_column = next(
        (
            column
            for column in ("Hist_Segment", "hist_segment", "static_segment")
            if column in static_segments
        ),
        None,
    )
    if static_column is None:
        raise ValueError("static_segments must include a historical segment label.")
    merged = static_segments[[CUSTOMER_ID, static_column]].merge(
        trajectory_assignments[[CUSTOMER_ID, "trajectory_cluster_id"]],
        on=CUSTOMER_ID,
        how="inner",
        validate="one_to_one",
    )
    assigned = merged.dropna(
        subset=[static_column, "trajectory_cluster_id"]
    ).copy()
    if assigned.empty:
        return {
            "comparable_customers": 0,
            "normalized_mutual_information": None,
            "adjusted_rand_index": None,
            "cross_tabulation": [],
        }
    table = pd.crosstab(
        assigned[static_column].astype(str),
        assigned["trajectory_cluster_id"].astype(int),
    )
    return {
        "comparable_customers": int(len(assigned)),
        "normalized_mutual_information": float(
            normalized_mutual_info_score(
                assigned[static_column].astype(str),
                assigned["trajectory_cluster_id"].astype(int),
            )
        ),
        "adjusted_rand_index": float(
            adjusted_rand_score(
                assigned[static_column].astype(str),
                assigned["trajectory_cluster_id"].astype(int),
            )
        ),
        "cross_tabulation": [
            {
                "static_segment": str(segment),
                "trajectory_cluster_id": int(cluster),
                "customers": int(table.loc[segment, cluster]),
            }
            for segment in table.index
            for cluster in table.columns
        ],
    }
