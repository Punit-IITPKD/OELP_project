"""Reproducible Notebook 08 evaluation on the authorized temporal cohorts."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import purchase_clock as pc
from src import temporal_framework as tf
from src.behavior_evaluation import (
    BEHAVIOR_FEATURE_FAMILIES,
    BEHAVIOR_MODEL_FEATURES,
    SelectedBehaviorModel,
    predict_nonpurchase_probability,
    select_behavior_model,
)
from src.behavior_monitor import (
    BehaviorConfig,
    DEFAULT_CONFIG,
    EWMA_LAMBDA_CANDIDATES,
    MODEL_VERSION,
    POLICY_VERSION,
    build_behavior_trajectory,
    compute_behavior_features,
    evaluate_binary_risk,
    evaluate_frozen_alert_threshold,
    paired_customer_bootstrap_difference,
    probability_metrics,
    prepare_purchase_events,
    select_alert_threshold,
)

HORIZONS = (30, 60, 90)
SPLIT_ROLES = ("TRAIN", "VAL", "TEST")
EVALUATION_VERSION = "behavior-evaluation-v1"
TARGET_COLUMNS = {
    "Customer ID",
    "cutoff_date",
    "split_role",
    "Hist_Segment",
    "Recency",
    "Frequency",
    "Monetary_Gross",
    "AOV",
    "Tenure_obs_days",
    "SpendRate_per_obs_day",
    "PurchaseRate_per_obs_day",
    "Median_Gap_days",
    "Recent_Orders",
}
BOOTSTRAP_RESAMPLES = 500


@dataclass
class BehaviorStudyResult:
    evaluation: dict[str, Any]
    metadata: dict[str, Any]
    selection: pd.DataFrame
    lambda_selection: pd.DataFrame
    comparison: pd.DataFrame
    ablations: pd.DataFrame
    subgroups: pd.DataFrame
    case_studies: pd.DataFrame
    figures: dict[str, plt.Figure]


def _json_native(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_native(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_native(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if value is pd.NA or (isinstance(value, float) and not np.isfinite(value)):
        return None
    return value


def _load_project_data(
    root: Path,
) -> tuple[pd.DataFrame, dict[int, pd.DataFrame], dict[str, Any]]:
    data_dir = root / "data" / "processed" / "temporal"
    orders = pd.read_csv(
        data_dir / "orders.csv",
        parse_dates=["PurchaseDate"],
    )
    split_metadata = json.loads(
        (data_dir / "temporal_split_metadata.json").read_text(encoding="utf-8")
    )
    split_columns = sorted(TARGET_COLUMNS)
    split_frames: dict[int, pd.DataFrame] = {}
    for horizon in HORIZONS:
        frame = pd.read_csv(
            data_dir / f"predictive_splits_{horizon}d.csv",
            usecols=split_columns,
            parse_dates=["cutoff_date"],
        )
        frame["Customer ID"] = pd.to_numeric(
            frame["Customer ID"], errors="raise"
        ).astype("int64")
        if frame.duplicated(["Customer ID", "cutoff_date"]).any():
            raise ValueError(f"{horizon}d split contains duplicate customer/cutoff rows.")
        split_frames[horizon] = frame

    for horizon, frame in split_frames.items():
        maturity = split_metadata["predictive_splits_outcome_matured"][str(horizon)]
        expected = {
            "TRAIN": pd.Timestamp(maturity["train_cutoff"]),
            "VAL": pd.Timestamp(maturity["val_cutoff"]),
            "TEST": pd.Timestamp(maturity["test_cutoff"]),
        }
        for role, cutoff in expected.items():
            observed = frame.loc[frame["split_role"].eq(role), "cutoff_date"].unique()
            if len(observed) != 1 or pd.Timestamp(observed[0]) != cutoff:
                raise ValueError(
                    f"{horizon}d {role} cutoff does not match temporal metadata."
                )
        if split_metadata["predictive_splits_outcome_matured"][str(horizon)][
            "test_cutoff"
        ] != "2010-09-10":
            raise ValueError(f"{horizon}d TEST cutoff differs from the approved holdout.")
    return orders, split_frames, split_metadata


def _split_cohort(
    splits: dict[int, pd.DataFrame],
    horizon: int,
    role: str,
) -> pd.DataFrame:
    frame = splits[horizon]
    return frame.loc[frame["split_role"].eq(role)].copy().reset_index(drop=True)


def _target_for_role(
    orders: pd.DataFrame,
    cohort: pd.DataFrame,
    horizon: int,
    dataset_end: pd.Timestamp,
) -> pd.DataFrame:
    cutoff_values = pd.to_datetime(cohort["cutoff_date"]).unique()
    if len(cutoff_values) != 1:
        raise ValueError("A temporal role must contain exactly one cutoff.")
    cutoff = pd.Timestamp(cutoff_values[0])
    result = tf.compute_future_targets(
        orders,
        cohort[["Customer ID", "cutoff_date"]],
        cutoff,
        dataset_end,
        horizons=[horizon],
    )
    label = f"Purchased_{horizon}d"
    if result[label].isna().any():
        raise ValueError(f"{horizon}d outcome at {cutoff.date()} is not fully mature.")
    return result[["Customer ID", label]].copy()


def _add_delay_ratio(
    cohort: pd.DataFrame,
    population_median_gap: float,
) -> pd.DataFrame:
    feature_columns = ["Customer ID", "cutoff_date", *pc.NUMERIC_FEATURES]
    if "Hist_Segment" in cohort:
        feature_columns.append("Hist_Segment")
    delay = pc.calculate_delay_ratio(
        cohort.loc[:, feature_columns],
        population_median_gap,
    )
    return cohort.merge(
        delay[["Customer ID", "delay_ratio"]],
        on="Customer ID",
        how="left",
        validate="one_to_one",
    )


def _feature_snapshot(
    events: pd.DataFrame,
    cutoff: pd.Timestamp,
    ewma_lambda: float,
    cache: dict[tuple[str, float], pd.DataFrame],
) -> pd.DataFrame:
    key = (pd.Timestamp(cutoff).isoformat(), float(ewma_lambda))
    if key not in cache:
        cache[key] = compute_behavior_features(
            events,
            cutoff,
            BehaviorConfig(**{**asdict(DEFAULT_CONFIG), "ewma_lambda": ewma_lambda}),
        )
    return cache[key]


def _join_behavior(
    cohort: pd.DataFrame,
    events: pd.DataFrame,
    ewma_lambda: float,
    cache: dict[tuple[str, float], pd.DataFrame],
) -> pd.DataFrame:
    cutoff = pd.Timestamp(cohort["cutoff_date"].iloc[0])
    behavior = _feature_snapshot(events, cutoff, ewma_lambda, cache)
    return cohort.merge(
        behavior,
        on=["Customer ID", "cutoff_date"],
        how="inner",
        validate="one_to_one",
        suffixes=("", "_behavior"),
    )


def _json_number(value: Any) -> float | None:
    if pd.isna(value):
        return None
    number = float(value)
    return number if np.isfinite(number) else None


def _model_metrics(
    horizon: int,
    name: str,
    outcomes: np.ndarray,
    scores: np.ndarray,
    threshold: float | None,
    *,
    probabilistic: bool,
    status: str = "evaluated_on_locked_TEST",
) -> tuple[dict[str, Any], dict[str, Any]]:
    ranking = evaluate_binary_risk(outcomes, scores, top_fraction=0.10)
    frozen_coverage: float | None = None
    frozen_false_alert_rate: float | None = None
    if threshold is None:
        pass
    else:
        frozen = evaluate_frozen_alert_threshold(outcomes, scores, threshold)
        frozen_coverage = float(frozen["alert_coverage"])
        frozen_false_alert_rate = float(frozen["false_alert_rate"])
    probability = (
        {"brier_score": None, "log_loss": None}
        if not probabilistic
        else probability_metrics(outcomes, scores)
    )
    row = {
        "horizon_days": int(horizon),
        "model": name,
        "n_customers": int(ranking["n_customers"]),
        "roc_auc": float(ranking["roc_auc"]),
        "average_precision": float(ranking["average_precision"]),
        "precision_at_budget": float(ranking["precision_at_budget"]),
        "recall_at_budget": float(ranking["recall_at_budget"]),
        "brier_score": _json_number(probability["brier_score"]),
        "log_loss": _json_number(probability["log_loss"]),
        "alert_coverage": float(ranking["alert_coverage_at_budget"]),
        "false_alert_rate": float(ranking["false_alert_rate_at_budget"]),
        "threshold": _json_number(threshold),
        "frozen_threshold_alert_coverage": frozen_coverage,
        "frozen_threshold_false_alert_rate": frozen_false_alert_rate,
        "status": status,
    }
    return row, ranking


def _ablation_selection(
    train: pd.DataFrame,
    y_train: np.ndarray,
    validation: pd.DataFrame,
    y_validation: np.ndarray,
    family: str,
) -> tuple[SelectedBehaviorModel, tuple[str, ...]]:
    omitted = set(BEHAVIOR_FEATURE_FAMILIES[family])
    features = tuple(column for column in BEHAVIOR_MODEL_FEATURES if column not in omitted)
    selected = select_behavior_model(
        train.loc[:, list(features)],
        y_train,
        validation.loc[:, list(features)],
        y_validation,
        features,
    )
    return selected, features


def _subgroup_metrics(
    horizon: int,
    model_name: str,
    outcomes: np.ndarray,
    scores: np.ndarray,
    test: pd.DataFrame,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group_type, column in (
        ("history_sufficiency", "history_sufficiency"),
        ("historical_segment", "Hist_Segment"),
    ):
        groups = test[column].fillna("Unknown").astype(str)
        for group in sorted(groups.unique()):
            mask = groups.eq(group).to_numpy()
            y = outcomes[mask]
            score = scores[mask]
            row: dict[str, Any] = {
                "horizon_days": int(horizon),
                "model": model_name,
                "group_type": group_type,
                "group": group,
                "n_customers": int(mask.sum()),
                "nonpurchase_rate": float(y.mean()) if len(y) else None,
                "roc_auc": None,
                "average_precision": None,
                "status": "evaluated",
            }
            if len(y) and np.unique(y).size == 2:
                row["roc_auc"] = float(evaluate_binary_risk(y, score)["roc_auc"])
                row["average_precision"] = float(
                    evaluate_binary_risk(y, score)["average_precision"]
                )
            else:
                row["status"] = "ranking_unavailable_one_outcome_class"
            rows.append(row)
    return rows


def _make_hypothesis_results(
    bootstrap_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    definitions = {
        "H1": (
            "Personalized gap deviation",
            "Customers whose current gap is unusually long relative to their own history are less likely to purchase soon.",
            "personalized_gap",
        ),
        "H2": (
            "Frequency deterioration",
            "A decline in recent purchasing rate relative to earlier activity contains additional predictive information.",
            "frequency_change",
        ),
        "H3": (
            "Spending deterioration",
            "A reduction in purchasing revenue rate may indicate deterioration, although spending is noisy.",
            "spending_change",
        ),
        "H4": (
            "Trajectory information",
            "The direction and persistence of behavior changes may add information beyond instantaneous inactivity.",
            "trajectory_change",
        ),
    }
    results: list[dict[str, Any]] = []
    for hypothesis, (title, statement, family) in definitions.items():
        comparisons = [
            row
            for row in bootstrap_rows
            if row["comparison"] == f"Candidate E vs E without {family}"
            and row["metric"] == "average_precision"
        ]
        positive_intervals = sum(
            row["confidence_interval_95_lower"] > 0 for row in comparisons
        )
        all_nonpositive = bool(comparisons) and all(
            row["confidence_interval_95_upper"] <= 0 for row in comparisons
        )
        if len(comparisons) == len(HORIZONS) and positive_intervals >= 2:
            status = "supported_in_multiple_horizons"
        elif all_nonpositive:
            status = "not_supported_in_evaluated_horizons"
        else:
            status = "inconclusive"
        values = ", ".join(
            f"P{row['horizon_days']} AP delta {row['difference_first_minus_second']:.3f} "
            f"(95% CI {row['confidence_interval_95_lower']:.3f} to "
            f"{row['confidence_interval_95_upper']:.3f})"
            for row in comparisons
        )
        results.append(
            {
                "hypothesis": hypothesis,
                "statement": statement,
                "status": status,
                "evidence_summary": (
                    values
                    if values
                    else "A feature-family ablation could not be estimated."
                ),
            }
        )
    direct = [
        row
        for row in bootstrap_rows
        if row["comparison"] == "Candidate E vs Personalized Purchase Clock"
        and row["metric"] == "average_precision"
    ]
    direct_values = ", ".join(
        f"P{row['horizon_days']} AP difference {row['difference_first_minus_second']:.3f} "
        f"(95% CI {row['confidence_interval_95_lower']:.3f} to "
        f"{row['confidence_interval_95_upper']:.3f})"
        for row in direct
    )
    results.append(
        {
            "hypothesis": "H5",
            "statement": "Behavior features add independent prospective information beyond the existing Purchase Clock.",
            "status": "not_assessed_candidate_F_vintage_ineligible",
            "evidence_summary": (
                "Candidate E and the existing Purchase Clock are compared on the locked TEST cohort "
                f"({direct_values}). A conditional Candidate F was not fitted because no saved Purchase Clock "
                "prediction vintage exists at the official TRAIN cutoffs; separate-model comparison cannot "
                "establish independent incremental information."
            ),
        }
    )
    return results


def _figures(
    test_frames: dict[int, pd.DataFrame],
    comparison: pd.DataFrame,
    case_studies: pd.DataFrame,
) -> dict[str, plt.Figure]:
    figures: dict[str, plt.Figure] = {}

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=False)
    for ax, horizon in zip(axes, HORIZONS):
        data = test_frames[horizon]
        values = pd.to_numeric(data["gap_deviation_score"], errors="coerce").dropna()
        ax.hist(values, bins=24, color="#436b5b", alpha=0.82)
        ax.axvline(values.median(), color="#c17e4e", linestyle="--", label="Median")
        ax.set(title=f"P{horizon} · {len(values):,} available", xlabel="Gap deviation (median/MAD)")
        ax.set_ylabel("Customers")
        ax.legend(frameon=False)
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("Personalized purchase-gap deviation at the historical TEST cutoff")
    fig.tight_layout()
    figures["gap_deviation"] = fig

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharex=True, sharey=True)
    for ax, horizon in zip(axes, HORIZONS):
        data = test_frames[horizon]
        ax.scatter(
            data["reference_order_rate"],
            data["recent_order_rate"],
            c=data["history_sufficiency"].map(
                {"sufficient": "#315a4c", "limited": "#d49a65", "insufficient": "#9daaa0"}
            ),
            s=12,
            alpha=0.55,
        )
        ax.set(title=f"P{horizon}", xlabel="Reference orders/day", ylabel="Recent orders/day")
        ax.grid(alpha=0.2)
    fig.suptitle("Observed purchase rates, exposure-adjusted and prior-smoothed")
    fig.tight_layout()
    figures["purchase_rates"] = fig

    if not case_studies.empty:
        fig, axes = plt.subplots(
            len(case_studies), 1, figsize=(10, max(3.0, 2.8 * len(case_studies))), squeeze=False
        )
        for ax, case in zip(axes[:, 0], case_studies.to_dict(orient="records")):
            ax.bar(case["trajectory"]["period_start"], case["trajectory"]["order_count"], width=20, color="#315a4c")
            ax.set_title(
                f"Customer {case['customer_id']} · {case['selection_reason']} · "
                f"descriptive only, cutoff {case['cutoff_date']}"
            )
            ax.set_ylabel("Orders / 30d")
            ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        figures["customer_trajectories"] = fig

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, metric in zip(axes, ("average_precision", "roc_auc")):
        view = comparison.loc[comparison["model"].isin(
            ["Global inactivity indicator", "Recency-only ranking", "Personalized delay ratio", "Personalized Purchase Clock", "Behavior features only"]
        )]
        for model, group in view.groupby("model"):
            ax.plot(group["horizon_days"], group[metric], marker="o", label=model)
        ax.set(xticks=HORIZONS, xlabel="Outcome horizon (days)", ylabel=metric.replace("_", " ").title())
        ax.grid(alpha=0.2)
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Locked TEST ranking comparison")
    fig.tight_layout()
    figures["baseline_comparison"] = fig

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, horizon in zip(axes, HORIZONS):
        view = comparison.loc[
            comparison["horizon_days"].eq(horizon)
            & comparison["model"].isin(
                ["Global inactivity indicator", "Recency-only ranking", "Personalized delay ratio", "Personalized Purchase Clock", "Behavior features only"]
            )
        ]
        ax.bar(
            view["model"],
            view["precision_at_budget"],
            color=["#78918a", "#a8ad78", "#d8ad5e", "#c57d5c", "#315a4c"][: len(view)],
        )
        ax.tick_params(axis="x", labelrotation=35, labelsize=8)
        ax.set(title=f"P{horizon}", ylabel="Precision in top 10%" if horizon == HORIZONS[0] else "")
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("Top-decile alert-budget performance (ranking only)")
    fig.tight_layout()
    figures["alert_budget"] = fig

    test = test_frames[90]
    counts = test["history_sufficiency"].value_counts().reindex(
        ["sufficient", "limited", "insufficient"], fill_value=0
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(counts.index, counts.values, color=["#315a4c", "#d8ad5e", "#aeb8b1"])
    ax.set(title="History support in the P90 TEST cohort", ylabel="Customers")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    figures["history_sufficiency"] = fig

    return figures


def run_behavior_study(
    project_root: str | Path | None = None,
    *,
    n_bootstrap: int = BOOTSTRAP_RESAMPLES,
) -> BehaviorStudyResult:
    """Run validation-only selection and a single locked TEST evaluation."""
    started = time.perf_counter()
    root = (
        Path(project_root).resolve()
        if project_root is not None
        else Path(__file__).resolve().parents[1]
    )
    orders, split_frames, split_metadata = _load_project_data(root)
    dataset_end = pd.Timestamp(orders["PurchaseDate"].max())
    order_count = len(orders)
    event_prepare_started = time.perf_counter()
    events = prepare_purchase_events(orders)
    event_prepare_seconds = time.perf_counter() - event_prepare_started

    purchase_metadata = json.loads(
        (root / "models" / "purchase_clock" / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    validation_metadata = json.loads(
        (
            root
            / "models"
            / "purchase_clock"
            / "validation_vintage"
            / "metadata.json"
        ).read_text(encoding="utf-8")
    )
    purchase_bundle = pc.load_purchase_clock_artifacts(
        root / "models" / "purchase_clock"
    )
    population_median_gap = float(
        purchase_metadata["population_median_gap_days"]
    )
    if (
        pd.Timestamp(purchase_metadata["training_outcome_end"])
        >= pd.Timestamp("2010-09-10")
        or pd.Timestamp(purchase_metadata["selection_outcome_end"])
        >= pd.Timestamp("2010-09-10")
    ):
        raise ValueError("The saved Purchase Clock vintage overlaps the locked TEST period.")

    behavior_cache: dict[tuple[str, float], pd.DataFrame] = {}
    split_cohorts: dict[tuple[int, str], pd.DataFrame] = {}
    for horizon in HORIZONS:
        for role in ("TRAIN", "VAL"):
            cohort = _split_cohort(split_frames, horizon, role)
            target = _target_for_role(orders, cohort, horizon, dataset_end)
            label = f"Purchased_{horizon}d"
            cohort = cohort.merge(target, on="Customer ID", validate="one_to_one")
            cohort["no_purchase"] = 1 - cohort[label].astype(int)
            cohort = _add_delay_ratio(cohort, population_median_gap)
            split_cohorts[(horizon, role)] = cohort
        test_cohort = _split_cohort(split_frames, horizon, "TEST")
        split_cohorts[(horizon, "TEST")] = _add_delay_ratio(
            test_cohort, population_median_gap
        )

    feature_seconds_started = time.perf_counter()
    selected_models: dict[int, SelectedBehaviorModel] = {}
    selected_lambdas: dict[int, float] = {}
    selection_rows: list[dict[str, Any]] = []
    lambda_selection_rows: list[dict[str, Any]] = []
    validation_thresholds: dict[tuple[int, str], float] = {}
    ablation_models: dict[tuple[int, str], SelectedBehaviorModel] = {}

    family_sets = {
        "personalized_gap": BEHAVIOR_FEATURE_FAMILIES["personalized_gap"],
        "frequency_change": BEHAVIOR_FEATURE_FAMILIES["frequency_change"],
        "spending_change": BEHAVIOR_FEATURE_FAMILIES["spending_change"],
        "trajectory_change": BEHAVIOR_FEATURE_FAMILIES["trajectory_change"],
    }
    for horizon in HORIZONS:
        train = _join_behavior(
            split_cohorts[(horizon, "TRAIN")],
            events,
            EWMA_LAMBDA_CANDIDATES[0],
            behavior_cache,
        )
        validation = _join_behavior(
            split_cohorts[(horizon, "VAL")],
            events,
            EWMA_LAMBDA_CANDIDATES[0],
            behavior_cache,
        )
        y_train = train["no_purchase"].to_numpy(dtype=int)
        y_validation = validation["no_purchase"].to_numpy(dtype=int)
        candidates: list[tuple[float, float, float, SelectedBehaviorModel]] = []
        for ewma_lambda in EWMA_LAMBDA_CANDIDATES:
            train_at_lambda = _join_behavior(
                split_cohorts[(horizon, "TRAIN")],
                events,
                ewma_lambda,
                behavior_cache,
            )
            val_at_lambda = _join_behavior(
                split_cohorts[(horizon, "VAL")],
                events,
                ewma_lambda,
                behavior_cache,
            )
            selected = select_behavior_model(
                train_at_lambda.loc[:, list(BEHAVIOR_MODEL_FEATURES)],
                y_train,
                val_at_lambda.loc[:, list(BEHAVIOR_MODEL_FEATURES)],
                y_validation,
                BEHAVIOR_MODEL_FEATURES,
            )
            candidates.append(
                (
                    -float(selected.validation_metrics["average_precision"]),
                    float(
                        selected.validation_probability_metrics["brier_score"]
                    ),
                    float(ewma_lambda),
                    selected,
                )
            )
            lambda_selection_rows.append(
                {
                    "horizon_days": horizon,
                    "ewma_lambda": float(ewma_lambda),
                    "regularization_c": selected.regularization_c,
                    "validation_average_precision": float(
                        selected.validation_metrics["average_precision"]
                    ),
                    "validation_brier_score": float(
                        selected.validation_probability_metrics["brier_score"]
                    ),
                    "validation_customers": int(len(validation)),
                }
            )
        candidates.sort(key=lambda row: (row[0], row[1], row[2]))
        _, _, selected_lambda, selected_model = candidates[0]
        selected_models[horizon] = selected_model
        selected_lambdas[horizon] = selected_lambda

        train = _join_behavior(
            split_cohorts[(horizon, "TRAIN")], events, selected_lambda, behavior_cache
        )
        validation = _join_behavior(
            split_cohorts[(horizon, "VAL")], events, selected_lambda, behavior_cache
        )
        validation_prediction = predict_nonpurchase_probability(
            selected_model,
            validation,
        )
        validation_thresholds[(horizon, "behavior")] = select_alert_threshold(
            validation_prediction
        )
        selection_rows.append(
            {
                "horizon_days": horizon,
                "ewma_lambda": float(selected_lambda),
                "regularization_c": selected_model.regularization_c,
                "validation_average_precision": float(
                    selected_model.validation_metrics["average_precision"]
                ),
                "validation_brier_score": float(
                    selected_model.validation_probability_metrics["brier_score"]
                ),
                "validation_customers": int(len(validation)),
                "active_features": list(selected_model.feature_columns),
            }
        )

        for family, removed in family_sets.items():
            ablation, _ = _ablation_selection(
                train.loc[:, list(BEHAVIOR_MODEL_FEATURES)],
                y_train,
                validation.loc[:, list(BEHAVIOR_MODEL_FEATURES)],
                y_validation,
                family,
            )
            ablation_models[(horizon, family)] = ablation

        training_recency_threshold = float(
            train["Recency"].quantile(0.90, interpolation="linear")
        )
        val_baselines = {
            "global_inactivity": (
                validation["Recency"].ge(training_recency_threshold).astype(float).to_numpy()
            ),
            "recency": validation["Recency"].to_numpy(dtype=float),
            "delay_ratio": validation["delay_ratio"].to_numpy(dtype=float),
        }
        for baseline_name, scores in val_baselines.items():
            validation_thresholds[(horizon, baseline_name)] = select_alert_threshold(
                scores
            )

    selection_seconds = time.perf_counter() - feature_seconds_started
    # No TEST labels have been constructed or read before the selection above.
    test_started = time.perf_counter()
    comparison_rows: list[dict[str, Any]] = []
    bootstrap_rows: list[dict[str, Any]] = []
    subgroup_rows: list[dict[str, Any]] = []
    test_frames: dict[int, pd.DataFrame] = {}
    case_rows: list[dict[str, Any]] = []

    vintage_available_by = pd.Timestamp(
        validation_metadata["validation_vintage"]["available_for_forecasts_by"]
    )
    training_cutoffs = {
        horizon: pd.Timestamp(
            split_metadata["predictive_splits_outcome_matured"][str(horizon)][
                "train_cutoff"
            ]
        )
        for horizon in HORIZONS
    }
    candidate_f_eligible = all(
        training_cutoffs[horizon] >= vintage_available_by
        for horizon in HORIZONS
    )
    candidate_f_status = (
        "eligible"
        if candidate_f_eligible
        else (
            "not_fitted: no saved Purchase Clock vintage was available by any official "
            "TRAIN cutoff; the validation vintage was available only from "
            f"{vintage_available_by.date()} and the test model was available by "
            f"{purchase_metadata['available_for_test_by']}"
        )
    )

    for horizon in HORIZONS:
        train = _join_behavior(
            split_cohorts[(horizon, "TRAIN")],
            events,
            selected_lambdas[horizon],
            behavior_cache,
        )
        validation = _join_behavior(
            split_cohorts[(horizon, "VAL")],
            events,
            selected_lambdas[horizon],
            behavior_cache,
        )
        test_features = _split_cohort(split_frames, horizon, "TEST")
        if not test_features["cutoff_date"].eq(pd.Timestamp("2010-09-10")).all():
            raise ValueError("Locked TEST features have an unexpected cutoff.")
        test_outcomes = _target_for_role(
            orders,
            test_features,
            horizon,
            dataset_end,
        )
        label = f"Purchased_{horizon}d"
        expected = split_metadata["predictive_splits_outcome_matured"][str(horizon)][
            "summary"
        ]
        expected_test = next(row for row in expected if row["Split_Role"] == "TEST")
        test_target = test_features[["Customer ID"]].merge(
            test_outcomes,
            on="Customer ID",
            validate="one_to_one",
        )
        if len(test_target) != expected_test["Eligible_Custs"]:
            raise ValueError(f"{horizon}d TEST cohort size changed.")
        if int(test_target[label].sum()) != expected_test["Future_Buyers"]:
            raise ValueError(f"{horizon}d TEST labels differ from saved metadata.")
        y_test = (1 - test_target[label].to_numpy(dtype=int))

        test = _join_behavior(
            split_cohorts[(horizon, "TEST")],
            events,
            selected_lambdas[horizon],
            behavior_cache,
        )
        test_frames[horizon] = test
        behavior_score = predict_nonpurchase_probability(
            selected_models[horizon],
            test,
        )
        test["candidate_e_nonpurchase_probability"] = behavior_score
        purchase_features = test_features.loc[
            :, ["Customer ID", "cutoff_date", *pc.NUMERIC_FEATURES]
        ].copy()
        purchase_predictions = pc.predict_purchase_clock(
            purchase_bundle,
            purchase_features,
        )
        clock_risk = 1.0 - purchase_predictions[f"personalized_P{horizon}"].to_numpy(
            dtype=float
        )

        train_recency_threshold = float(train["Recency"].quantile(0.90))
        score_map = {
            "Global inactivity indicator": test["Recency"]
            .ge(train_recency_threshold)
            .astype(float)
            .to_numpy(),
            "Recency-only ranking": test["Recency"].to_numpy(dtype=float),
            "Personalized delay ratio": test["delay_ratio"].to_numpy(dtype=float),
            "Personalized Purchase Clock": clock_risk,
            "Behavior features only": behavior_score,
        }
        probabilistic = {
            "Personalized Purchase Clock",
            "Behavior features only",
        }
        for model_name, scores in score_map.items():
            validation_name = {
                "Global inactivity indicator": "global_inactivity",
                "Recency-only ranking": "recency",
                "Personalized delay ratio": "delay_ratio",
                "Behavior features only": "behavior",
            }.get(model_name)
            threshold = (
                validation_thresholds[(horizon, validation_name)]
                if validation_name is not None
                else None
            )
            row, _ = _model_metrics(
                horizon,
                model_name,
                y_test,
                scores,
                threshold,
                probabilistic=model_name in probabilistic,
            )
            comparison_rows.append(row)

        comparison_rows.append(
            {
                "horizon_days": horizon,
                "model": "Purchase Clock + behavior",
                "n_customers": int(len(y_test)),
                "roc_auc": None,
                "average_precision": None,
                "precision_at_budget": None,
                "recall_at_budget": None,
                "brier_score": None,
                "log_loss": None,
                "alert_coverage": None,
                "false_alert_rate": None,
                "threshold": None,
                "frozen_threshold_alert_coverage": None,
                "frozen_threshold_false_alert_rate": None,
                "status": candidate_f_status,
            }
        )

        test_customer_ids = test["Customer ID"].to_numpy()
        for metric in ("average_precision", "brier"):
            difference = paired_customer_bootstrap_difference(
                y_test,
                behavior_score,
                clock_risk,
                test_customer_ids,
                metric=metric,
                n_resamples=n_bootstrap,
                random_state=42 + horizon,
            )
            bootstrap_rows.append(
                {
                    "horizon_days": horizon,
                    "comparison": "Candidate E vs Personalized Purchase Clock",
                    **difference,
                }
            )

        for family in (
            "personalized_gap",
            "frequency_change",
            "spending_change",
            "trajectory_change",
        ):
            ablation = ablation_models[(horizon, family)]
            ablation_score = predict_nonpurchase_probability(ablation, test)
            for metric in ("average_precision",):
                difference = paired_customer_bootstrap_difference(
                    y_test,
                    behavior_score,
                    ablation_score,
                    test_customer_ids,
                    metric=metric,
                    n_resamples=n_bootstrap,
                    random_state=100 + horizon + len(family),
                )
                bootstrap_rows.append(
                    {
                        "horizon_days": horizon,
                        "comparison": f"Candidate E vs E without {family}",
                        **difference,
                    }
                )
            threshold = validation_thresholds[(horizon, "behavior")]
            row, _ = _model_metrics(
                horizon,
                f"Candidate E without {family}",
                y_test,
                ablation_score,
                threshold=None,
                probabilistic=True,
            )
            comparison_rows.append(row)

        subgroup_rows.extend(
            _subgroup_metrics(horizon, "Behavior features only", y_test, behavior_score, test)
        )
        subgroup_rows.extend(
            _subgroup_metrics(
                horizon,
                "Personalized Purchase Clock",
                y_test,
                clock_risk,
                test,
            )
        )
        if horizon == 90:
            candidates = (
                test.loc[test["gap_deviation_score"].notna()]
                .loc[test["history_sufficiency"].eq("sufficient")]
                .sort_values("gap_deviation_score", ascending=False)
                .head(3)
            )
            for _, candidate in candidates.iterrows():
                trajectory = build_behavior_trajectory(
                    events,
                    candidate["Customer ID"],
                    candidate["cutoff_date"],
                )
                case_rows.append(
                    {
                        "customer_id": int(candidate["Customer ID"]),
                        "cutoff_date": pd.Timestamp(candidate["cutoff_date"]).date().isoformat(),
                        "selection_reason": "largest observed gap deviation with sufficient history",
                        "history_sufficiency": str(candidate["history_sufficiency"]),
                        "gap_deviation_score": _json_number(
                            candidate["gap_deviation_score"]
                        ),
                        "trajectory": trajectory,
                    }
                )

    test_seconds = time.perf_counter() - test_started
    comparison = pd.DataFrame(comparison_rows)
    ablations = pd.DataFrame(
        [
            {
                "horizon_days": row["horizon_days"],
                "comparison": row["comparison"],
                "metric": row["metric"],
                "difference_first_minus_second": row[
                    "difference_first_minus_second"
                ],
                "confidence_interval_95_lower": row[
                    "confidence_interval_95_lower"
                ],
                "confidence_interval_95_upper": row[
                    "confidence_interval_95_upper"
                ],
            }
            for row in bootstrap_rows
            if row["comparison"].startswith("Candidate E vs E without")
        ]
    )
    selection = pd.DataFrame(selection_rows)
    subgroups = pd.DataFrame(subgroup_rows)
    case_studies = pd.DataFrame(case_rows)

    validation_lambda_scores = pd.DataFrame(lambda_selection_rows)
    selected_global_lambda = float(
        validation_lambda_scores.groupby("ewma_lambda", as_index=False)
        .agg(
            mean_validation_average_precision=(
                "validation_average_precision",
                "mean",
            ),
            mean_validation_brier_score=("validation_brier_score", "mean"),
        )
        .sort_values(
            ["mean_validation_average_precision", "mean_validation_brier_score", "ewma_lambda"],
            ascending=[False, True, True],
        )
        .iloc[0]["ewma_lambda"]
    )

    hypotheses = _make_hypothesis_results(bootstrap_rows)
    evaluation = {
        "evaluation_version": EVALUATION_VERSION,
        "feature_version": MODEL_VERSION,
        "policy_version": POLICY_VERSION,
        "test_cutoff_date": "2010-09-10",
        "result_status": "completed_locked_TEST_evaluation",
        "candidate_f_status": candidate_f_status,
        "selection_results": [
            {
                "horizon_days": int(row["horizon_days"]),
                "selected_ewma_lambda": float(row["ewma_lambda"]),
                "selected_regularization_c": float(row["regularization_c"]),
                "validation_average_precision": float(
                    row["validation_average_precision"]
                ),
                "validation_brier_score": float(row["validation_brier_score"]),
                "validation_customers": int(row["validation_customers"]),
            }
            for row in selection_rows
        ],
        "model_comparison": comparison.to_dict(orient="records"),
        "bootstrap_comparisons": bootstrap_rows,
        "subgroup_results": subgroups.to_dict(orient="records"),
        "hypotheses": hypotheses,
        "limitations": [
            "Outcome means no observed purchase within the next H days; it is not permanent churn.",
            "The Year 1 UK retail cohort is sparse and the results are historical backtests, not live forecasts or intervention effects.",
            "Candidate F was not fitted because the saved Purchase Clock prediction vintages postdate every official TRAIN cutoff.",
            "Candidate E versus the Purchase Clock compares two separately trained/ranked methods; it does not establish independent incremental value without Candidate F.",
            "The top-10% ranking comparison is an evaluation budget, not a deployed alert policy. No categorical alert states are enabled.",
            "Customer-level bootstrap intervals assume the held-out TEST cutoff contributes one row per customer; repeated customer snapshots are not bootstrapped as independent rows.",
            "Some recent/reference revenue and EWMA features are unavailable for customers with sparse or zero-revenue histories.",
        ],
    }
    global_config = BehaviorConfig(
        **{**asdict(DEFAULT_CONFIG), "ewma_lambda": selected_global_lambda}
    )
    profiling = {
        "order_rows": int(order_count),
        "valid_purchase_events": int(len(events)),
        "customers_in_locked_test": int(
            split_frames[90].loc[
                split_frames[90]["split_role"].eq("TEST"), "Customer ID"
            ].nunique()
        ),
        "distinct_cutoff_lambda_snapshots": int(len(behavior_cache)),
        "event_preparation_seconds": float(event_prepare_seconds),
        "validation_selection_seconds": float(selection_seconds),
        "locked_test_evaluation_seconds": float(test_seconds),
        "total_seconds": float(time.perf_counter() - started),
        "feature_rows_scored_per_second": float(
            sum(len(frame) for frame in test_frames.values())
            / max(test_seconds, 1e-9)
        ),
        "api_feature_snapshot_cached_per_process": True,
    }
    metadata = {
        "feature_version": MODEL_VERSION,
        "policy_version": POLICY_VERSION,
        "evaluation_version": EVALUATION_VERSION,
        "method": "Descriptive continuous indicators; validation-selected L2 logistic regression for behavior-only comparison.",
        "config": asdict(global_config),
        "selected_ewma_lambda_by_horizon": {
            str(key): float(value) for key, value in selected_lambdas.items()
        },
        "serving_ewma_lambda_selected_on_validation": selected_global_lambda,
        "regularization_candidates": [0.1, 1.0, 10.0],
        "official_split_cutoffs": {
            str(horizon): {
                role.lower(): pd.Timestamp(
                    split_metadata["predictive_splits_outcome_matured"][str(horizon)][
                        f"{role.lower()}_cutoff"
                    ]
                ).date().isoformat()
                for role in SPLIT_ROLES
            }
            for horizon in HORIZONS
        },
        "test_cutoff": "2010-09-10",
        "test_outcomes_used_for_selection_or_training": False,
        "candidate_f_status": candidate_f_status,
        "alert_policy_available": False,
        "policy_status": "continuous_indicators_only",
        "alert_threshold": None,
        "purchase_clock_vintage_audit": {
            "validation_vintage_available_by": vintage_available_by.date().isoformat(),
            "validation_vintage_first_usable_cutoff": validation_metadata[
                "validation_vintage"
            ]["first_usable_forecast_cutoff"],
            "main_model_available_for_test_by": purchase_metadata[
                "available_for_test_by"
            ],
            "official_train_cutoffs": {
                str(key): value.date().isoformat()
                for key, value in training_cutoffs.items()
            },
            "eligible_for_candidate_f_training": candidate_f_eligible,
        },
        "profiling": profiling,
        "artifact_policy": "No joblib model or categorical alert artifact is saved unless validation supports it.",
    }
    evaluation["profiling"] = profiling

    metrics_path = root / "data" / "metrics" / "behavior_monitor_evaluation.json"
    model_dir = root / "models" / "behavior_monitor"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    (root / "data" / "metrics" / "behavior_monitor_profiling.json").write_text(
        json.dumps(_json_native(profiling), indent=2) + "\n",
        encoding="utf-8",
    )
    metrics_path.write_text(
        json.dumps(_json_native(evaluation), indent=2) + "\n",
        encoding="utf-8",
    )
    (model_dir / "metadata.json").write_text(
        json.dumps(_json_native(metadata), indent=2) + "\n",
        encoding="utf-8",
    )
    figures = _figures(test_frames, comparison, case_studies)
    return BehaviorStudyResult(
        evaluation=evaluation,
        metadata=metadata,
        selection=selection,
        lambda_selection=validation_lambda_scores.sort_values(
            ["horizon_days", "ewma_lambda"]
        ).reset_index(drop=True),
        comparison=comparison,
        ablations=ablations,
        subgroups=subgroups,
        case_studies=case_studies,
        figures=figures,
    )
