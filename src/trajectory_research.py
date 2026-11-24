"""Reproducible feasibility and retrospective association analysis.

This module keeps future outcomes separate from history features and never
refits saved Purchase Clock or spending models.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, pointbiserialr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.behavior_monitor import prepare_purchase_events
from src.customer_trajectories import (
    CUSTOMER_ID,
    GROSS_REVENUE,
    PURCHASE_DATE,
    TrajectoryConfig,
    build_customer_trajectory_matrix,
    calculate_trajectory_features,
)
from src.temporal_framework import HORIZON_SPLIT_SPECS

TRAJECTORY_ANALYSIS_VERSION = "customer-trajectory-analysis-v2"


def _bh_adjust(p_values: Sequence[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p-values, returned in input order."""
    values = np.asarray(p_values, dtype=float)
    if not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("p_values must be finite values in [0, 1].")
    if not len(values):
        return []
    order = np.argsort(values)
    ranked = values[order] * len(values) / np.arange(1, len(values) + 1)
    adjusted_sorted = np.minimum.accumulate(ranked[::-1])[::-1].clip(0, 1)
    adjusted = np.empty_like(adjusted_sorted)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


def _finite_quantiles(values: pd.Series) -> dict[str, float | None]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return {"median": None, "p25": None, "p75": None}
    return {
        "median": float(numeric.median()),
        "p25": float(numeric.quantile(0.25)),
        "p75": float(numeric.quantile(0.75)),
    }


def build_trajectory_feasibility_report(
    purchase_events: pd.DataFrame,
    *,
    config: TrajectoryConfig | None = None,
    split_specs: Mapping[int, Mapping[str, pd.Timestamp]] | None = None,
) -> dict[str, Any]:
    """Audit customer coverage at official TRAIN, VAL, and TEST cutoffs."""
    started = perf_counter()
    config = config or TrajectoryConfig()
    split_specs = split_specs or HORIZON_SPLIT_SPECS
    events = prepare_purchase_events(purchase_events)
    events = events.loc[events[GROSS_REVENUE].gt(0)].copy()
    cutoffs = {
        (int(horizon), str(role).upper(), pd.Timestamp(cutoff))
        for horizon, roles in split_specs.items()
        for role, cutoff in roles.items()
    }
    cutoff_results: list[dict[str, Any]] = []
    feasibility_rows: list[dict[str, Any]] = []
    for horizon, role, cutoff in sorted(
        cutoffs, key=lambda item: (item[0], item[2], item[1])
    ):
        historical = events.loc[events[PURCHASE_DATE].lt(cutoff)]
        matrix = build_customer_trajectory_matrix(
            historical,
            cutoff,
            window_days=config.window_days,
            lookback_days=config.lookback_days,
        )
        features = calculate_trajectory_features(matrix, config)
        customer_orders = (
            historical.groupby(CUSTOMER_ID)[ "Invoice" ]
            .nunique()
            .reindex(features[CUSTOMER_ID])
        )
        total = int(len(features))
        one_time = int(customer_orders.eq(1).sum())
        summary_count = int(features["eligible_for_summary_trajectory"].sum())
        functional_count = int(features["eligible_for_functional_analysis"].sum())
        full_curve = (
            matrix.groupby(CUSTOMER_ID)["observed_exposure_days"]
            .apply(lambda values: int(values.gt(0).sum()) == config.window_count)
            .reindex(features[CUSTOMER_ID], fill_value=False)
        )
        rolling_count = int(features["observed_windows"].gt(0).sum())
        shape_count = int(full_curve.sum())
        cutoff_results.append(
            {
                "horizon_days": int(horizon),
                "role": role,
                "cutoff_date": cutoff.date().isoformat(),
                "customer_count": total,
                "valid_invoice_count": int(len(historical)),
                "one_time_customers": one_time,
                "one_time_share": float(one_time / total) if total else None,
                "purchase_count_distribution": {
                    "min": int(customer_orders.min()) if total else None,
                    "median": float(customer_orders.median()) if total else None,
                    "p90": float(customer_orders.quantile(0.90)) if total else None,
                    "max": int(customer_orders.max()) if total else None,
                },
                "history_length_days": _finite_quantiles(
                    features["history_length_days"]
                ),
                "observed_window_counts": {
                    str(int(key)): int(value)
                    for key, value in features["observed_windows"]
                    .value_counts()
                    .sort_index()
                    .items()
                },
                "active_window_counts": {
                    str(int(key)): int(value)
                    for key, value in features["active_purchase_windows"]
                    .value_counts()
                    .sort_index()
                    .items()
                },
                "completed_gap_counts": {
                    str(int(key)): int(value)
                    for key, value in features["completed_purchase_gaps"]
                    .value_counts()
                    .sort_index()
                    .items()
                },
                "history_sufficiency_counts": {
                    str(key): int(value)
                    for key, value in features["history_sufficiency"]
                    .value_counts()
                    .items()
                },
            }
        )
        specifications = [
            (
                "Descriptive rolling-window trajectories",
                "At least one exposed window",
                rolling_count,
                "Pre-first-purchase windows are unavailable, not zero activity.",
            ),
            (
                "Summary-feature trajectory clustering",
                f">={config.min_summary_observed_windows} observed windows, "
                f">={config.min_summary_active_windows} active windows, "
                ">=1 completed gap",
                summary_count,
                "Sparse customers remain unassigned; cluster stability must be evaluated.",
            ),
            (
                "Smoothed functional trajectories",
                f"All {config.window_count} windows observed with "
                f">={config.min_functional_active_windows} active windows",
                functional_count,
                "Short customer histories and left truncation limit complete curves.",
            ),
            (
                "Functional PCA",
                f"At least {config.window_count} fully observed windows and "
                "sufficient active TRAIN curves",
                functional_count,
                "Grid-based PCA is an approximation; no specialized FDA estimator is used.",
            ),
            (
                "Incremental Purchase Clock prediction",
                "Chronologically eligible saved model predictions at downstream TRAIN cutoffs",
                0,
                "No saved model vintage is available before all official downstream TRAIN cutoffs.",
            ),
        ]
        for method, requirement, eligible, limitation in specifications:
            feasibility_rows.append(
                {
                    "horizon_days": int(horizon),
                    "role": role,
                    "cutoff_date": cutoff.date().isoformat(),
                    "method": method,
                    "minimum_observation_requirements": requirement,
                    "eligible_customers": int(eligible),
                    "total_customers": total,
                    "coverage_percentage": (
                        float(100 * eligible / total) if total else None
                    ),
                    "main_limitations": [limitation],
                }
            )
    return {
        "analysis_version": TRAJECTORY_ANALYSIS_VERSION,
        "window_days": int(config.window_days),
        "lookback_days": int(config.lookback_days),
        "cutoffs": cutoff_results,
        "feasibility": feasibility_rows,
        "runtime_ms": float((perf_counter() - started) * 1000),
        "limitations": [
            "first_observed_purchase_is_not_assumed_to_be_customer_acquisition",
            "available history is left-truncated at the dataset start",
            "eligible counts describe support, not representativeness or validity",
        ],
    }


def build_trajectory_curve_table(
    trajectory_matrix: pd.DataFrame,
    trajectory_features: pd.DataFrame,
    *,
    rate_column: str = "purchase_rate_per_observed_day",
) -> pd.DataFrame:
    """Create fixed-grid curve rows with support flags for downstream methods."""
    if rate_column not in trajectory_matrix:
        raise ValueError(f"Unknown curve rate column: {rate_column}")
    if trajectory_matrix.empty:
        return pd.DataFrame(columns=[CUSTOMER_ID, "functional_eligible"])
    window_count = int(trajectory_matrix["window_index"].max()) + 1
    pivot = trajectory_matrix.pivot(
        index=CUSTOMER_ID,
        columns="window_index",
        values=rate_column,
    ).reindex(columns=range(window_count))
    pivot.columns = [f"window_{index}" for index in range(window_count)]
    result = pivot.reset_index()
    support = trajectory_features.set_index(CUSTOMER_ID)
    result["functional_eligible"] = (
        support["eligible_for_functional_analysis"]
        .reindex(result[CUSTOMER_ID])
        .fillna(False)
        .to_numpy(dtype=bool)
    )
    return result


def build_future_purchase_outcomes(
    purchase_events: pd.DataFrame,
    customer_ids: Sequence[int],
    cutoff_date: Any,
    horizon_days: int,
    dataset_end: Any,
) -> pd.DataFrame:
    """Build fully matured purchase outcomes, separate from historical features."""
    cutoff = pd.Timestamp(cutoff_date)
    end = pd.Timestamp(dataset_end)
    if cutoff.tz is not None or end.tz is not None or pd.isna(cutoff) or pd.isna(end):
        raise ValueError("cutoff_date and dataset_end must be valid naive timestamps.")
    if isinstance(horizon_days, bool) or int(horizon_days) not in {30, 60, 90}:
        raise ValueError("horizon_days must be one of 30, 60, or 90.")
    horizon_end = cutoff + pd.Timedelta(days=int(horizon_days))
    if horizon_end > end:
        raise ValueError("The requested future outcome horizon is not fully observable.")
    ids = pd.Index(customer_ids, name=CUSTOMER_ID)
    if ids.has_duplicates or ids.isna().any():
        raise ValueError("customer_ids must be unique and non-null.")
    events = prepare_purchase_events(purchase_events)
    events = events.loc[
        events[GROSS_REVENUE].gt(0)
        & events[PURCHASE_DATE].gt(cutoff)
        & events[PURCHASE_DATE].le(horizon_end)
        & events[CUSTOMER_ID].isin(ids)
    ]
    outcomes = events.groupby(CUSTOMER_ID, as_index=False).agg(
        future_purchase_count=("Invoice", "nunique"),
        future_gross_revenue=(GROSS_REVENUE, "sum"),
    )
    result = pd.DataFrame({CUSTOMER_ID: ids.to_numpy()}).merge(
        outcomes, on=CUSTOMER_ID, how="left", validate="one_to_one"
    )
    result["future_purchase_count"] = (
        result["future_purchase_count"].fillna(0).astype("int64")
    )
    result["future_gross_revenue"] = result["future_gross_revenue"].fillna(0.0)
    result["purchased_within_horizon"] = result["future_purchase_count"].gt(0).astype(
        "int64"
    )
    result["horizon_days"] = int(horizon_days)
    result["outcome_window_end"] = horizon_end
    return result


def _bootstrap_difference(
    values: np.ndarray,
    group_mask: np.ndarray,
    *,
    random_state: int,
    n_bootstrap: int,
) -> tuple[float, float]:
    group = values[group_mask]
    comparison = values[~group_mask]
    if not len(group) or not len(comparison):
        return float("nan"), float("nan")
    rng = np.random.default_rng(random_state)
    group_samples = rng.choice(group, size=(n_bootstrap, len(group)), replace=True)
    comparison_samples = rng.choice(
        comparison, size=(n_bootstrap, len(comparison)), replace=True
    )
    differences = group_samples.mean(axis=1) - comparison_samples.mean(axis=1)
    return (
        float(np.quantile(differences, 0.025)),
        float(np.quantile(differences, 0.975)),
    )


def analyze_future_purchase_associations(
    features: pd.DataFrame,
    assignments: pd.DataFrame,
    outcomes_by_horizon: Mapping[int, pd.DataFrame],
    *,
    forecast_features: pd.DataFrame | None = None,
    random_state: int = 42,
    n_bootstrap: int = 1000,
) -> dict[str, Any]:
    """Summarize historical cluster/outcome associations with uncertainty."""
    for frame, name in (
        (features, "features"),
        (assignments, "assignments"),
    ):
        if CUSTOMER_ID not in frame or frame[CUSTOMER_ID].duplicated().any():
            raise ValueError(f"{name} must contain one row per customer.")
    if n_bootstrap < 100:
        raise ValueError("n_bootstrap must be at least 100.")
    base = features.merge(assignments, on=CUSTOMER_ID, how="inner", validate="one_to_one")
    base = base.dropna(subset=["trajectory_cluster_id"]).copy()
    forecast_columns: list[str] = []
    if forecast_features is not None:
        forecast_columns = [
            column
            for column in (
                "purchase_probability",
                "personalized_expected_revenue_gbp",
            )
            if column in forecast_features
        ]
        base = base.merge(
            forecast_features[[CUSTOMER_ID, *forecast_columns]],
            on=CUSTOMER_ID,
            how="left",
            validate="one_to_one",
        )
    analyses: dict[str, Any] = {}
    for horizon, outcomes in sorted(outcomes_by_horizon.items()):
        merged = base.merge(
            outcomes, on=CUSTOMER_ID, how="inner", validate="one_to_one"
        )
        values = merged["purchased_within_horizon"].to_numpy(dtype=float)
        clusters = sorted(merged["trajectory_cluster_id"].dropna().unique())
        rows: list[dict[str, Any]] = []
        p_values: list[float] = []
        for cluster_id in clusters:
            mask = merged["trajectory_cluster_id"].eq(cluster_id).to_numpy()
            group = merged.loc[mask]
            rest = merged.loc[~mask]
            group_rate = float(group["purchased_within_horizon"].mean())
            rest_rate = float(rest["purchased_within_horizon"].mean()) if len(rest) else float("nan")
            ci_low, ci_high = _bootstrap_difference(
                values,
                mask,
                random_state=random_state + int(horizon) + int(cluster_id),
                n_bootstrap=n_bootstrap,
            )
            a = int(group["purchased_within_horizon"].sum())
            b = int(len(group) - a)
            c = int(rest["purchased_within_horizon"].sum())
            d = int(len(rest) - c)
            p_value = (
                float(fisher_exact([[a, b], [c, d]]).pvalue)
                if len(rest)
                else 1.0
            )
            p_values.append(p_value)
            row: dict[str, Any] = {
                "trajectory_cluster_id": int(cluster_id),
                "customer_count": int(len(group)),
                "future_purchase_rate": group_rate,
                "future_nonpurchase_rate": float(1 - group_rate),
                "comparison_future_purchase_rate": rest_rate,
                "purchase_rate_difference_vs_other_clusters": (
                    group_rate - rest_rate if len(rest) else None
                ),
                "difference_ci_95": (
                    [ci_low, ci_high]
                    if np.isfinite(ci_low) and np.isfinite(ci_high)
                    else None
                ),
                "fisher_exact_p_value": p_value,
                "mean_history_length_days": (
                    float(group["history_length_days"].mean())
                    if "history_length_days" in group
                    else None
                ),
                "median_history_recency_days": (
                    float(group["Recency"].median()) if "Recency" in group else None
                ),
                "mean_purchase_probability": (
                    float(group["purchase_probability"].mean())
                    if "purchase_probability" in group
                    and group["purchase_probability"].notna().any()
                    else None
                ),
                "mean_personalized_expected_revenue_gbp": (
                    float(group["personalized_expected_revenue_gbp"].mean())
                    if "personalized_expected_revenue_gbp" in group
                    and group["personalized_expected_revenue_gbp"].notna().any()
                    else None
                ),
            }
            rows.append(row)
        adjusted = _bh_adjust(p_values)
        for row, q_value in zip(rows, adjusted, strict=True):
            row["fdr_adjusted_q_value"] = float(q_value)
        analyses[str(int(horizon))] = {
            "horizon_days": int(horizon),
            "evaluated_assigned_customers": int(len(merged)),
            "clusters": rows,
            "interpretation": (
                "Retrospective association only; cluster membership is not causal, "
                "and no purchase during the observed horizon is not proof of churn."
            ),
            "multiple_testing_correction": "Benjamini-Hochberg across cluster comparisons",
        }
    return {
        "fit_role": "historical TEST association only",
        "horizons": analyses,
        "limitations": [
            "association analysis uses future outcomes only after frozen assignments",
            "customers without an assigned trajectory cluster are excluded",
            "bootstrap uncertainty does not correct selection or model-vintage bias",
        ],
    }


def analyze_trajectory_feature_outcome_associations(
    trajectory_features: pd.DataFrame,
    outcomes_by_horizon: Mapping[int, pd.DataFrame],
    *,
    feature_columns: Sequence[str],
    random_state: int = 42,
    n_bootstrap: int = 1000,
) -> dict[str, Any]:
    """Estimate retrospective point-biserial associations for supported features.

    Each feature uses its own finite, one-to-one historical TEST cohort. The
    returned confidence intervals are customer-bootstrap intervals and do not
    adjust for feature selection, confounding, or model vintage.
    """
    if CUSTOMER_ID not in trajectory_features:
        raise ValueError(f"trajectory_features must include {CUSTOMER_ID!r}.")
    if trajectory_features[CUSTOMER_ID].isna().any() or trajectory_features[
        CUSTOMER_ID
    ].duplicated().any():
        raise ValueError("trajectory_features must contain unique customers.")
    if not feature_columns or len(set(feature_columns)) != len(feature_columns):
        raise ValueError("feature_columns must be non-empty and unique.")
    missing = sorted(set(feature_columns).difference(trajectory_features.columns))
    if missing:
        raise ValueError(f"trajectory_features are missing features: {missing}")
    if n_bootstrap < 100:
        raise ValueError("n_bootstrap must be at least 100.")
    for column in feature_columns:
        lowered = column.lower()
        if any(
            token in lowered
            for token in (
                "future",
                "target",
                "purchased_",
                "next_purchase",
                "expected_revenue",
            )
        ):
            raise ValueError(f"Outcome-derived feature is forbidden: {column}")

    results: dict[str, Any] = {}
    for horizon, outcomes in sorted(outcomes_by_horizon.items()):
        if CUSTOMER_ID not in outcomes or "purchased_within_horizon" not in outcomes:
            raise ValueError("Outcome data must include customer ID and binary label.")
        if outcomes[CUSTOMER_ID].duplicated().any():
            raise ValueError("Outcome rows must be unique by customer.")
        merged = trajectory_features[
            [CUSTOMER_ID, *feature_columns]
        ].merge(
            outcomes[[CUSTOMER_ID, "purchased_within_horizon"]],
            on=CUSTOMER_ID,
            how="inner",
            validate="one_to_one",
        )
        rows: list[dict[str, Any]] = []
        supported_p_values: list[float] = []
        supported_indices: list[int] = []
        for index, column in enumerate(feature_columns):
            pair = merged[[column, "purchased_within_horizon"]].apply(
                pd.to_numeric, errors="coerce"
            ).dropna()
            feature = pair[column].to_numpy(dtype=float)
            label = pair["purchased_within_horizon"].to_numpy(dtype=int)
            row: dict[str, Any] = {
                "feature": column,
                "eligible_customers": int(len(pair)),
                "point_biserial_correlation": None,
                "bootstrap_ci_95": None,
                "p_value": None,
                "fdr_adjusted_q_value": None,
            }
            if (
                len(pair) >= 30
                and np.unique(feature).size > 1
                and np.unique(label).size == 2
                and np.isin(label, [0, 1]).all()
            ):
                correlation, p_value = pointbiserialr(label, feature)
                rng = np.random.default_rng(
                    random_state + int(horizon) * 100 + index
                )
                sampled = rng.integers(0, len(pair), size=(n_bootstrap, len(pair)))
                sampled_features = feature[sampled]
                sampled_labels = label[sampled].astype(float)
                centered_features = sampled_features - sampled_features.mean(
                    axis=1, keepdims=True
                )
                centered_labels = sampled_labels - sampled_labels.mean(
                    axis=1, keepdims=True
                )
                numerator = np.sum(centered_features * centered_labels, axis=1)
                denominator = np.sqrt(
                    np.sum(centered_features**2, axis=1)
                    * np.sum(centered_labels**2, axis=1)
                )
                bootstrap = np.divide(
                    numerator,
                    denominator,
                    out=np.full(n_bootstrap, np.nan, dtype=float),
                    where=denominator > 0,
                )
                bootstrap = bootstrap[np.isfinite(bootstrap)]
                row.update(
                    {
                        "point_biserial_correlation": float(correlation),
                        "bootstrap_ci_95": (
                            [
                                float(np.quantile(bootstrap, 0.025)),
                                float(np.quantile(bootstrap, 0.975)),
                            ]
                            if len(bootstrap)
                            else None
                        ),
                        "p_value": float(p_value),
                    }
                )
                supported_indices.append(index)
                supported_p_values.append(float(p_value))
            rows.append(row)
        adjusted = _bh_adjust(supported_p_values)
        for index, q_value in zip(supported_indices, adjusted, strict=True):
            rows[index]["fdr_adjusted_q_value"] = float(q_value)
        results[str(int(horizon))] = {
            "horizon_days": int(horizon),
            "cohort_customers": int(len(merged)),
            "observed_purchase_rate": (
                float(merged["purchased_within_horizon"].mean())
                if len(merged)
                else None
            ),
            "feature_associations": rows,
            "multiple_testing_correction": (
                "Benjamini-Hochberg within horizon across supported features"
            ),
            "interpretation": (
                "Retrospective association only; these unadjusted feature "
                "correlations do not establish independent predictive value, "
                "causality, or permanent churn."
            ),
        }
    return {
        "fit_role": "historical TEST association only",
        "horizons": results,
        "limitations": [
            "features are measured before the fixed historical cutoff",
            "each feature's finite support may define a different sample size",
            "bootstrap intervals do not adjust for confounding or model selection",
        ],
    }


def assess_purchase_clock_vintage_availability(
    purchase_clock_metadata: Mapping[str, Any],
    *,
    downstream_train_cutoffs: Mapping[int, pd.Timestamp] | None = None,
) -> dict[str, Any]:
    """Check whether saved Purchase Clock outputs predate downstream TRAIN rows."""
    downstream_train_cutoffs = downstream_train_cutoffs or {
        int(horizon): pd.Timestamp(split["train"])
        for horizon, split in HORIZON_SPLIT_SPECS.items()
    }
    vintage = purchase_clock_metadata.get("validation_vintage", {})
    earliest_validation = vintage.get("first_usable_forecast_cutoff")
    earliest_primary = purchase_clock_metadata.get("available_for_test_by")
    earliest_candidates = [
        pd.Timestamp(value)
        for value in (earliest_validation, earliest_primary)
        if value
    ]
    earliest_available = min(earliest_candidates) if earliest_candidates else None
    results: dict[str, Any] = {}
    for horizon, cutoff in sorted(downstream_train_cutoffs.items()):
        train_cutoff = pd.Timestamp(cutoff)
        available = (
            earliest_available is not None and earliest_available < train_cutoff
        )
        results[str(int(horizon))] = {
            "downstream_train_cutoff": train_cutoff.date().isoformat(),
            "earliest_saved_prediction_vintage": (
                earliest_available.date().isoformat()
                if earliest_available is not None
                else None
            ),
            "chronologically_available": bool(available),
            "status": (
                "eligible_for_separate_vintage_audit"
                if available
                else "not_fitted_due_to_vintage_unavailability"
            ),
            "reason": (
                "A saved Purchase Clock prediction vintage is not available strictly "
                "before the downstream TRAIN cutoff."
            ),
        }
    return {
        "incremental_purchase_clock_plus_trajectory": "not_fitted_due_to_vintage_unavailability",
        "model_vintage_checks": results,
        "retrained_saved_models": False,
        "limitations": [
            "A trajectory-only TEST comparison cannot establish conditional incremental value over Purchase Clock.",
            "No saved Purchase Clock or spending model was changed or retrained.",
        ],
    }


def fit_trajectory_purchase_model(
    train_features: pd.DataFrame,
    train_outcomes: pd.DataFrame,
    validation_features: pd.DataFrame,
    validation_outcomes: pd.DataFrame,
    *,
    feature_columns: Sequence[str],
    c_candidates: Sequence[float] = (0.1, 1.0, 10.0),
) -> dict[str, Any]:
    """Fit a trajectory-only logistic model on TRAIN and select C on VAL."""
    if not feature_columns or not c_candidates:
        raise ValueError("feature_columns and c_candidates must be non-empty.")
    for column in feature_columns:
        lowered = column.lower()
        if any(
            token in lowered
            for token in (
                "future",
                "target",
                "purchased_",
                "next_purchase",
                "expected_revenue",
            )
        ):
            raise ValueError(f"Outcome-derived feature is forbidden: {column}")

    def align(
        features: pd.DataFrame, outcomes: pd.DataFrame, role: str
    ) -> tuple[pd.DataFrame, np.ndarray]:
        if CUSTOMER_ID not in features or CUSTOMER_ID not in outcomes:
            raise ValueError(f"{role} requires customer identifiers.")
        if features[CUSTOMER_ID].duplicated().any() or outcomes[
            CUSTOMER_ID
        ].duplicated().any():
            raise ValueError(f"{role} rows must be unique by customer.")
        missing = sorted(set(feature_columns).difference(features.columns))
        if missing:
            raise ValueError(f"{role} is missing features: {missing}")
        merged = features[[CUSTOMER_ID, *feature_columns]].merge(
            outcomes[[CUSTOMER_ID, "purchased_within_horizon"]],
            on=CUSTOMER_ID,
            how="inner",
            validate="one_to_one",
        )
        if merged.empty:
            raise ValueError(f"{role} feature and outcome cohorts do not overlap.")
        if not set(merged["purchased_within_horizon"].unique()).issubset({0, 1}):
            raise ValueError(f"{role} outcomes must be binary and fully observed.")
        return (
            merged.loc[:, feature_columns],
            merged["purchased_within_horizon"].to_numpy(dtype=int),
        )

    x_train, y_train = align(train_features, train_outcomes, "TRAIN")
    x_validation, y_validation = align(
        validation_features, validation_outcomes, "VAL"
    )
    if np.unique(y_train).size < 2:
        raise ValueError("TRAIN outcomes must contain both classes.")
    candidates = sorted({float(value) for value in c_candidates})
    if any(not np.isfinite(value) or value <= 0 for value in candidates):
        raise ValueError("c_candidates must contain positive finite values.")
    choices: list[dict[str, float]] = []
    models: dict[float, Pipeline] = {}
    for c_value in candidates:
        model = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
                ("scaler", StandardScaler()),
                (
                    "logistic",
                    LogisticRegression(C=c_value, max_iter=1000, random_state=42),
                ),
            ]
        )
        model.fit(x_train, y_train)
        probabilities = model.predict_proba(x_validation)[:, 1]
        validation_brier = float(brier_score_loss(y_validation, probabilities))
        models[c_value] = model
        choices.append({"C": c_value, "validation_brier_score": validation_brier})
    selected_c = min(
        choices,
        key=lambda choice: (
            choice["validation_brier_score"],
            choice["C"],
        ),
    )["C"]
    return {
        "fit_role": "TRAIN",
        "selection_role": "VAL",
        "pipeline": models[selected_c],
        "selected_C": float(selected_c),
        "feature_columns": list(feature_columns),
        "training_customers": int(len(x_train)),
        "validation_customers": int(len(x_validation)),
        "validation_selection_metric": "brier_score",
        "validation_candidates": choices,
        "test_outcomes_used_for_selection_or_training": False,
    }


def predict_trajectory_purchase_probability(
    fitted_bundle: Mapping[str, Any],
    features: pd.DataFrame,
) -> pd.DataFrame:
    """Apply the frozen TRAIN pipeline to a cohort with compatible features."""
    if fitted_bundle.get("fit_role") != "TRAIN":
        raise ValueError("Trajectory predictions require a TRAIN-fitted pipeline.")
    columns = list(fitted_bundle["feature_columns"])
    missing = sorted(set(columns).difference(features.columns))
    if CUSTOMER_ID not in features or missing:
        raise ValueError(f"Prediction features are missing columns: {missing}.")
    if features[CUSTOMER_ID].duplicated().any():
        raise ValueError("Prediction rows must be unique by customer.")
    probabilities = fitted_bundle["pipeline"].predict_proba(
        features.loc[:, columns]
    )[:, 1]
    return pd.DataFrame(
        {
            CUSTOMER_ID: features[CUSTOMER_ID].to_numpy(),
            "trajectory_purchase_probability": probabilities.astype(float),
        }
    )


def compute_binary_prediction_metrics(
    outcomes: Sequence[int],
    probabilities: Sequence[float],
) -> dict[str, Any]:
    """Return proper probability metrics and top-decile ranking metrics."""
    y_true = np.asarray(outcomes, dtype=int)
    y_prob = np.asarray(probabilities, dtype=float)
    if y_true.ndim != 1 or y_prob.ndim != 1 or len(y_true) != len(y_prob):
        raise ValueError("outcomes and probabilities must be aligned vectors.")
    if len(y_true) == 0 or not set(np.unique(y_true)).issubset({0, 1}):
        raise ValueError("outcomes must be a non-empty binary vector.")
    if not np.isfinite(y_prob).all() or ((y_prob < 0) | (y_prob > 1)).any():
        raise ValueError("probabilities must be finite and within [0, 1].")
    order = np.argsort(-y_prob, kind="mergesort")
    top_count = max(1, int(np.ceil(len(y_true) * 0.10)))
    top_labels = y_true[order[:top_count]]
    calibration_error = float(abs(float(y_prob.mean()) - float(y_true.mean())))
    ece = 0.0
    edges = np.linspace(0, 1, 11)
    for index, (lower, upper) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        mask = (
            (y_prob >= lower)
            & ((y_prob < upper) if index < 9 else (y_prob <= upper))
        )
        if mask.any():
            ece += float(mask.mean()) * abs(
                float(y_prob[mask].mean()) - float(y_true[mask].mean())
            )
    unique = np.unique(y_true)
    return {
        "customer_count": int(len(y_true)),
        "positive_rate": float(y_true.mean()),
        "roc_auc": (
            float(roc_auc_score(y_true, y_prob)) if len(unique) == 2 else None
        ),
        "average_precision": (
            float(average_precision_score(y_true, y_prob))
            if int(y_true.sum()) > 0
            else None
        ),
        "brier_score": float(brier_score_loss(y_true, y_prob)),
        "log_loss": float(log_loss(y_true, y_prob, labels=[0, 1])),
        "mean_predicted_probability": float(y_prob.mean()),
        "calibration_in_the_large_absolute_error": calibration_error,
        "expected_calibration_error_10_bins": float(ece),
        "top_10_percent_customers": int(top_count),
        "top_10_percent_precision": float(top_labels.mean()),
        "top_10_percent_recall": (
            float(top_labels.sum() / y_true.sum()) if y_true.sum() else None
        ),
    }


def paired_brier_difference_interval(
    outcomes: Sequence[int],
    first_probabilities: Sequence[float],
    second_probabilities: Sequence[float],
    *,
    random_state: int = 42,
    n_bootstrap: int = 1000,
) -> dict[str, Any]:
    """Paired customer-bootstrap CI for first minus second Brier score."""
    y_true = np.asarray(outcomes, dtype=int)
    first = np.asarray(first_probabilities, dtype=float)
    second = np.asarray(second_probabilities, dtype=float)
    if not (len(y_true) == len(first) == len(second)) or not len(y_true):
        raise ValueError("Paired outcomes and predictions must align and be non-empty.")
    if n_bootstrap < 100:
        raise ValueError("n_bootstrap must be at least 100.")
    point = float(np.mean((first - y_true) ** 2) - np.mean((second - y_true) ** 2))
    rng = np.random.default_rng(random_state)
    samples = rng.integers(0, len(y_true), size=(n_bootstrap, len(y_true)))
    first_errors = (first[samples] - y_true[samples]) ** 2
    second_errors = (second[samples] - y_true[samples]) ** 2
    differences = first_errors.mean(axis=1) - second_errors.mean(axis=1)
    return {
        "difference_first_minus_second": point,
        "ci_95": [
            float(np.quantile(differences, 0.025)),
            float(np.quantile(differences, 0.975)),
        ],
        "n_customers": int(len(y_true)),
        "bootstrap_replicates": int(n_bootstrap),
        "interpretation": (
            "Negative differences favor the first probability model on Brier score; "
            "this is not a causal or conditional incremental-value estimate."
        ),
    }
