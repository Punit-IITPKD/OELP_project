"""Reproducible offline evaluation for Notebook 09.

All evaluation predictions come from committed model artifacts. TEST outcomes
are joined only after predictions and validation-selected bin edges are frozen.
"""

from __future__ import annotations

import json
import platform
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src import purchase_clock as pc
from src import spending_model as sm
from src import temporal_framework as tf
from src.explainability import (
    explain_cumulative_probability,
    explain_customer_purchase_clock,
)
from src.prediction_reliability import (
    DEFAULT_CONFIG,
    ReliabilityConfig,
    build_reliability_artifact,
    compute_calibration_bins,
    compute_probability_metrics,
    compute_subgroup_reliability,
    estimate_group_metric_intervals,
)

TEST_CUTOFF = pd.Timestamp("2010-09-10")
SUPPORTED_HORIZONS = (30, 60, 90)
PURCHASE_REFERENCE_FEATURES = tuple(pc.NUMERIC_FEATURES)
SPENDING_REFERENCE_FEATURES = tuple(sm.NUMERIC_FEATURES)
REFERENCE_DEFINITION = (
    "Training-only feature medians and deterministic lexical mode, calculated "
    "from the exact saved model training split after applying its saved "
    "TRAIN-fitted segmentation transform."
)
RECENCY_QUANTILES = (1.0 / 3.0, 2.0 / 3.0)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, pd.DataFrame):
        return _json_safe(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return _json_safe(value.to_dict())
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(_json_safe(payload), indent=2, allow_nan=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _training_rows(root: Path, horizon: int) -> pd.DataFrame:
    path = root / "data" / "processed" / "temporal" / f"predictive_splits_{horizon}d.csv"
    frame = pd.read_csv(path, parse_dates=["cutoff_date"])
    if "split_role" not in frame or "TRAIN" not in set(frame["split_role"]):
        raise ValueError(f"Training rows are missing from {path}.")
    return frame.loc[frame["split_role"].eq("TRAIN")].copy()


def _feature_reference(
    features: pd.DataFrame,
    numeric_features: tuple[str, ...],
    *,
    model_version: str,
    training_cutoff: str | None,
) -> dict[str, Any]:
    if features.empty:
        raise ValueError("Cannot build a reference profile from an empty TRAIN cohort.")
    values: dict[str, Any] = {}
    numeric_bounds: dict[str, dict[str, float]] = {}
    for column in numeric_features:
        numeric = pd.to_numeric(features[column], errors="coerce")
        usable = numeric[np.isfinite(numeric)]
        if usable.empty:
            raise ValueError(f"TRAIN reference feature {column!r} has no finite values.")
        values[column] = float(usable.median())
        lower, upper = np.quantile(usable.to_numpy(dtype=float), [0.01, 0.99])
        numeric_bounds[column] = {
            "lower": float(lower),
            "upper": float(upper),
            "lower_quantile": 0.01,
            "upper_quantile": 0.99,
        }
    categories: dict[str, list[str]] = {}
    for column in ("Hist_Segment",):
        if column not in features:
            continue
        series = features[column].dropna().astype(str)
        if series.empty:
            continue
        counts = series.value_counts()
        mode_values = sorted(counts.index[counts.eq(counts.max())].tolist())
        values[column] = mode_values[0]
        categories[column] = sorted(series.unique().tolist())
    values["_definition"] = REFERENCE_DEFINITION
    return {
        "model_version": model_version,
        "training_cutoff": training_cutoff,
        "training_customers": int(features[pc.CUSTOMER_ID].nunique()),
        "source_role": "TRAIN",
        "reference_values": values,
        "numeric_bounds": numeric_bounds,
        "categorical_values": categories,
        "quantile_definition": "linear 1st and 99th percentiles calculated from TRAIN only",
    }


def build_reference_profile(
    root: str | Path,
    purchase_bundle: dict[str, Any],
    spending_bundle: dict[str, Any],
) -> dict[str, Any]:
    """Create TRAIN-only reference values and support ranges for each model."""
    project_root = Path(root)
    purchase_metadata = purchase_bundle.get("metadata", {})
    purchase_train = _training_rows(project_root, 90)
    purchase_inputs = purchase_train.loc[:, list(sm.BASE_FEATURE_COLUMNS)].drop(
        columns=["Hist_Cluster_id", "Hist_Segment"], errors="ignore"
    )
    purchase_inputs = pc._apply_bundle_segmentation(purchase_bundle, purchase_inputs)
    purchase_profile = _feature_reference(
        purchase_inputs,
        PURCHASE_REFERENCE_FEATURES,
        model_version=str(purchase_metadata.get("model_version")),
        training_cutoff=purchase_metadata.get("training_cutoff"),
    )
    purchase_profile["reference_values"]["_definition"] = REFERENCE_DEFINITION

    spending_profiles: dict[str, Any] = {}
    for horizon in SUPPORTED_HORIZONS:
        training = _training_rows(project_root, horizon)
        inputs = training.loc[:, list(sm.BASE_FEATURE_COLUMNS)].drop(
            columns=["Hist_Cluster_id", "Hist_Segment"], errors="ignore"
        )
        segmented = sm.apply_spending_segmentation(
            spending_bundle, inputs, horizon
        )
        horizon_model = spending_bundle["horizon_models"].get(
            horizon, spending_bundle["horizon_models"].get(str(horizon), {})
        )
        horizon_profile = _feature_reference(
            segmented,
            SPENDING_REFERENCE_FEATURES,
            model_version=str(spending_bundle.get("metadata", {}).get("model_version")),
            training_cutoff=(
                pd.Timestamp(training["cutoff_date"].iloc[0]).date().isoformat()
                if len(training) and "cutoff_date" in training
                else None
            ),
        )
        horizon_profile["horizon_days"] = horizon
        horizon_profile["reference_values"]["_definition"] = REFERENCE_DEFINITION
        horizon_profile["selected_alpha"] = horizon_model.get(
            "personalized_conditional", {}
        ).get("alpha")
        spending_profiles[str(horizon)] = horizon_profile

    training_recency = pd.to_numeric(purchase_inputs["Recency"], errors="coerce").dropna()
    recency_edges = np.quantile(
        training_recency.to_numpy(dtype=float), RECENCY_QUANTILES
    ).tolist()
    return {
        "artifact_version": "prediction-reliability-reference-v1",
        "feature_schema_version": "customer-forecast-features-v2",
        "forecast_cutoff": TEST_CUTOFF.date().isoformat(),
        "reference_profile_definition": REFERENCE_DEFINITION,
        "purchase_clock": purchase_profile,
        "spending": spending_profiles,
        "recency_band_edges": [float(value) for value in recency_edges],
        "recency_band_source": (
            "TRAIN-only one-third and two-thirds empirical quantiles from the "
            "purchase-clock TRAIN cohort."
        ),
    }


def _validation_features(
    root: Path,
    orders: pd.DataFrame,
    horizon: int,
) -> tuple[pd.DataFrame, str, int]:
    """Get a leakage-safe VAL feature cohort available before TEST."""
    if horizon == 30:
        source_horizon, cutoff = 30, pd.Timestamp("2010-08-01")
    elif horizon == 60:
        source_horizon, cutoff = 60, pd.Timestamp("2010-07-01")
    else:
        # The final 90-day model's June validation outcomes were not mature
        # until August 30. Use only the earlier Jan/Apr validation-vintage
        # model's July 1 probability distribution to choose the 90-day bins.
        source_horizon, cutoff = 60, pd.Timestamp("2010-07-01")
    split_path = (
        root
        / "data"
        / "processed"
        / "temporal"
        / f"predictive_splits_{source_horizon}d.csv"
    )
    split = pd.read_csv(split_path, parse_dates=["cutoff_date"])
    val = split.loc[
        split["split_role"].eq("VAL") & split["cutoff_date"].eq(cutoff)
    ]
    if val.empty:
        raise ValueError(f"No eligible validation cohort exists for {horizon}-day bins.")
    all_features = tf.compute_historical_features(orders, cutoff)
    ids = set(pd.to_numeric(val[pc.CUSTOMER_ID], errors="raise").astype(int))
    selected = all_features.loc[
        pd.to_numeric(all_features[pc.CUSTOMER_ID], errors="raise").astype(int).isin(ids)
    ]
    if len(selected) != len(ids):
        raise AssertionError("Validation feature and split cohorts do not align.")
    return (
        selected.loc[:, list(sm.BASE_FEATURE_COLUMNS)].reset_index(drop=True),
        cutoff.date().isoformat(),
        len(ids),
    )


def _choose_calibration_edges(
    validation_probabilities: np.ndarray,
    config: ReliabilityConfig,
) -> dict[str, Any]:
    """Choose fixed bins using validation probability support only."""
    probabilities = np.asarray(validation_probabilities, dtype=float).reshape(-1)
    if probabilities.size == 0 or not np.isfinite(probabilities).all():
        raise ValueError("Validation predictions for bin selection must be finite and non-empty.")
    candidates: dict[str, np.ndarray] = {
        "equal_width_10": np.linspace(0.0, 1.0, 11),
    }
    quantiles = np.quantile(probabilities, np.linspace(0.0, 1.0, 11))
    quantile_edges = np.unique(np.concatenate(([0.0], quantiles, [1.0])))
    if len(quantile_edges) >= 2:
        candidates["validation_quantile"] = quantile_edges

    candidate_scores: list[dict[str, Any]] = []
    for name, edges in candidates.items():
        counts = compute_calibration_bins(
            probabilities, np.zeros(len(probabilities), dtype=int), edges
        )["customer_count"].to_numpy(dtype=int)
        populated = counts[counts > 0]
        candidate_scores.append(
            {
                "name": name,
                "edges": edges.tolist(),
                "bin_counts": counts.tolist(),
                "empty_bins": int((counts == 0).sum()),
                "minimum_populated_bin_support": (
                    int(populated.min()) if len(populated) else 0
                ),
                "meets_minimum_support": bool(
                    len(populated)
                    and int(populated.min()) >= config.minimum_validation_bin_support
                ),
            }
        )
    selected = max(
        candidate_scores,
        key=lambda item: (
            item["minimum_populated_bin_support"],
            -item["empty_bins"],
            item["name"] == "validation_quantile",
        ),
    )
    return {
        "selected_method": selected["name"],
        "bin_edges": selected["edges"],
        "validation_customer_count": int(len(probabilities)),
        "validation_outcomes_used_for_selection": False,
        "minimum_validation_bin_support": config.minimum_validation_bin_support,
        "selection_rule": (
            "Maximize the minimum populated-bin support on validation probabilities; "
            "tie-break by fewer empty bins, then prefer validation quantiles."
        ),
        "selected_candidate": selected,
        "candidate_comparison": candidate_scores,
    }


def _load_outcomes(root: Path, horizon: int) -> pd.DataFrame:
    path = (
        root
        / "data"
        / "processed"
        / "temporal"
        / f"predictive_splits_{horizon}d.csv"
    )
    frame = pd.read_csv(path, parse_dates=["cutoff_date"])
    test = frame.loc[frame["split_role"].eq("TEST")].copy()
    required = [
        pc.CUSTOMER_ID,
        "cutoff_date",
        f"Purchased_{horizon}d",
        f"FutureOrders_{horizon}d",
        f"FutureRevenue_{horizon}d",
    ]
    missing = sorted(set(required).difference(test.columns))
    if missing:
        raise ValueError(f"TEST outcomes in {path} are missing {missing}.")
    return test.loc[:, required].rename(
        columns={
            f"Purchased_{horizon}d": "observed_outcome",
            f"FutureOrders_{horizon}d": "actual_future_orders",
            f"FutureRevenue_{horizon}d": "actual_revenue",
        }
    )


def _history_group(frequency: pd.Series) -> pd.Series:
    values = pd.to_numeric(frequency, errors="coerce")
    return pd.Series(
        np.select(
            [values.eq(1), values.between(2, 4), values.ge(5)],
            [
                "Exactly one purchase",
                "Two to four purchases",
                "Five or more purchases",
            ],
            default="Unknown history",
        ),
        index=frequency.index,
        dtype="string",
    )


def _recency_bands(values: pd.Series, edges: list[float]) -> pd.Series:
    bins = np.searchsorted(np.asarray(edges, dtype=float), values.to_numpy(dtype=float), side="right")
    labels = np.asarray(
        ["TRAIN recency band 1", "TRAIN recency band 2", "TRAIN recency band 3"],
        dtype=object,
    )
    return pd.Series(labels[bins], index=values.index, dtype="string")


def _probability_bin_labels(
    probabilities: np.ndarray, edges: list[float]
) -> tuple[np.ndarray, np.ndarray]:
    boundaries = np.asarray(edges, dtype=float)
    indices = np.searchsorted(boundaries, probabilities, side="right") - 1
    indices = np.clip(indices, 0, len(boundaries) - 2)
    labels = np.asarray([f"Bin {i + 1:02d}" for i in indices], dtype=object)
    return indices, labels


def _revenue_metrics(
    prediction_frame: pd.DataFrame,
    outcome_frame: pd.DataFrame,
    horizon: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    joined = prediction_frame.merge(
        outcome_frame,
        on=[pc.CUSTOMER_ID, "cutoff_date"],
        how="inner",
        validate="one_to_one",
    )
    if len(joined) != len(prediction_frame):
        raise AssertionError(f"Revenue TEST outcomes do not align for {horizon} days.")
    model_columns = (
        (
            "Historical spending-rate",
            f"historical_rate_expected_{horizon}d",
        ),
        ("Segment-aware two-stage", f"segment_expected_revenue_{horizon}d"),
        ("Personalized two-stage", f"personalized_expected_revenue_{horizon}d"),
    )
    overall: list[dict[str, Any]] = []
    by_history: list[dict[str, Any]] = []
    large_spender: list[dict[str, Any]] = []
    actual = joined["actual_revenue"].to_numpy(dtype=float)
    top_threshold = float(np.quantile(actual, 0.99))
    top_mask = actual >= top_threshold
    for model_name, prediction_column in model_columns:
        predicted = joined[prediction_column].to_numpy(dtype=float)
        metrics = sm.evaluate_expected_revenue(actual, predicted)
        row = {
            "model": model_name,
            "horizon_days": horizon,
            "split_role": "TEST",
            "n_customers": int(len(joined)),
            "mae": metrics["mae"],
            "rmse": metrics["rmse"],
            "mean_forecast_bias": metrics["mean_forecast_bias"],
            "total_predicted_revenue": float(predicted.sum()),
            "total_actual_revenue": float(actual.sum()),
            "total_revenue_bias": float(predicted.sum() - actual.sum()),
            "portfolio_revenue_bias_ratio": (
                float((predicted.sum() - actual.sum()) / actual.sum())
                if actual.sum() > 0
                else None
            ),
        }
        overall.append(row)
        for group, frame in joined.groupby("history_group", dropna=False, sort=True):
            group_actual = frame["actual_revenue"].to_numpy(dtype=float)
            group_predicted = frame[prediction_column].to_numpy(dtype=float)
            group_metrics = sm.evaluate_expected_revenue(group_actual, group_predicted)
            by_history.append(
                {
                    "model": model_name,
                    "horizon_days": horizon,
                    "history_group": str(group),
                    "customer_count": int(len(frame)),
                    "mae": group_metrics["mae"],
                    "rmse": group_metrics["rmse"],
                    "mean_forecast_bias": group_metrics["mean_forecast_bias"],
                    "total_predicted_revenue": float(group_predicted.sum()),
                    "total_actual_revenue": float(group_actual.sum()),
                    "total_revenue_bias": float(group_predicted.sum() - group_actual.sum()),
                }
            )
        retained = ~top_mask
        large_spender.append(
            {
                "model": model_name,
                "horizon_days": horizon,
                "large_spender_definition": "actual TEST revenue at or above the cohort 99th percentile",
                "actual_revenue_threshold": top_threshold,
                "large_spender_count": int(top_mask.sum()),
                "all_customers": {
                    "mae": metrics["mae"],
                    "rmse": metrics["rmse"],
                    "mean_forecast_bias": metrics["mean_forecast_bias"],
                },
                "excluding_large_spenders": {
                    "customer_count": int(retained.sum()),
                    **sm.evaluate_expected_revenue(
                        actual[retained], predicted[retained]
                    ),
                },
                "interpretation": (
                    "Retrospective error sensitivity only; this TEST-defined group "
                    "was not used to select the forecast or reliability thresholds."
                ),
            }
        )
    return overall, by_history, large_spender


def _bootstrap_reliability_intervals(
    evaluation_frame: pd.DataFrame,
    subgroup_columns: tuple[str, ...],
    config: ReliabilityConfig,
) -> list[dict[str, Any]]:
    output: list[pd.DataFrame] = []
    all_rows = evaluation_frame.copy()
    all_rows["group_type"] = "overall"
    all_rows["group"] = "All test customers"
    group_frames = [all_rows]
    for subgroup in subgroup_columns:
        current = evaluation_frame.copy()
        current["group_type"] = subgroup
        current["group"] = current[subgroup].astype("string").fillna("Unknown")
        group_frames.append(current)
    for frame in group_frames:
        for metric in ("observed_purchase_rate", "calibration_gap", "brier_score"):
            output.append(estimate_group_metric_intervals(frame, metric, config))
    revenue_models = (
        ("Historical spending-rate", "historical_rate_expected"),
        ("Segment-aware two-stage", "segment_expected_revenue"),
        ("Personalized two-stage", "personalized_expected_revenue"),
    )
    for model_name, column_prefix in revenue_models:
        for group_type, group_values in (
            ("overall", pd.Series("All test customers", index=evaluation_frame.index)),
            ("history_group", evaluation_frame["history_group"].astype("string")),
        ):
            revenue_frame = evaluation_frame.copy()
            revenue_frame["group_type"] = group_type
            revenue_frame["group"] = group_values.fillna("Unknown").astype("string")
            revenue_frame["predicted_revenue"] = revenue_frame[
                f"{column_prefix}_{int(evaluation_frame['horizon_days'].iloc[0])}d"
            ]
            # Each row is one horizon, so use its matching fitted revenue prediction.
            for horizon, horizon_frame in revenue_frame.groupby("horizon_days", sort=True):
                horizon_frame = horizon_frame.copy()
                horizon_frame["predicted_revenue"] = horizon_frame[
                    f"{column_prefix}_{int(horizon)}d"
                ]
                intervals = estimate_group_metric_intervals(
                    horizon_frame, "mean_forecast_bias", config
                )
                intervals["revenue_model"] = model_name
                output.append(intervals)
    combined = pd.concat(output, ignore_index=True)
    return combined.to_dict(orient="records")


def run_reliability_analysis(
    project_root: str | Path = ".",
    config: ReliabilityConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    """Build and save the frozen reliability artifact from committed data/models."""
    root = Path(project_root).resolve()
    timings: dict[str, float] = {}
    overall_started = time.perf_counter()
    started = time.perf_counter()
    purchase_bundle = pc.load_purchase_clock_artifacts(root / "models" / "purchase_clock")
    spending_bundle = sm.load_spending_artifacts(root / "models" / "spending_model")
    validation_bundle = pc.load_purchase_clock_artifacts(
        root / "models" / "purchase_clock" / "validation_vintage"
    )
    timings["saved_model_loading_ms"] = (time.perf_counter() - started) * 1000.0

    orders_path = root / "data" / "processed" / "temporal" / "orders.csv"
    orders = pd.read_csv(orders_path, parse_dates=["PurchaseDate"])
    started = time.perf_counter()
    test_features = tf.compute_historical_features(orders, TEST_CUTOFF)
    test_model_features = test_features.loc[:, list(sm.BASE_FEATURE_COLUMNS)]
    timings["test_feature_construction_ms"] = (time.perf_counter() - started) * 1000.0
    if test_features[pc.CUSTOMER_ID].duplicated().any():
        raise AssertionError("TEST feature cohort must contain one row per customer.")

    started = time.perf_counter()
    prepared_purchase_features = pc._apply_bundle_segmentation(
        purchase_bundle, test_model_features
    )
    purchase_predictions = pc.predict_purchase_clock(
        purchase_bundle, test_model_features
    )
    timings["batch_hazard_inference_3373_ms"] = (time.perf_counter() - started) * 1000.0
    revenue_predictions = sm.predict_expected_revenue(
        spending_bundle, test_model_features, purchase_predictions
    )
    prediction_frame = (
        test_model_features.loc[:, [pc.CUSTOMER_ID, pc.CUTOFF_COL]]
        .merge(
            purchase_predictions.drop(
                columns=["Hist_Cluster_id", "Hist_Segment", "history_group"],
                errors="ignore",
            ),
            on=[pc.CUSTOMER_ID, pc.CUTOFF_COL],
            how="inner",
            validate="one_to_one",
        )
        .merge(
            revenue_predictions.drop(
                columns=[
                    f"purchase_probability_{horizon}d"
                    for horizon in SUPPORTED_HORIZONS
                ],
                errors="ignore",
            ),
            on=[pc.CUSTOMER_ID, pc.CUTOFF_COL],
            how="inner",
            validate="one_to_one",
            suffixes=("", "_revenue"),
        )
    )
    if len(prediction_frame) != len(test_features):
        raise AssertionError("TEST prediction joins must preserve every eligible customer.")

    reference_profile = build_reference_profile(root, purchase_bundle, spending_bundle)
    purchase_reference = reference_profile["purchase_clock"]["reference_values"]
    validation_predictions: dict[int, np.ndarray] = {}
    validation_selection: dict[str, Any] = {}
    for horizon in SUPPORTED_HORIZONS:
        features, cutoff, validation_count = _validation_features(root, orders, horizon)
        validation_model_features = pc._apply_bundle_segmentation(
            validation_bundle, features
        )
        prediction = pc.predict_purchase_clock(validation_bundle, features)
        probability_column = f"personalized_P{horizon}"
        probabilities = prediction[probability_column].to_numpy(dtype=float)
        validation_predictions[horizon] = probabilities
        validation_selection[str(horizon)] = {
            "validation_cutoff": cutoff,
            "validation_customer_count": validation_count,
            "validation_vintage_model_version": validation_bundle.get("metadata", {}).get(
                "model_version"
            ),
            "validation_vintage_available_by": validation_bundle.get("metadata", {})
            .get("validation_vintage", {})
            .get("available_for_forecasts_by"),
            "feature_cohort_alignment": int(len(validation_model_features)),
            "binning": _choose_calibration_edges(probabilities, config),
        }

    recency_edges = reference_profile["recency_band_edges"]
    test_groups = prepared_purchase_features.loc[
        :, [pc.CUSTOMER_ID, pc.CUTOFF_COL, "Hist_Segment"]
    ].copy()
    test_groups["history_group"] = _history_group(test_features["Frequency"])
    test_groups["recency_band"] = _recency_bands(
        test_features["Recency"], recency_edges
    )
    prediction_frame = prediction_frame.merge(
        test_groups,
        on=[pc.CUSTOMER_ID, pc.CUTOFF_COL],
        how="inner",
        validate="one_to_one",
    )

    evaluation_rows: list[pd.DataFrame] = []
    purchase_calibration: list[dict[str, Any]] = []
    revenue_metrics: list[dict[str, Any]] = []
    revenue_history: list[dict[str, Any]] = []
    large_spender_sensitivity: list[dict[str, Any]] = []
    bin_sensitivity: list[dict[str, Any]] = []
    model_parity: list[dict[str, Any]] = []
    for horizon in SUPPORTED_HORIZONS:
        outcomes = _load_outcomes(root, horizon)
        frame = (
            prediction_frame.merge(
                outcomes,
                on=[pc.CUSTOMER_ID, pc.CUTOFF_COL],
                how="inner",
                validate="one_to_one",
            )
        )
        if len(frame) != 3373:
            raise AssertionError(
                f"Expected 3,373 fixed-cutoff TEST customers for {horizon} days; got {len(frame)}."
            )
        prediction_column = f"personalized_P{horizon}"
        revenue_column = f"personalized_expected_revenue_{horizon}d"
        frame = frame.rename(
            columns={
                pc.CUSTOMER_ID: "customer_id",
                prediction_column: "predicted_probability",
            }
        )
        frame["horizon_days"] = horizon
        frame["predicted_revenue"] = frame[revenue_column].astype(float)
        frame["probability_band_index"], frame["probability_band"] = _probability_bin_labels(
            frame["predicted_probability"].to_numpy(dtype=float),
            validation_selection[str(horizon)]["binning"]["bin_edges"],
        )
        frame["calibration_bin"] = frame["probability_band"]
        evaluation_rows.append(frame)

        edges = validation_selection[str(horizon)]["binning"]["bin_edges"]
        outcomes_array = frame["observed_outcome"].to_numpy(dtype=int)
        probabilities = frame["predicted_probability"].to_numpy(dtype=float)
        metrics = compute_probability_metrics(probabilities, outcomes_array, edges)
        metrics.update(
            {
                "horizon_days": horizon,
                "model": "Personalized Purchase Clock",
                "forecast_cutoff": TEST_CUTOFF.date().isoformat(),
                "test_outcomes_used_for_method_selection": False,
            }
        )
        purchase_calibration.append(metrics)
        equal_width = compute_probability_metrics(
            probabilities, outcomes_array, np.linspace(0.0, 1.0, 11)
        )
        bin_sensitivity.append(
            {
                "horizon_days": horizon,
                "selected_method": validation_selection[str(horizon)]["binning"][
                    "selected_method"
                ],
                "selected_ece": metrics["expected_calibration_error"],
                "selected_mce": metrics["maximum_calibration_error"],
                "equal_width_10_ece": equal_width["expected_calibration_error"],
                "equal_width_10_mce": equal_width["maximum_calibration_error"],
                "interpretation": (
                    "TEST is used only to compare frozen diagnostic bin summaries; "
                    "the binning policy was selected using validation predictions."
                ),
            }
        )

        official = json.loads(
            (root / "data" / "metrics" / "notebook_evaluation_summary.json").read_text(
                encoding="utf-8"
            )
        )
        official_metrics = next(
            item
            for item in official["purchase_clock"]["test_metrics"]
            if item["model"] == "Personalized" and item["horizon_days"] == horizon
        )
        parity = {
            "horizon_days": horizon,
            "customer_count": int(len(frame)),
            "brier_score_current": float(
                np.mean((probabilities - outcomes_array) ** 2)
            ),
            "brier_score_official": float(official_metrics["brier_score"]),
            "mean_probability_current": float(probabilities.mean()),
            "mean_probability_official": float(
                official_metrics["mean_predicted_probability"]
            ),
            "purchased_rate_current": float(outcomes_array.mean()),
            "purchased_rate_official": float(official_metrics["actual_purchase_rate"]),
        }
        for model_key, official_key in (
            ("brier_score_current", "brier_score"),
            ("mean_probability_current", "mean_predicted_probability"),
            ("purchased_rate_current", "actual_purchase_rate"),
        ):
            if not np.isclose(
                parity[model_key],
                float(official_metrics[official_key]),
                rtol=0.0,
                atol=1.1e-6,
            ):
                raise AssertionError(
                    f"Recomputed TEST values differ from Notebook 06 for {horizon} days."
                )
        model_parity.append(parity)

        overall_revenue, history_revenue, spender_sensitivity = _revenue_metrics(
            prediction_frame, outcomes, horizon
        )
        revenue_metrics.extend(overall_revenue)
        revenue_history.extend(history_revenue)
        large_spender_sensitivity.extend(spender_sensitivity)

    evaluation_frame = pd.concat(evaluation_rows, ignore_index=True)
    subgroup_columns = (
        "history_group",
        "Hist_Segment",
        "recency_band",
        "probability_band",
        "calibration_bin",
    )
    subgroup_results = compute_subgroup_reliability(
        evaluation_frame,
        subgroup_columns,
        config,
    )
    # Preserve the validation-frozen probability bands for bootstrap strata.
    group_records = subgroup_results.to_dict(orient="records")
    started = time.perf_counter()
    bootstrap_intervals = _bootstrap_reliability_intervals(
        evaluation_frame, subgroup_columns, config
    )
    timings["bootstrap_evaluation_ms"] = (time.perf_counter() - started) * 1000.0

    interval_lookup = {
        (
            str(item.get("group_type")),
            str(item.get("group")),
            int(item.get("horizon_days")),
            str(item["metric"]),
            str(item.get("revenue_model", "")),
        ): item
        for item in bootstrap_intervals
    }
    for row in group_records:
        row["bootstrap_intervals"] = {}
        for metric in (
            "observed_purchase_rate",
            "calibration_gap",
            "brier_score",
        ):
            match = interval_lookup.get(
                (
                    str(row["group_type"]),
                    str(row["group"]),
                    int(row["horizon_days"]),
                    metric,
                    "",
                )
            )
            if match is not None:
                row["bootstrap_intervals"][metric] = {
                    "lower": match["lower"],
                    "upper": match["upper"],
                    "successful_samples": match["successful_bootstrap_samples"],
                    "status": match["status"],
                }

    revenue_history_lookup = {
        (str(row["group"]), int(row["horizon_days"])): row
        for row in group_records
        if row["group_type"] == "history_group"
    }
    for row in revenue_history:
        interval = interval_lookup.get(
            (
                "history_group",
                str(row["history_group"]),
                int(row["horizon_days"]),
                "mean_forecast_bias",
                str(row["model"]),
            )
        )
        if interval:
            row["mean_forecast_bias_interval"] = {
                "lower": interval["lower"],
                "upper": interval["upper"],
                "successful_samples": interval["successful_bootstrap_samples"],
                "status": interval["status"],
            }
        row["reliability_group_status"] = revenue_history_lookup.get(
            (str(row["history_group"]), int(row["horizon_days"])), {}
        ).get("status", "reliability_evidence_unavailable")

    for row in revenue_metrics:
        interval = interval_lookup.get(
            (
                "overall",
                "All test customers",
                int(row["horizon_days"]),
                "mean_forecast_bias",
                str(row["model"]),
            )
        )
        if interval:
            row["mean_forecast_bias_interval"] = {
                "lower": interval["lower"],
                "upper": interval["upper"],
                "successful_samples": interval["successful_bootstrap_samples"],
                "status": interval["status"],
            }

    official = json.loads(
        (root / "data" / "metrics" / "notebook_evaluation_summary.json").read_text(
            encoding="utf-8"
        )
    )
    for row in revenue_metrics:
        official_row = next(
            item
            for item in official["spending_forecast"]["test_metrics"]
            if item["split_role"] == "TEST"
            and item["horizon_days"] == row["horizon_days"]
            and item["model"] == row["model"]
        )
        for key in (
            "mae",
            "rmse",
            "mean_forecast_bias",
            "total_predicted_revenue",
            "total_actual_revenue",
        ):
            tolerance = 0.51 if key == "total_predicted_revenue" else 1.1e-6
            if not np.isclose(
                float(row[key]),
                float(official_row[key]),
                rtol=0.0,
                atol=tolerance,
            ):
                raise AssertionError(
                    f"Recomputed {row['model']} TEST {key} differs from Notebook 07."
                )

    train_source = (
        "data/processed/temporal/predictive_splits_90d.csv, split_role=TRAIN, "
        "purchase-clock training cutoff 2010-03-01."
    )
    val_source = {
        "30": "predictive_splits_30d.csv VAL at 2010-08-01; validation-vintage purchase model available by 2010-06-30.",
        "60": "predictive_splits_60d.csv VAL at 2010-07-01; validation-vintage purchase model available by 2010-06-30.",
        "90": (
            "predictive_splits_60d.csv VAL features at 2010-07-01; validation-vintage "
            "P90 probabilities only, with no validation outcomes used to choose bins."
        ),
    }
    test_source = {
        str(h): f"predictive_splits_{h}d.csv, split_role=TEST, cutoff 2010-09-10."
        for h in SUPPORTED_HORIZONS
    }
    metadata = {
        "purchase_clock_model_version": purchase_bundle["metadata"]["model_version"],
        "spending_model_version": spending_bundle["metadata"]["model_version"],
        "forecast_cutoff": TEST_CUTOFF.date().isoformat(),
        "supported_horizons": list(SUPPORTED_HORIZONS),
        "TRAIN_source": train_source,
        "VAL_source": val_source,
        "TEST_source": test_source,
        "calibration_binning_method": {
            key: value["binning"]["selected_method"]
            for key, value in validation_selection.items()
        },
        "minimum_group_support": config.minimum_group_support,
        "bootstrap_method": "fixed-cutoff customer-level percentile bootstrap",
        "bootstrap_resamples": config.bootstrap_resamples,
        "reference_profile_definition": REFERENCE_DEFINITION,
        "known_limitations": [
            "The final 90-day spending model has no eligible prospective validation vintage; TEST revenue results are retrospective.",
            "The 90-day probability-bin edges use a validation-vintage July 1 probability distribution; no validation outcomes select the bins.",
            "Fixed-model bootstrap intervals quantify empirical group-metric uncertainty, not model-parameter or individual-outcome uncertainty.",
            "Feature-range flags are TRAIN reference-support diagnostics, not model-failure probabilities.",
        ],
    }
    artifact = build_reliability_artifact(
        validation_results={
            "bin_selection_by_horizon": validation_selection,
            "selection_policy": (
                "Validation probabilities only; maximize minimum populated-bin "
                "support, then prefer fewer empty bins."
            ),
        },
        evaluation_results={
            "metadata": metadata,
            "purchase_calibration": purchase_calibration,
            "calibration_bin_sensitivity": bin_sensitivity,
            "subgroups": group_records,
            "bootstrap_intervals": bootstrap_intervals,
            "revenue": revenue_metrics,
            "revenue_by_history_group": revenue_history,
            "large_spender_sensitivity": large_spender_sensitivity,
            "model_parity": model_parity,
            "evaluation_customer_count": int(test_features[pc.CUSTOMER_ID].nunique()),
        },
        config=config,
    )

    # Profile one genuine TEST customer chosen only by lowest customer ID.
    order_for_case = test_features.sort_values(pc.CUSTOMER_ID).reset_index(drop=True)
    case = order_for_case.iloc[[0]].loc[:, list(sm.BASE_FEATURE_COLUMNS)]
    started = time.perf_counter()
    purchase_explanation = explain_customer_purchase_clock(
        purchase_bundle, case, purchase_reference
    )
    timings["single_customer_explanation_ms"] = (time.perf_counter() - started) * 1000.0
    started = time.perf_counter()
    explain_cumulative_probability(purchase_bundle, case, purchase_reference)
    timings["batched_reference_perturbations_ms"] = (time.perf_counter() - started) * 1000.0
    started = time.perf_counter()
    for calibration in purchase_calibration:
        horizon = int(calibration["horizon_days"])
        current = evaluation_frame.loc[evaluation_frame["horizon_days"].eq(horizon)]
        compute_calibration_bins(
            current["predicted_probability"],
            current["observed_outcome"],
            calibration["bin_edges"],
        )
    timings["calibration_bins_ms"] = (time.perf_counter() - started) * 1000.0
    timings["total_offline_evaluation_ms"] = (
        time.perf_counter() - overall_started
    ) * 1000.0
    timings["single_customer_batch_size"] = 1
    timings["test_hazard_batch_size"] = int(len(test_features))
    profiling = {
        "environment": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "model_versions": {
            "purchase_clock": purchase_bundle["metadata"]["model_version"],
            "spending": spending_bundle["metadata"]["model_version"],
        },
        "sample_sizes": {
            "test_customers": int(len(test_features)),
            "validation_by_horizon": {
                key: value["validation_customer_count"]
                for key, value in validation_selection.items()
            },
        },
        "timings": timings,
        "warm_api_endpoint_latency": {
            "status": "measured separately after API integration",
            "endpoints": {},
        },
    }

    metrics_dir = root / "data" / "metrics"
    model_dir = root / "models" / "prediction_reliability"
    _write_json(metrics_dir / "prediction_reliability_evaluation.json", artifact)
    _write_json(model_dir / "metadata.json", artifact["metadata"])
    _write_json(model_dir / "reference_profile.json", reference_profile)
    _write_json(metrics_dir / "prediction_reliability_profiling.json", profiling)
    return {
        "artifact": artifact,
        "reference_profile": reference_profile,
        "profiling": profiling,
        "test_features": test_features,
        "test_predictions": prediction_frame,
        "test_evaluation_frame": evaluation_frame,
        "purchase_bundle": purchase_bundle,
        "spending_bundle": spending_bundle,
        "purchase_case_explanation": purchase_explanation,
    }


def profile_warm_api_endpoints(
    project_root: str | Path = ".",
    *,
    repetitions: int = 10,
) -> dict[str, Any]:
    """Measure warm in-process API latency with FastAPI's local test client."""
    if repetitions < 1:
        raise ValueError("repetitions must be positive.")
    from fastapi.testclient import TestClient

    from api.main import app

    root = Path(project_root).resolve()
    reliability_path = root / "data" / "metrics" / "prediction_reliability_profiling.json"
    reliability = json.loads(reliability_path.read_text(encoding="utf-8"))
    test_features = tf.compute_historical_features(
        pd.read_csv(
            root / "data" / "processed" / "temporal" / "orders.csv",
            parse_dates=["PurchaseDate"],
        ),
        TEST_CUTOFF,
    )
    customer_id = int(test_features.sort_values(pc.CUSTOMER_ID).iloc[0][pc.CUSTOMER_ID])
    endpoint_paths = {
        "summary": "/api/reliability/summary",
        "calibration": "/api/reliability/calibration",
        "subgroups": "/api/reliability/subgroups",
        "revenue": "/api/reliability/revenue",
        "explanation": f"/api/customers/{customer_id}/explanation?horizon_days=30",
        "customer_reliability": f"/api/customers/{customer_id}/reliability?horizon_days=30",
    }
    timings: dict[str, Any] = {}
    with TestClient(app) as client:
        for name, path in endpoint_paths.items():
            warm = client.get(path)
            if warm.status_code != 200:
                raise AssertionError(
                    f"Cannot profile {path}: HTTP {warm.status_code} {warm.text[:300]}"
                )
            samples = []
            for _ in range(repetitions):
                started = time.perf_counter()
                response = client.get(path)
                elapsed = (time.perf_counter() - started) * 1000.0
                if response.status_code != 200:
                    raise AssertionError(
                        f"Warm request failed for {path}: HTTP {response.status_code}"
                    )
                samples.append(elapsed)
            timings[name] = {
                "path": path,
                "successful_repetitions": repetitions,
                "median_ms": float(np.median(samples)),
                "p95_ms": float(np.quantile(samples, 0.95)),
                "all_status_codes": [200] * repetitions,
                "measurement": "in-process FastAPI TestClient after one warm-up request",
            }
    reliability["warm_api_endpoint_latency"] = {
        "status": "measured",
        "measurement_environment": "in-process FastAPI TestClient",
        "endpoints": timings,
    }
    _write_json(reliability_path, reliability)
    return reliability["warm_api_endpoint_latency"]
