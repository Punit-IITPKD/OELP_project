"""Calibration and historical reliability diagnostics for frozen forecasts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)

ARTIFACT_VERSION = "prediction-reliability-v1"
FEATURE_SCHEMA_VERSION = "customer-forecast-features-v2"


@dataclass(frozen=True)
class ReliabilityConfig:
    """Frozen diagnostic settings; thresholds are not tuned on TEST outcomes."""

    minimum_group_support: int = 100
    bootstrap_resamples: int = 500
    random_seed: int = 20261124
    confidence_level: float = 0.95
    minimum_validation_bin_support: int = 30

    def __post_init__(self) -> None:
        if self.minimum_group_support < 1:
            raise ValueError("minimum_group_support must be positive.")
        if self.bootstrap_resamples < 1:
            raise ValueError("bootstrap_resamples must be positive.")
        if not 0.0 < self.confidence_level < 1.0:
            raise ValueError("confidence_level must be between 0 and 1.")
        if self.minimum_validation_bin_support < 1:
            raise ValueError("minimum_validation_bin_support must be positive.")


DEFAULT_CONFIG = ReliabilityConfig()


def _probability_outcome_arrays(
    predictions: Sequence[float] | np.ndarray,
    outcomes: Sequence[int] | np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    predicted = np.asarray(predictions, dtype=float).reshape(-1)
    observed = np.asarray(outcomes, dtype=float).reshape(-1)
    if predicted.size == 0 or predicted.shape != observed.shape:
        raise ValueError("Predictions and outcomes must be non-empty and equally sized.")
    if not np.isfinite(predicted).all() or not np.isfinite(observed).all():
        raise ValueError("Predictions and outcomes must be finite.")
    if ((predicted < 0.0) | (predicted > 1.0)).any():
        raise ValueError("Predicted probabilities must be in [0, 1].")
    if not np.isin(observed, [0.0, 1.0]).all():
        raise ValueError("Observed purchase outcomes must be binary.")
    return predicted, observed.astype(np.int8, copy=False)


def _validated_edges(bin_edges: Sequence[float]) -> np.ndarray:
    edges = np.asarray(bin_edges, dtype=float).reshape(-1)
    if (
        edges.size < 2
        or not np.isfinite(edges).all()
        or (np.diff(edges) <= 0.0).any()
        or edges[0] > 0.0
        or edges[-1] < 1.0
    ):
        raise ValueError("Bin edges must be increasing, finite, and cover [0, 1].")
    return edges


def compute_calibration_bins(
    predicted_probabilities: Sequence[float] | np.ndarray,
    observed_outcomes: Sequence[int] | np.ndarray,
    bin_edges: Sequence[float],
) -> pd.DataFrame:
    """Return vectorized calibration counts and observed/predicted means."""
    predicted, observed = _probability_outcome_arrays(
        predicted_probabilities, observed_outcomes
    )
    edges = _validated_edges(bin_edges)
    # right-sided insertion keeps internal boundaries in the higher bin;
    # probability 1 is explicitly assigned to the final bin.
    indices = np.searchsorted(edges, predicted, side="right") - 1
    indices = np.clip(indices, 0, len(edges) - 2)
    number_of_bins = len(edges) - 1
    counts = np.bincount(indices, minlength=number_of_bins)
    predicted_sums = np.bincount(indices, weights=predicted, minlength=number_of_bins)
    outcome_sums = np.bincount(indices, weights=observed, minlength=number_of_bins)
    mean_predicted = np.divide(
        predicted_sums,
        counts,
        out=np.full(number_of_bins, np.nan, dtype=float),
        where=counts > 0,
    )
    observed_rate = np.divide(
        outcome_sums,
        counts,
        out=np.full(number_of_bins, np.nan, dtype=float),
        where=counts > 0,
    )
    gap = mean_predicted - observed_rate
    ece_component = np.where(counts > 0, counts / len(predicted) * np.abs(gap), 0.0)
    return pd.DataFrame(
        {
            "bin_index": np.arange(number_of_bins, dtype=int),
            "lower_bound": edges[:-1],
            "upper_bound": edges[1:],
            "upper_inclusive": [
                index == number_of_bins - 1 for index in range(number_of_bins)
            ],
            "customer_count": counts.astype(int),
            "mean_predicted_probability": mean_predicted,
            "observed_purchase_rate": observed_rate,
            "calibration_gap": gap,
            "ece_component": ece_component,
        }
    )


def compute_probability_metrics(
    predictions: Sequence[float] | np.ndarray,
    outcomes: Sequence[int] | np.ndarray,
    bin_edges: Sequence[float] | None = None,
) -> dict[str, Any]:
    """Calculate proper scores and bin-dependent calibration diagnostics."""
    predicted, observed = _probability_outcome_arrays(predictions, outcomes)
    edges = _validated_edges(
        np.linspace(0.0, 1.0, 11) if bin_edges is None else bin_edges
    )
    bins = compute_calibration_bins(predicted, observed, edges)
    populated = bins.loc[bins["customer_count"] > 0]
    two_classes = np.unique(observed).size == 2
    return {
        "customer_count": int(len(predicted)),
        "brier_score": float(brier_score_loss(observed, predicted)),
        "log_loss": float(log_loss(observed, predicted, labels=[0, 1])),
        "roc_auc": float(roc_auc_score(observed, predicted)) if two_classes else None,
        "average_precision": (
            float(average_precision_score(observed, predicted)) if two_classes else None
        ),
        "average_precision_reason": (
            None if two_classes else "Only one outcome class is present."
        ),
        "expected_calibration_error": (
            float(populated["ece_component"].sum()) if len(populated) else None
        ),
        "maximum_calibration_error": (
            float(populated["calibration_gap"].abs().max()) if len(populated) else None
        ),
        "mean_predicted_probability": float(predicted.mean()),
        "observed_purchase_rate": float(observed.mean()),
        "signed_calibration_gap": float(predicted.mean() - observed.mean()),
        "bin_edges": edges.tolist(),
        "calibration_bins": bins.replace({np.nan: None}).to_dict(orient="records"),
        "calibration_note": (
            "ECE and MCE depend on these fixed bin edges and are diagnostics, "
            "not universal reliability scores."
        ),
    }


def compute_subgroup_reliability(
    evaluation_frame: pd.DataFrame,
    subgroup_columns: Sequence[str],
    config: ReliabilityConfig | Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Evaluate cutoff-time subgroups with explicit support and class handling."""
    settings = _coerce_config(config)
    required = {
        "horizon_days",
        "predicted_probability",
        "observed_outcome",
        *subgroup_columns,
    }
    missing = sorted(required.difference(evaluation_frame.columns))
    if missing:
        raise ValueError(f"Evaluation data is missing columns: {missing}")
    rows: list[dict[str, Any]] = []
    for subgroup_column in subgroup_columns:
        values = evaluation_frame[subgroup_column].astype("string").fillna("Unknown")
        for group_value in sorted(values.unique().tolist()):
            group_frame = evaluation_frame.loc[values.eq(group_value)]
            for horizon, horizon_frame in group_frame.groupby("horizon_days", sort=True):
                y = horizon_frame["observed_outcome"].to_numpy(dtype=int)
                p = horizon_frame["predicted_probability"].to_numpy(dtype=float)
                metrics = compute_probability_metrics(p, y)
                count = len(horizon_frame)
                has_two_classes = np.unique(y).size == 2
                if count < settings.minimum_group_support:
                    status = "insufficient_evaluation_support"
                    reason = (
                        f"Support {count} is below the predeclared minimum "
                        f"{settings.minimum_group_support}."
                    )
                elif not has_two_classes:
                    status = "single_outcome_class"
                    reason = "Only one outcome class is present; discrimination is undefined."
                else:
                    status = "well_supported_historical_evaluation_group"
                    reason = None
                rows.append(
                    {
                        "group_type": subgroup_column,
                        "group": str(group_value),
                        "horizon_days": int(horizon),
                        "customer_count": int(count),
                        "mean_predicted_probability": metrics[
                            "mean_predicted_probability"
                        ],
                        "observed_purchase_rate": metrics["observed_purchase_rate"],
                        "brier_score": metrics["brier_score"],
                        "average_precision": metrics["average_precision"],
                        "calibration_gap": metrics["signed_calibration_gap"],
                        "status": status,
                        "status_reason": reason,
                    }
                )
    return pd.DataFrame(rows)


def _metric_values(frame: pd.DataFrame, metric: str) -> np.ndarray:
    predicted = frame["predicted_probability"].to_numpy(dtype=float)
    observed = frame["observed_outcome"].to_numpy(dtype=float)
    if metric == "observed_purchase_rate":
        return observed
    if metric == "calibration_gap":
        # The mean of these customer-level residuals is mean(p) - mean(y).
        return predicted - observed
    if metric == "brier_score":
        return (predicted - observed) ** 2
    if metric == "mean_forecast_bias":
        required = {"predicted_revenue", "actual_revenue"}
        if not required.issubset(frame.columns):
            raise ValueError("Revenue-bias intervals require predicted_revenue and actual_revenue.")
        return frame["predicted_revenue"].to_numpy(dtype=float) - frame[
            "actual_revenue"
        ].to_numpy(dtype=float)
    raise ValueError(
        "metric must be observed_purchase_rate, calibration_gap, "
        "brier_score, or mean_forecast_bias."
    )


def estimate_group_metric_intervals(
    evaluation_frame: pd.DataFrame,
    metric: str,
    config: ReliabilityConfig | Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Bootstrap fixed-cutoff customer rows, returning percentile intervals.

    The reliability study uses one record per customer within each horizon and
    subgroup. If repeated snapshots are supplied, they must first be clustered
    into one independent customer-level record for the requested estimand.
    """
    settings = _coerce_config(config)
    required = {"customer_id", "horizon_days", "predicted_probability", "observed_outcome"}
    if not required.issubset(evaluation_frame.columns):
        raise ValueError(
            "Bootstrap data requires customer_id, horizon_days, "
            "predicted_probability, and observed_outcome."
        )
    group_columns = [
        column
        for column in ("horizon_days", "group_type", "group")
        if column in evaluation_frame.columns
    ]
    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(settings.random_seed)
    alpha = (1.0 - settings.confidence_level) / 2.0
    for group_key, frame in evaluation_frame.groupby(group_columns, dropna=False, sort=True):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        if frame["customer_id"].duplicated().any():
            raise ValueError(
                "Customer-cluster bootstrap expects one row per customer within each "
                "fixed-cutoff group; aggregate repeated snapshots first."
            )
        customer_values = _metric_values(frame, metric)
        count = len(customer_values)
        record = dict(zip(group_columns, group_key, strict=True))
        record.update(
            {
                "metric": metric,
                "customer_count": int(count),
                "confidence_level": settings.confidence_level,
                "method": "customer-level percentile bootstrap with replacement",
                "successful_bootstrap_samples": 0,
                "lower": None,
                "upper": None,
            }
        )
        if count < settings.minimum_group_support:
            record["status"] = "insufficient_evaluation_support"
            rows.append(record)
            continue
        sample_indices = rng.integers(
            0, count, size=(settings.bootstrap_resamples, count)
        )
        samples = customer_values[sample_indices].mean(axis=1)
        finite = samples[np.isfinite(samples)]
        record["successful_bootstrap_samples"] = int(len(finite))
        if len(finite):
            record["lower"] = float(np.quantile(finite, alpha))
            record["upper"] = float(np.quantile(finite, 1.0 - alpha))
            record["status"] = "estimated"
        else:
            record["status"] = "not_estimable"
        rows.append(record)
    return pd.DataFrame(rows)


def assess_distribution_support(
    customer_features: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Flag raw inputs beyond TRAIN-only quantile bounds or seen categories."""
    numeric_bounds = profile.get("numeric_bounds", {})
    categorical_values = profile.get("categorical_values", {})
    flags: list[dict[str, Any]] = []
    for feature, bounds in numeric_bounds.items():
        value = customer_features.get(feature)
        if value is None or pd.isna(value):
            continue
        number = float(value)
        lower, upper = float(bounds["lower"]), float(bounds["upper"])
        if number < lower:
            flags.append(
                {"feature": feature, "value": number, "status": "below_train_range", "bound": lower}
            )
        elif number > upper:
            flags.append(
                {"feature": feature, "value": number, "status": "above_train_range", "bound": upper}
            )
    for feature, supported in categorical_values.items():
        value = customer_features.get(feature)
        if value is not None and not pd.isna(value) and str(value) not in supported:
            flags.append(
                {
                    "feature": feature,
                    "value": str(value),
                    "status": "unseen_train_category",
                    "bound": None,
                }
            )
    return {
        "atypical_feature_count": len(flags),
        "flags": flags,
        "status": (
            "outside_typical_historical_feature_range"
            if flags
            else "within_train_reference_ranges"
        ),
        "interpretation": (
            "Distribution-support flags describe distance from TRAIN reference ranges; "
            "they are not probabilities of model failure."
        ),
    }


def build_reliability_artifact(
    validation_results: Mapping[str, Any],
    evaluation_results: Mapping[str, Any],
    config: ReliabilityConfig | Mapping[str, Any],
) -> dict[str, Any]:
    """Create a small, versioned artifact containing aggregate evidence only."""
    settings = _coerce_config(config)
    metadata = dict(evaluation_results.get("metadata", {}))
    required_metadata = {
        "purchase_clock_model_version",
        "spending_model_version",
        "forecast_cutoff",
        "TRAIN_source",
        "VAL_source",
        "TEST_source",
    }
    missing = sorted(required_metadata.difference(metadata))
    if missing:
        raise ValueError(f"Reliability metadata is missing required fields: {missing}")
    metadata.update(
        {
            "artifact_version": ARTIFACT_VERSION,
            "feature_schema_version": FEATURE_SCHEMA_VERSION,
            "supported_horizons": [30, 60, 90],
            "minimum_group_support": settings.minimum_group_support,
            "bootstrap_method": "customer-level percentile bootstrap",
            "bootstrap_resamples": settings.bootstrap_resamples,
        }
    )
    return {
        "metadata": metadata,
        "configuration": asdict(settings),
        "validation": dict(validation_results),
        "evaluation": {
            key: value for key, value in evaluation_results.items() if key != "metadata"
        },
        "uncertainty_definitions": {
            "aleatoric": "A future customer outcome remains uncertain even if the probability is correct.",
            "epistemic": "Uncertainty in fitted model parameters is not estimated by these fixed-model intervals.",
            "empirical_calibration": (
                "Bootstrap intervals quantify finite-sample uncertainty in observed "
                "group-level evaluation metrics."
            ),
        },
        "limitations": [
            "Aggregate historical evaluation is not an individual prediction guarantee.",
            "ECE and MCE depend on the selected, frozen calibration bins.",
            "TEST results are retrospective diagnostics and were not used to select methods or thresholds.",
        ],
    }


def attach_customer_reliability_context(
    customer_forecasts: pd.DataFrame,
    reliability_artifact: Mapping[str, Any],
) -> pd.DataFrame:
    """Attach matching history-group evidence without exposing TEST labels."""
    required = {"history_group", "horizon_days"}
    if not required.issubset(customer_forecasts.columns):
        raise ValueError("Customer forecasts require history_group and horizon_days.")
    subgroup_rows = reliability_artifact.get("evaluation", {}).get("subgroups", [])
    lookup = {
        (str(item["group"]), int(item["horizon_days"])): item
        for item in subgroup_rows
        if item.get("group_type") == "history_group"
    }
    attached = customer_forecasts.copy()
    contexts = []
    for row in attached.to_dict(orient="records"):
        match = lookup.get((str(row["history_group"]), int(row["horizon_days"])))
        if match is None:
            contexts.append(
                {
                    "evaluation_group_count": 0,
                    "group_brier_score": None,
                    "group_calibration_gap": None,
                    "reliability_status": "reliability_evidence_unavailable",
                }
            )
        else:
            contexts.append(
                {
                    "evaluation_group_count": int(match["customer_count"]),
                    "group_brier_score": match.get("brier_score"),
                    "group_calibration_gap": match.get("calibration_gap"),
                    "reliability_status": match["status"],
                }
            )
    return pd.concat([attached.reset_index(drop=True), pd.DataFrame(contexts)], axis=1)


def _coerce_config(
    config: ReliabilityConfig | Mapping[str, Any] | None,
) -> ReliabilityConfig:
    if config is None:
        return DEFAULT_CONFIG
    if isinstance(config, ReliabilityConfig):
        return config
    return ReliabilityConfig(**dict(config))
