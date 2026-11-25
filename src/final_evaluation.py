"""Build a deterministic, evidence-linked summary of the 11 OELP notebooks."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from app.config import METRICS_DIR, PROCESSED_DIR, PROJECT_ROOT

ARTIFACT_VERSION = "oelp-final-research-evaluation-v1"
OUTPUT_PATH = METRICS_DIR / "final_project_evaluation.json"

NOTEBOOK_SOURCE_PATHS = (
    "notebooks/01_EDA_analysis.ipynb",
    "notebooks/02_Customer_feature_engineering.ipynb",
    "notebooks/03_Interpurchase_Distribution_Analysis.ipynb",
    "notebooks/04_KMeans_Customer_Segmentation.ipynb",
    "notebooks/05_Statistical_Validation_and_Temporal_Framework.ipynb",
    "notebooks/06_Personalized_Purchase_Clock.ipynb",
    "notebooks/07_Future_Spending_and_Revenue_Forecasting.ipynb",
    "notebooks/08_Behavioral_Change_Detection.ipynb",
    "notebooks/09_Prediction_Reliability_and_Explainability.ipynb",
    "notebooks/10_Revenue_at_Risk_and_Retention_Planning.ipynb",
    "notebooks/11_Customer_Retention_Trajectory_Analysis.ipynb",
)

SOURCE_PATHS = (
    *NOTEBOOK_SOURCE_PATHS,
    "data/metrics/notebook_evaluation_summary.json",
    "data/metrics/behavior_monitor_evaluation.json",
    "data/metrics/prediction_reliability_evaluation.json",
    "data/metrics/revenue_exposure_evaluation.json",
    "data/metrics/trajectory_analysis_evaluation.json",
    "data/metrics/retention_scenario_sensitivity.json",
    "data/processed/segmentation_metadata.json",
    "data/processed/temporal/temporal_split_metadata.json",
    "data/processed/temporal/validation_results.json",
    "data/processed/customer_features.csv",
    "data/processed/interpurchase_distribution_results.csv",
    "data/processed/inactivity_threshold.json",
    "data/processed/clustering_metrics.csv",
    "models/purchase_clock/metadata.json",
    "models/spending_model/metadata.json",
    "models/behavior_monitor/metadata.json",
    "models/prediction_reliability/metadata.json",
    "models/revenue_exposure/metadata.json",
    "models/trajectory_analysis/metadata.json",
)

MODULES: tuple[dict[str, Any], ...] = (
    {
        "notebook_id": "01",
        "title": "Exploratory data analysis",
        "objective": "Inspect source quality, missingness, transaction patterns, and cleaning decisions before customer-level analysis.",
        "method": "Descriptive data checks; no predictive model or churn label.",
        "source_artifacts": ["notebooks/01_EDA_analysis.ipynb", "data/processed/online_retail_cleaned_data.csv"],
        "source_fields": ["notebook markdown and cleaning pipeline"],
        "horizons_days": [],
        "population": "Year 1 transaction records; customer-level eligibility is defined by later notebooks.",
        "limitations": ["Missing customer identifiers and the short, left-truncated observation window limit customer-level interpretation."],
    },
    {
        "notebook_id": "02",
        "title": "Customer feature engineering",
        "objective": "Create reproducible customer-level RFM and activity features with explicit handling of sparse and missing histories.",
        "method": "Invoice aggregation, customer feature construction, and documented transforms.",
        "source_artifacts": ["notebooks/02_Customer_feature_engineering.ipynb", "data/processed/customer_features.csv"],
        "source_fields": ["feature definitions and saved customer feature table"],
        "horizons_days": [],
        "population": "Customers with valid customer-linked purchases.",
        "limitations": ["Single-purchase histories do not support an inter-purchase gap estimate."],
    },
    {
        "notebook_id": "03",
        "title": "Inter-purchase distributions",
        "objective": "Describe customer purchase gaps and fit candidate gap distributions without treating a fitted distribution as a churn threshold.",
        "method": "Invoice-level inter-purchase intervals and maximum-likelihood distribution fits.",
        "source_artifacts": ["notebooks/03_Interpurchase_Distribution_Analysis.ipynb", "data/processed/interpurchase_distribution_results.csv", "data/processed/inactivity_threshold.json"],
        "source_fields": ["distribution fit summaries and empirical threshold provenance"],
        "horizons_days": [],
        "population": "Customers with at least two valid purchase orders for gap fitting.",
        "limitations": ["Distribution fit diagnostics are descriptive; gaps crossing the observation boundary are censored."],
    },
    {
        "notebook_id": "04",
        "title": "K-means customer segments",
        "objective": "Create stable, descriptive RFM customer segments using the full historical Year 1 snapshot.",
        "method": "Log1p-transformed RFM, standardized K-means, and seed-stability checks.",
        "source_artifacts": ["notebooks/04_KMeans_Customer_Segmentation.ipynb", "data/processed/segmentation_metadata.json", "data/processed/clustering_metrics.csv"],
        "source_fields": ["final_metrics", "stability_check", "cluster_sizes"],
        "horizons_days": [],
        "population": "Full-period descriptive cohort; not used as a prospective predictor.",
        "limitations": ["Full-period segment labels are descriptive and must not be interpreted as a prospective churn score."],
    },
    {
        "notebook_id": "05",
        "title": "Statistical validation and time splits",
        "objective": "Validate historical segment differences and define outcome-matured TRAIN, VAL, and TEST cutoffs for prediction.",
        "method": "Retrospective nonparametric and survival comparisons plus horizon-specific temporal splits.",
        "source_artifacts": ["notebooks/05_Statistical_Validation_and_Temporal_Framework.ipynb", "data/processed/temporal/temporal_split_metadata.json", "data/processed/temporal/validation_results.json"],
        "source_fields": ["predictive_splits_outcome_matured", "binary_90d_purchase", "order_count_90d", "revenue_90d", "survival_logrank"],
        "horizons_days": [],
        "population": "Horizon-specific historical cohorts at outcome-matured cutoffs.",
        "limitations": ["Retrospective validation establishes association, not causation; combined descriptive cutoffs are not training data."],
    },
    {
        "notebook_id": "06",
        "title": "Personalized Purchase Clock",
        "objective": "Compare global, historical-segment, and personalized purchase probabilities at historical cutoffs.",
        "method": "Saved discrete-time logistic hazard model and baseline comparisons.",
        "source_artifacts": ["notebooks/06_Personalized_Purchase_Clock.ipynb", "data/metrics/notebook_evaluation_summary.json", "models/purchase_clock/metadata.json"],
        "source_fields": ["purchase_clock.test_metrics", "purchase_clock_model_version", "forecast_horizons_days"],
        "horizons_days": [],
        "population": "Locked historical TEST cohort at the official cutoff.",
        "limitations": ["Forecasts reproduce a historical saved model; future nonpurchase is horizon-specific and is not permanent churn."],
    },
    {
        "notebook_id": "07",
        "title": "Future spending forecasts",
        "objective": "Evaluate historical-rate, segment-aware, and personalized expected gross-revenue forecasts over the supported horizons.",
        "method": "Two-stage purchase probability times conditional spending, with a direct historical-rate baseline.",
        "source_artifacts": ["notebooks/07_Future_Spending_and_Revenue_Forecasting.ipynb", "data/metrics/notebook_evaluation_summary.json", "models/spending_model/metadata.json"],
        "source_fields": ["spending_forecast.test_metrics", "model_version", "forecast_horizons_days"],
        "horizons_days": [],
        "population": "Locked historical TEST cohort at the official cutoff.",
        "limitations": ["Spending forecasts are historical estimates; no one model minimizes every error or calibration measure at every horizon."],
    },
    {
        "notebook_id": "08",
        "title": "Behavioral change detection",
        "objective": "Test whether continuous, cutoff-safe behavior-change indicators improve short-horizon ranking beyond simple historical signals.",
        "method": "Validation-selected behavior-only ablations with customer-clustered bootstrap comparisons.",
        "source_artifacts": ["notebooks/08_Behavioral_Change_Detection.ipynb", "data/metrics/behavior_monitor_evaluation.json", "models/behavior_monitor/metadata.json"],
        "source_fields": ["hypotheses", "model_comparison", "result_status", "candidate_f_status"],
        "horizons_days": [],
        "population": "Locked historical TEST customers; model comparisons are limited to supported history.",
        "limitations": ["H5 is unresolved because a chronologically eligible saved Purchase Clock vintage was unavailable at the official TRAIN cutoffs; no operational alert policy is supported."],
    },
    {
        "notebook_id": "09",
        "title": "Prediction reliability and explainability",
        "objective": "Explain frozen historical model outputs and evaluate calibration, subgroup reliability, and uncertainty without changing predictions.",
        "method": "Saved-model diagnostics, validation-defined bins, subgroup metrics, and customer-level bootstrap intervals.",
        "source_artifacts": ["notebooks/09_Prediction_Reliability_and_Explainability.ipynb", "data/metrics/prediction_reliability_evaluation.json", "models/prediction_reliability/metadata.json"],
        "source_fields": ["evaluation", "uncertainty_definitions", "limitations"],
        "horizons_days": [],
        "population": "Locked historical TEST cohort at the official cutoff.",
        "limitations": ["Intervals describe empirical group-metric uncertainty, not parameter uncertainty or an individual's future outcome."],
    },
    {
        "notebook_id": "10",
        "title": "Revenue exposure and retention planning",
        "objective": "Separate expected revenue, model disagreement, nonreturn screening proxies, and hypothetical campaign scenarios.",
        "method": "Saved forecast evaluation, validation-selected ranking rules, and explicit scenario sensitivity analysis.",
        "source_artifacts": ["notebooks/10_Revenue_at_Risk_and_Retention_Planning.ipynb", "data/metrics/revenue_exposure_evaluation.json", "data/metrics/retention_scenario_sensitivity.json", "models/revenue_exposure/metadata.json"],
        "source_fields": ["financial_definitions", "hypotheses", "ranking_selection_and_test_evaluation", "metadata.reference_exposure"],
        "horizons_days": [],
        "population": "Locked historical TEST cohort; policy selection uses validation only.",
        "limitations": ["Reference-based exposure is not estimable; nonreturn proxies are not losses, and campaign response/uplift assumptions are hypothetical and noncausal."],
    },
    {
        "notebook_id": "11",
        "title": "Customer retention trajectories",
        "objective": "Test whether exposure-aware longitudinal purchase paths add stable descriptive structure or predictive information beyond static features and the saved Purchase Clock.",
        "method": "Rolling exposure-adjusted trajectories, TRAIN/VAL-selected curve clustering and functional representation, and locked TEST comparisons.",
        "source_artifacts": ["notebooks/11_Customer_Retention_Trajectory_Analysis.ipynb", "data/metrics/trajectory_analysis_evaluation.json", "models/trajectory_analysis/metadata.json"],
        "source_fields": ["data_scope", "predictive_evaluation", "paired_brier_differences", "cluster_selection", "functional_evaluation"],
        "horizons_days": [],
        "population": "Common historical TEST cohort with separate shape-cluster and functional eligibility requirements.",
        "limitations": ["History is short and left-truncated; clusters are descriptive, and trajectory-only comparisons do not establish conditional incremental value."],
    },
)

STATUS_MAP = {
    "supported_in_multiple_horizons": "supported",
    "inconclusive": "inconclusive",
    "not_assessed_candidate_F_vintage_ineligible": "not_evaluable",
    "supported_descriptively": "descriptive_only",
    "rankings_are_distinct": "descriptive_only",
    "forecast_bias_observed": "descriptive_only",
    "selection_changes_with_budget_or_cost": "descriptive_only",
    "descriptive_assumption_independent_screening_orders": "descriptive_only",
    "not_supported_on_locked_test": "not_supported",
}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required research evidence is missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in research evidence {path}.")
    return value


def _source_manifest(root: Path) -> list[dict[str, str]]:
    manifest = []
    for relative in SOURCE_PATHS:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"Required research evidence is missing: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest.append({"path": relative, "sha256": digest})
    return manifest


def current_source_manifest(root: Path = PROJECT_ROOT) -> list[dict[str, str]]:
    """Return hashes for the checked-in evidence used by the final summary."""
    return _source_manifest(Path(root))


def _hypotheses(behavior: dict[str, Any], revenue: dict[str, Any]) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    behavior_customer_count = behavior.get("profiling", {}).get(
        "customers_in_locked_test"
    )
    behavior_limitations = behavior.get("limitations", [])
    for item in behavior.get("hypotheses", []):
        raw_status = item.get("status")
        evidence = item.get("evidence_summary", "")
        uncertainty = [
            {
                "horizon_days": int(match.group("horizon")),
                "metric": "average_precision_difference",
                "estimate": float(match.group("estimate")),
                "lower": float(match.group("lower")),
                "upper": float(match.group("upper")),
                "level": 0.95,
            }
            for match in re.finditer(
                r"P(?P<horizon>\d+)\s+AP\s+(?:delta|difference)\s+"
                r"(?P<estimate>[-+0-9.eE]+)\s+\(95% CI "
                r"(?P<lower>[-+0-9.eE]+)\s+to\s+(?P<upper>[-+0-9.eE]+)\)",
                evidence,
            )
        ]
        hypotheses.append(
            {
                "id": f"08-{item['hypothesis']}",
                "notebook_id": "08",
                "kind": "hypothesis",
                "statement": item["statement"],
                "raw_status": raw_status,
                "evidence_status": STATUS_MAP.get(raw_status, "not_evaluable"),
                "evidence_summary": evidence,
                "reference_baseline": (
                    "Saved Purchase Clock"
                    if item["hypothesis"] == "H5"
                    else None
                ),
                "selection_protocol": "Behavior-only candidate selection used validation data; the locked TEST cohort was reserved for final evaluation.",
                "test_protocol": "Locked historical TEST comparison using average-precision differences and customer-clustered bootstrap intervals where available.",
                "evaluation_horizons_days": [30, 60, 90],
                "cohort_size": behavior_customer_count,
                "primary_metric": "average_precision_difference",
                "observed_result": evidence,
                "uncertainty_intervals": uncertainty,
                "limitations": behavior_limitations,
                "source_artifact": "data/metrics/behavior_monitor_evaluation.json",
                "source_field": f"hypotheses.{item['hypothesis']}",
            }
        )
    for key, item in revenue.get("hypotheses", {}).items():
        raw_status = item.get("status")
        evidence = item.get("evidence", "")
        hypotheses.append(
            {
                "id": f"10-{key}",
                "notebook_id": "10",
                "kind": "hypothesis",
                "statement": item.get("evidence", ""),
                "raw_status": raw_status,
                "evidence_status": STATUS_MAP.get(raw_status, "not_evaluable"),
                "evidence_summary": evidence,
                "reference_baseline": None,
                "selection_protocol": "Ranking selection, where applicable, uses validation; the locked TEST set is not used to retune the policy.",
                "test_protocol": "Notebook-specific descriptive, forecast-diagnostic, and scenario-sensitivity procedures; see the linked source field.",
                "evaluation_horizons_days": revenue.get("metadata", {}).get(
                    "supported_horizons", []
                ),
                "cohort_size": revenue.get("metadata", {}).get(
                    "evaluation_customer_count"
                ),
                "primary_metric": "Hypothesis-specific saved metric; see evidence summary.",
                "observed_result": evidence,
                "uncertainty_intervals": [],
                "limitations": revenue.get("limitations", []),
                "source_artifact": "data/metrics/revenue_exposure_evaluation.json",
                "source_field": f"hypotheses.{key}",
            }
        )
    return hypotheses


def _compact_reliability(reliability: dict[str, Any]) -> dict[str, Any]:
    evaluation = reliability.get("evaluation", {})
    metadata = reliability.get("metadata", {})
    purchase_calibration = evaluation.get("purchase_calibration", [])
    revenue_metrics = evaluation.get("revenue", [])
    calibration_fields = (
        "horizon_days",
        "n_customers",
        "brier_score",
        "log_loss",
        "average_precision",
        "expected_calibration_error",
        "mean_predicted_probability",
        "observed_purchase_rate",
    )
    return {
        "artifact_version": metadata.get("artifact_version"),
        "forecast_cutoff": metadata.get("forecast_cutoff"),
        "supported_horizons": metadata.get("supported_horizons", []),
        "evaluation_customer_count": evaluation.get(
            "evaluation_customer_count",
            metadata.get("evaluation_customer_count"),
        ),
        "purchase_calibration": [
            {key: row[key] for key in calibration_fields if key in row}
            for row in purchase_calibration
        ],
        "revenue_diagnostics": [
            {
                key: row[key]
                for key in (
                    "horizon_days",
                    "model",
                    "n_customers",
                    "mae",
                    "rmse",
                    "mean_forecast_bias",
                    "mean_forecast_bias_interval",
                    "portfolio_revenue_bias_ratio",
                    "split_role",
                )
                if key in row
            }
            for row in revenue_metrics
        ],
        "uncertainty_definitions": reliability.get("uncertainty_definitions", {}),
        "limitations": reliability.get("limitations", metadata.get("known_limitations", [])),
    }


def _population_counts(
    notebook_id: str,
    *,
    segmentation: dict[str, Any],
    temporal: dict[str, Any],
    notebook_summary: dict[str, Any],
    behavior: dict[str, Any],
    reliability: dict[str, Any],
    revenue: dict[str, Any],
    trajectory: dict[str, Any],
    trajectory_metadata: dict[str, Any],
    purchase_horizons: list[int],
    spending_horizons: list[int],
) -> dict[str, Any]:
    if notebook_id == "04":
        return {
            "input_customers": segmentation.get("n_customers_input"),
            "excluded_test_accounts": segmentation.get("n_test_accounts_excluded"),
            "clustered_customers": segmentation.get("n_customers_clustered"),
        }
    if notebook_id == "05":
        return {
            horizon: {
                role["Split_Role"].lower(): role["Eligible_Custs"]
                for role in split["summary"]
            }
            for horizon, split in temporal.get(
                "predictive_splits_outcome_matured", {}
            ).items()
        }
    if notebook_id == "06":
        return {
            str(horizon): max(
                (
                    row["n_customers"]
                    for row in notebook_summary["purchase_clock"]["test_metrics"]
                    if row["horizon_days"] == int(horizon)
                ),
                default=0,
            )
            for horizon in purchase_horizons
        }
    if notebook_id == "07":
        return {
            str(horizon): max(
                (
                    row["n_customers"]
                    for row in notebook_summary["spending_forecast"]["test_metrics"]
                    if row["horizon_days"] == int(horizon)
                ),
                default=0,
            )
            for horizon in spending_horizons
        }
    if notebook_id == "08":
        return {
            "locked_test_customers": behavior.get("profiling", {}).get(
                "customers_in_locked_test"
            )
        }
    if notebook_id == "09":
        return {
            "locked_test_customers": reliability.get("evaluation", {}).get(
                "evaluation_customer_count"
            )
        }
    if notebook_id == "10":
        return {
            "locked_test_customers": revenue.get("metadata", {}).get(
                "evaluation_customer_count"
            )
        }
    if notebook_id == "11":
        scope = trajectory.get("data_scope", {})
        return {
            "locked_test_customers": scope.get("official_test_customers"),
            "shape_cluster_eligible_by_role": trajectory_metadata.get(
                "shape_cluster_eligible_counts", {}
            ),
            "summary_trajectory_eligible_by_horizon_and_role": trajectory_metadata.get(
                "eligible_customer_counts", {}
            ),
        }
    return {}


def _module_registry(
    segmentation: dict[str, Any],
    temporal: dict[str, Any],
    purchase_metadata: dict[str, Any],
    spending_metadata: dict[str, Any],
    behavior: dict[str, Any],
    behavior_metadata: dict[str, Any],
    reliability: dict[str, Any],
    revenue_metadata: dict[str, Any],
    trajectory_metadata: dict[str, Any],
    notebook_summary: dict[str, Any],
    revenue: dict[str, Any],
    trajectory: dict[str, Any],
    root: Path,
    inactivity_threshold: dict[str, Any],
) -> list[dict[str, Any]]:
    purchase_horizons = purchase_metadata.get("forecast_horizons_days", [])
    spending_horizons = spending_metadata.get("forecast_horizons_days", [])
    module_entries = []
    for definition in MODULES:
        item = dict(definition)
        notebook_id = item["notebook_id"]
        item["dataset"] = "UCI Online Retail II, Year 1"
        item["evaluation_population"] = item["population"]
        item["source_artifact"] = item["source_artifacts"][0]
        item["source_field"] = item["source_fields"][0]
        item["reproducibility_command"] = _reproducibility_command(notebook_id)
        item["reproducibility_reference"] = "docs/FINAL_REPRODUCIBILITY_GUIDE.md"
        item["source_version"] = {
            "04": f"segmentation metadata, K={segmentation.get('selected_K')}",
            "05": f"temporal split metadata, {temporal.get('dataset_span_days')} days",
            "06": purchase_metadata.get("model_version"),
            "07": spending_metadata.get("model_version"),
            "08": behavior.get("evaluation_version"),
            "09": reliability.get("metadata", {}).get("artifact_version"),
            "10": revenue_metadata.get("artifact_version"),
            "11": trajectory_metadata.get("model_version"),
        }.get(item["notebook_id"], "not versioned in a separate evaluation artifact")
        item["evaluation_horizons_days"] = {
            "05": sorted(int(value) for value in temporal.get("predictive_splits_outcome_matured", {})),
            "06": purchase_horizons,
            "07": spending_horizons,
            "08": sorted(
                {int(row["horizon_days"]) for row in behavior.get("model_comparison", [])}
            ),
            "09": reliability.get("metadata", {}).get("supported_horizons", []),
            "10": revenue_metadata.get("supported_horizons", []),
            "11": sorted(int(value) for value in trajectory_metadata.get("official_cutoffs", {})),
        }.get(item["notebook_id"], [])
        item["horizons_days"] = item["evaluation_horizons_days"]
        item["evaluation_population_counts"] = _population_counts(
            item["notebook_id"],
            segmentation=segmentation,
            temporal=temporal,
            notebook_summary=notebook_summary,
            behavior=behavior,
            reliability=reliability,
            revenue=revenue,
            trajectory=trajectory,
            trajectory_metadata=trajectory_metadata,
            purchase_horizons=purchase_horizons,
            spending_horizons=spending_horizons,
        )
        if notebook_id in {"01", "02", "03", "04"}:
            item["historical_cutoff"] = {
                "analysis_period": "full observed Year 1 snapshot",
                "dataset_start": temporal.get("dataset_start"),
                "dataset_end": temporal.get("dataset_end"),
            }
        elif notebook_id == "05":
            item["historical_cutoff"] = {
                "cutoffs_by_horizon": {
                    horizon: {
                        key: split.get(key)
                        for key in ("train_cutoff", "val_cutoff", "test_cutoff")
                    }
                    for horizon, split in temporal.get(
                        "predictive_splits_outcome_matured", {}
                    ).items()
                }
            }
        else:
            item["historical_cutoff"] = {
                "dataset_start": temporal.get("dataset_start"),
                "dataset_end": temporal.get("dataset_end"),
                "official_test_cutoff": temporal.get("predictive_splits_outcome_matured", {})
                .get("30", {})
                .get("test_cutoff"),
            }
        item["major_findings"] = _major_findings(
            notebook_id,
            root=root,
            segmentation=segmentation,
            temporal=temporal,
            notebook_summary=notebook_summary,
            behavior=behavior,
            reliability=reliability,
            revenue=revenue,
            trajectory=trajectory,
            trajectory_metadata=trajectory_metadata,
            inactivity_threshold=inactivity_threshold,
            purchase_horizons=purchase_horizons,
            spending_horizons=spending_horizons,
        )
        module_entries.append(item)
    return module_entries


def _reproducibility_command(notebook_id: str) -> str:
    notebook_path = next(
        path for path in NOTEBOOK_SOURCE_PATHS if path.startswith(f"notebooks/{notebook_id}_")
    )
    execute = (
        "uv run --no-project --python 3.11 --with-requirements requirements-ci.txt "
        "--with jupyter --with ipykernel python -m jupyter execute --inplace "
        f"{notebook_path}"
    )
    if notebook_id == "10":
        build = (
            "uv run --no-project --python 3.11 --with-requirements requirements-ci.txt "
            "python scripts/build_notebook10.py"
        )
        return f"{build} && {execute}"
    return execute


def _major_findings(
    notebook_id: str,
    *,
    root: Path,
    segmentation: dict[str, Any],
    temporal: dict[str, Any],
    notebook_summary: dict[str, Any],
    behavior: dict[str, Any],
    reliability: dict[str, Any],
    revenue: dict[str, Any],
    trajectory: dict[str, Any],
    trajectory_metadata: dict[str, Any],
    inactivity_threshold: dict[str, Any],
    purchase_horizons: list[int],
    spending_horizons: list[int],
) -> list[str]:
    if notebook_id == "01":
        return [
            "Customer IDs are not imputed; records without a reliable customer link are excluded from customer-level behavior analysis.",
            "The source window is short and left-truncated, so a customer's first observed order is not necessarily acquisition.",
        ]
    if notebook_id == "02":
        return [
            "Meaningful missing recency and interpurchase values are retained rather than filled with artificial behavior.",
            "A single observed purchase does not provide an interpurchase gap; later analyses apply method-specific history support.",
        ]
    if notebook_id == "03":
        with (root / "data/processed/interpurchase_distribution_results.csv").open(
            newline="", encoding="utf-8-sig"
        ) as source:
            distributions = list(csv.DictReader(source))
        best = min(distributions, key=lambda row: float(row["aic"]))
        threshold = inactivity_threshold["selected_threshold_days"]
        return [
            f"{best['distribution']} has the lowest saved AIC ({float(best['aic']):,.0f}) among the compared gap distributions.",
            f"The empirical P90 gap is {threshold:.1f} days and is retained only as a descriptive threshold, not as a churn label.",
        ]
    if notebook_id == "04":
        stability = segmentation.get("stability_check", {})
        return [
            f"Descriptive RFM K-means selected K={segmentation.get('selected_K')} for {segmentation.get('n_customers_clustered'):,} customers.",
            f"Seed stability is high (mean ARI {stability.get('mean_ARI_vs_seed42')}, minimum ARI {stability.get('min_ARI_vs_seed42')}); the segments are not prospective churn scores.",
        ]
    if notebook_id == "05":
        split_data = temporal.get("predictive_splits_outcome_matured", {})
        test_counts = {
            str(horizon): next(
                row["Eligible_Custs"]
                for row in split_data[str(horizon)]["summary"]
                if row["Split_Role"] == "TEST"
            )
            for horizon in sorted(int(value) for value in split_data)
        }
        cutoff = split_data.get("30", {}).get("test_cutoff")
        return [
            f"Outcome-matured TRAIN/VAL/TEST cutoffs were saved separately for 30-, 60-, and 90-day targets; locked TEST populations by horizon are {test_counts}.",
            f"The common TEST cutoff is {cutoff}; horizon-specific targets end at different dates and must not be mixed.",
        ]
    if notebook_id == "06":
        metrics = notebook_summary["purchase_clock"]["test_metrics"]
        horizons = sorted({int(row["horizon_days"]) for row in metrics})
        top_roc = sum(
            max((row for row in metrics if row["horizon_days"] == horizon), key=lambda row: row["roc_auc"])["model"]
            == "Personalized"
            for horizon in horizons
        )
        top_ap = sum(
            max((row for row in metrics if row["horizon_days"] == horizon), key=lambda row: row["average_precision"])["model"]
            == "Personalized"
            for horizon in horizons
        )
        best_brier = sum(
            min((row for row in metrics if row["horizon_days"] == horizon), key=lambda row: row["brier_score"])["model"]
            == "Personalized"
            for horizon in horizons
        )
        return [
            f"Personalized Purchase Clock ranks highest on ROC-AUC and average precision, and lowest on Brier score, at {top_roc}/{len(horizons)}, {top_ap}/{len(horizons)}, and {best_brier}/{len(horizons)} saved TEST horizons respectively.",
            "Calibration error remains horizon-specific; these are locked historical comparisons, not current-business forecasts.",
        ]
    if notebook_id == "07":
        metrics = notebook_summary["spending_forecast"]["test_metrics"]
        horizons = sorted({int(row["horizon_days"]) for row in metrics})
        return [
            "Personalized two-stage forecasts have the lowest saved MAE at all evaluated horizons, while forecast bias and aggregate calibration differ by model and horizon.",
            "Expected revenue is purchase probability multiplied by conditional expected spending; model disagreement is not a financial loss estimate.",
        ]
    if notebook_id == "08":
        statuses = {item["hypothesis"]: item["status"] for item in behavior.get("hypotheses", [])}
        supported = [key for key, value in statuses.items() if value == "supported_in_multiple_horizons"]
        inconclusive = [key for key, value in statuses.items() if value == "inconclusive"]
        not_evaluable = [key for key, value in statuses.items() if value == "not_assessed_candidate_F_vintage_ineligible"]
        return [
            f"Saved hypothesis outcomes: supported in multiple horizons {', '.join(supported) or 'none'}; inconclusive {', '.join(inconclusive) or 'none'}; not evaluable {', '.join(not_evaluable) or 'none'}.",
            "The conditional Purchase Clock-plus-behavior model was not fitted because a chronologically eligible saved model vintage was unavailable; no operational alert policy is supported.",
        ]
    if notebook_id == "09":
        calibration = reliability.get("evaluation", {}).get("purchase_calibration", [])
        row = next((item for item in calibration if item.get("horizon_days") == 30), {})
        return [
            f"Reliability diagnostics cover {reliability.get('evaluation', {}).get('evaluation_customer_count', 0):,} historical TEST customers; the 30-day Personalized Clock Brier score is {row.get('brier_score')} with fixed-bin ECE {row.get('expected_calibration_error')}.",
            "Calibration and bootstrap intervals are group-level historical diagnostics, not individual accuracy guarantees; feature substitutions are noncausal sensitivities.",
        ]
    if notebook_id == "10":
        financial = revenue.get("financial_definitions", {})
        hypothesis = revenue.get("hypotheses", {}).get("H6_predictive_ranking", {})
        return [
            f"Reference-based revenue exposure is {financial.get('reference_exposure_status')}; the saved total remains {financial.get('reference_exposure_total_gbp')}.",
            f"Validation-selected ranking outcome on locked TEST: {hypothesis.get('status')}. The 90-day selection is exploratory, and campaign assumptions remain hypothetical rather than causal.",
        ]
    if notebook_id == "11":
        shape_count = trajectory_metadata.get("shape_cluster_eligible_counts", {}).get("TEST")
        functional = trajectory.get("functional_analysis", {}).get("test_evaluation", {})
        selected_clusters = trajectory.get("cluster_selection", {}).get("selected_cluster_count")
        explained = functional.get("train_cumulative_explained_variance")
        rmse = functional.get("test_reconstruction_rmse")
        summary_count = trajectory_metadata.get("eligible_customer_counts", {}).get("30d_test_summary")
        return [
            f"The selected descriptive shape solution has {selected_clusters} clusters; {shape_count:,} TEST customers meet its support rule, versus {summary_count:,} eligible for the broader 30-day summary trajectory.",
            f"TRAIN-fitted functional PCA evaluated {functional.get('evaluated_curves'):,} TEST curves, with {explained:.2%} TRAIN cumulative explained variance and TEST reconstruction RMSE {rmse:.6f}.",
            "Trajectory-only prediction comparisons do not establish conditional incremental value beyond the saved Purchase Clock.",
        ]
    return []


def build_final_evaluation(root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Build the stable summary from checked-in evaluation artifacts only."""
    root = Path(root)
    metrics = root / "data" / "metrics"
    processed = root / "data" / "processed"
    models = root / "models"

    notebook_summary = _read_json(metrics / "notebook_evaluation_summary.json")
    behavior = _read_json(metrics / "behavior_monitor_evaluation.json")
    reliability = _read_json(metrics / "prediction_reliability_evaluation.json")
    revenue = _read_json(metrics / "revenue_exposure_evaluation.json")
    trajectory = _read_json(metrics / "trajectory_analysis_evaluation.json")
    scenario_sensitivity = _read_json(metrics / "retention_scenario_sensitivity.json")
    segmentation = _read_json(processed / "segmentation_metadata.json")
    temporal = _read_json(processed / "temporal" / "temporal_split_metadata.json")
    validation = _read_json(processed / "temporal" / "validation_results.json")
    purchase_metadata = _read_json(models / "purchase_clock" / "metadata.json")
    spending_metadata = _read_json(models / "spending_model" / "metadata.json")
    behavior_metadata = _read_json(models / "behavior_monitor" / "metadata.json")
    reliability_metadata = _read_json(models / "prediction_reliability" / "metadata.json")
    revenue_metadata = _read_json(models / "revenue_exposure" / "metadata.json")
    trajectory_metadata = _read_json(models / "trajectory_analysis" / "metadata.json")
    inactivity_threshold = _read_json(processed / "inactivity_threshold.json")

    purchase_metrics = notebook_summary["purchase_clock"]["test_metrics"]
    spending_metrics = notebook_summary["spending_forecast"]["test_metrics"]
    hypotheses = _hypotheses(behavior, revenue)
    counts = Counter(row["evidence_status"] for row in hypotheses)
    paired = trajectory.get("predictive_evaluation", {}).get(
        "paired_brier_differences", {}
    )
    trajectory_questions = {
        "incremental_predictive_value": {
            "statement": "Do trajectory-derived predictors add reliable incremental value beyond the saved Purchase Clock?",
            "evidence_status": "inconclusive",
            "paired_brier_difference": paired.get(
                "saved Purchase Clock (same TEST subset)", {}
            ),
            "interpretation": "Overlapping paired confidence intervals are inconclusive; they do not establish equivalence or conditional incremental value.",
            "source_artifact": "data/metrics/trajectory_analysis_evaluation.json",
            "source_field": "predictive_evaluation.paired_brier_differences.saved Purchase Clock (same TEST subset)",
        },
    }

    source_refs = _source_manifest(root)
    final = {
        "artifact_version": ARTIFACT_VERSION,
        "research_scope": {
            "dataset": "UCI Online Retail II, Year 1",
            "observed_start": temporal.get("dataset_start"),
            "observed_end": temporal.get("dataset_end"),
            "official_test_cutoff": temporal.get("predictive_splits_outcome_matured", {})
            .get("30", {})
            .get("test_cutoff"),
            "test_customer_count": max(
                (
                    row["n_customers"]
                    for row in purchase_metrics
                    if row["model"] == "Personalized"
                ),
                default=0,
            ),
            "forecast_horizons_days": purchase_metadata.get(
                "forecast_horizons_days", []
            ),
            "notebook_count": len(MODULES),
            "is_historical_demonstration": True,
            "is_live_business_prediction": False,
        },
        "notebook_registry": _module_registry(
            segmentation,
            temporal,
            purchase_metadata,
            spending_metadata,
            behavior,
            behavior_metadata,
            reliability,
            revenue_metadata,
            trajectory_metadata,
            notebook_summary,
            revenue,
            trajectory,
            root,
            inactivity_threshold,
        ),
        "research_hypotheses": hypotheses,
        "hypothesis_status_counts": dict(sorted(counts.items())),
        "additional_research_questions": trajectory_questions,
        "coverage_summary": {
            "temporal_splits": temporal["predictive_splits_outcome_matured"],
            "purchase_clock_test_customers_by_horizon": {
                str(horizon): max(
                    (
                        row["n_customers"]
                        for row in purchase_metrics
                        if row["horizon_days"] == horizon
                    ),
                    default=0,
                )
                for horizon in [30, 60, 90]
            },
            "behavior_locked_test_customers": behavior.get("profiling", {}).get(
                "customers_in_locked_test"
            ),
            "reliability_test_customers": reliability.get("evaluation", {}).get(
                "evaluation_customer_count"
            ),
            "revenue_exposure_test_customers": revenue.get("metadata", {}).get(
                "evaluation_customer_count"
            ),
            "trajectory": trajectory.get("data_scope", {}),
            "trajectory_method_eligibility": trajectory_metadata.get(
                "shape_cluster_eligible_counts", {}
            ),
            "trajectory_summary_eligible_test": trajectory_metadata.get(
                "eligible_customer_counts", {}
            ).get("30d_test_summary"),
            "functional_curve_evaluated_test": trajectory.get(
                "functional_analysis", {}
            ).get("test_evaluation", {}).get("evaluated_curves"),
        },
        "purchase_clock_evaluation": {
            "model_version": purchase_metadata.get("model_version"),
            "forecast_cutoff": temporal.get("predictive_splits_outcome_matured", {})
            .get("30", {})
            .get("test_cutoff"),
            "horizons_days": purchase_metadata.get("forecast_horizons_days", []),
            "test_metrics": purchase_metrics,
            "source_artifact": "data/metrics/notebook_evaluation_summary.json",
            "source_field": "purchase_clock.test_metrics",
            "selection_used_test_outcomes": False,
        },
        "spending_forecast_evaluation": {
            "model_version": spending_metadata.get("model_version"),
            "forecast_cutoff": temporal.get("predictive_splits_outcome_matured", {})
            .get("30", {})
            .get("test_cutoff"),
            "horizons_days": spending_metadata.get("forecast_horizons_days", []),
            "test_metrics": spending_metrics,
            "source_artifact": "data/metrics/notebook_evaluation_summary.json",
            "source_field": "spending_forecast.test_metrics",
            "saved_model_predictions_changed": False,
        },
        "behavior_evaluation": {
            "artifact_version": behavior.get("evaluation_version"),
            "result_status": behavior.get("result_status"),
            "candidate_f_status": behavior.get("candidate_f_status"),
            "policy_status": behavior_metadata.get("policy_status"),
            "model_comparison": behavior.get("model_comparison", []),
            "hypotheses": behavior.get("hypotheses", []),
            "limitations": behavior.get("limitations", []),
        },
        "reliability_evaluation": _compact_reliability(reliability),
        "revenue_exposure_evaluation": {
            "artifact_version": revenue.get("metadata", {}).get("artifact_version"),
            "metadata": revenue.get("metadata", {}),
            "financial_definitions": revenue.get("financial_definitions", {}),
            "portfolio_by_horizon": revenue.get("portfolio_by_horizon", {}),
            "ranking_selection_and_test_evaluation": revenue.get(
                "ranking_selection_and_test_evaluation", {}
            ),
            "hypotheses": revenue.get("hypotheses", {}),
            "scenario_sensitivity": {
                "metadata": scenario_sensitivity.get("metadata", {}),
                "scenario_count": len(scenario_sensitivity.get("scenario_results", [])),
                "scenario_ranges_by_horizon": _scenario_ranges(scenario_sensitivity),
                "forecast_perturbation_sensitivity": scenario_sensitivity.get(
                    "forecast_perturbation_sensitivity", []
                ),
                "scenario_selection_stability": scenario_sensitivity.get(
                    "scenario_selection_stability", {}
                ),
                "interpretation": scenario_sensitivity.get("interpretation", ""),
            },
            "limitations": revenue.get("limitations", []),
        },
        "trajectory_evaluation": {
            "artifact_version": trajectory_metadata.get("model_version"),
            "data_scope": trajectory.get("data_scope", {}),
            "method_eligibility": trajectory_metadata.get(
                "shape_cluster_eligible_counts", {}
            ),
            "cluster_selection": trajectory.get("cluster_selection", {}),
            "shape_cluster_selection": trajectory.get("shape_cluster_selection", {}),
            "functional_analysis": _compact_functional_analysis(
                trajectory.get("functional_analysis", {})
            ),
            "predictive_evaluation": trajectory.get("predictive_evaluation", {}),
            "limitations": trajectory_metadata.get("api_limitations", []),
        },
        "financial_definitions": {
            **revenue.get("financial_definitions", {}),
            "campaign_scenario_inputs": scenario_sensitivity.get("metadata", {}),
            "currency_code": revenue.get("metadata", {}).get("currency_code"),
            "interpretation": "Historical model-based quantities and hypothetical scenarios are not causal estimates, realized losses, recovered revenue, or current-business forecasts.",
        },
        "limitations": [
            "The analyses use a short, left-truncated historical dataset; a customer's first observed purchase is not necessarily acquisition.",
            "No observed purchase within a finite horizon is not proof of permanent churn.",
            "Historical model predictions and TEST evaluations are not current-business forecasts or individual guarantees.",
            "Notebook 08 does not support an operational alert policy; its conditional comparison remains unresolved.",
            "Reference-based revenue exposure is not estimable from the saved artifacts.",
            "Campaign response and uplift values are hypothetical; no intervention outcomes support a causal claim.",
            "Trajectory clusters and functional representations are descriptive and limited to customers meeting method-specific history support.",
        ],
        "source_manifest": source_refs,
    }
    # Fail closed if accidental customer-level or future-outcome rows are added.
    serialized = json.dumps(final, allow_nan=False)
    forbidden = ("customer_id", "customer_ids", "futureorders_", "future_revenue_")
    if any(token in serialized.lower() for token in forbidden):
        raise ValueError("Final evaluation must not contain customer-level IDs or target rows.")
    return final


def _scenario_ranges(sensitivity: dict[str, Any]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in sensitivity.get("scenario_results", []):
        grouped.setdefault(str(row["horizon_days"]), []).append(row)
    output: dict[str, dict[str, Any]] = {}
    for horizon, rows in sorted(grouped.items(), key=lambda entry: int(entry[0])):
        revenue_values = [
            row["hypothetical_incremental_revenue_gbp"]
            for row in rows
            if row.get("hypothetical_incremental_revenue_gbp") is not None
        ]
        costs = [row["campaign_cost_gbp"] for row in rows if row.get("campaign_cost_gbp") is not None]
        output[horizon] = {
            "rows": len(rows),
            "strategies": sorted({row["ranking_strategy"] for row in rows}),
            "hypothetical_incremental_revenue_gbp_range": (
                [min(revenue_values), max(revenue_values)] if revenue_values else None
            ),
            "campaign_cost_gbp_range": [min(costs), max(costs)] if costs else None,
            "causal_estimate": False,
        }
    return output


def _compact_functional_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    test_evaluation = analysis.get("test_evaluation", {})
    candidate_rows = analysis.get("validation_candidates", [])
    return {
        "status": analysis.get("status"),
        "method": analysis.get("method"),
        "fit_role": analysis.get("fit_role"),
        "validation_candidate_count": len(candidate_rows),
        "test_evaluation": test_evaluation,
        "score_relationships_with_static_and_behavior_features": analysis.get(
            "score_relationships_with_static_and_behavior_features", {}
        ),
    }


def encode_final_evaluation(value: dict[str, Any]) -> bytes:
    """Return stable UTF-8 JSON for checked-in, reproducible artifacts."""
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
