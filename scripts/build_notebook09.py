from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "09_Prediction_Reliability_and_Explainability.ipynb"


def markdown(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


cells = [
    markdown(
        r"""
# Notebook 09 — Prediction Reliability and Explainability

**Research project:** Customer Segmentation and Retention Analysis Using Machine Learning and Statistical Modelling
**Scope:** explain the saved Purchase Clock and conditional-spending models; evaluate frozen historical forecasts.
**Forecast cutoff:** September 10, 2010 · **TEST cohort:** 3,373 customers.

> Historical demonstration only. These forecasts reproduce saved-model outputs at a recorded 2010 cutoff. They are not current-business predictions, recommendations, or guarantees.
"""
    ),
    markdown(
        """
## 01. Research objective and introduction

This study explains why the saved models assign their historical 30/60/90-day
purchase and expected-revenue forecasts, measures retrospective calibration,
and summarizes empirical performance for cutoff-valid customer groups. It
preserves the existing fitted models and predictions. TEST outcomes are used
only for retrospective evaluation, never to fit references, select bin edges,
or tune a forecasting method.
"""
    ),
    markdown(
        """
## 02. Existing model architecture

The Purchase Clock is the saved `purchase-clock-v2` binary logistic hazard
pipeline. The fitted preprocessing transforms the customer-level historical
features and expands them across nine 10-day interval indicators. The final
model has 21 transformed inputs. Cumulative P30/P60/P90 are reconstructed from
the saved conditional interval hazards, not from an independent horizon model.

The spending bundle is `spending-forecast-v2`: horizon-specific Ridge pipelines
for conditional 30/60/90-day spending. They preserve saved imputation, feature
transformation, clipping, scaling, categorical encoding, log-space target
training, and the fitted smearing correction used for retransformation.

The exact bundle metadata and fitted feature counts below come from the
committed saved artifacts. No model is retrained in this notebook.
"""
    ),
    markdown(
        """
## 03. Formal explanation methodology and temporal rules

For interval `t`, the logistic score is `β₀ + Σ βⱼ zⱼ`; its fitted hazard is
`sigmoid(score)`. The additive terms are exact only in transformed log-odds
space. Cumulative purchase probability is nonlinear:

`P(T ≤ H) = 1 − ∏ₜ₌₁ᴴ (1 − hₜ)`.

For cumulative explanation, each individual feature is replaced with a
TRAIN-derived median or deterministic categorical mode, then the complete
hazard curve is recomputed. The signed value is original probability minus
reference-replacement probability. These are model-input sensitivities, not
causal effects; replacing correlated or derived features independently can
produce an unrealistic profile.

All TEST features use only transactions strictly before 2010-09-10. Reference
profiles and numeric 1st/99th percentile support ranges use saved-model TRAIN
rows only. Validation probabilities, available before the forecast cutoff,
select diagnostic calibration bins. TEST outcomes do not select or tune the
method.
"""
    ),
    code(
        """
import sys
from pathlib import Path

candidate_roots = [Path.cwd(), *Path.cwd().parents]
PROJECT_ROOT = next(
    root for root in candidate_roots
    if (root / "src" / "purchase_clock.py").is_file()
    and (root / "models" / "purchase_clock").is_dir()
)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

from src import purchase_clock as pc
from src import spending_model as sm
from src.explainability import (
    decompose_expected_revenue,
    explain_conditional_spending,
    explain_customer_purchase_clock,
)
from src.prediction_reliability import assess_distribution_support
from src.reliability_research import (
    profile_warm_api_endpoints,
    run_reliability_analysis,
)

analysis = run_reliability_analysis(PROJECT_ROOT)
artifact = analysis["artifact"]
evaluation = artifact["evaluation"]
reference_profile = analysis["reference_profile"]
test_features = analysis["test_features"]
test_predictions = analysis["test_predictions"]
profile = analysis["profiling"]

print("Project root:", PROJECT_ROOT)
print("TEST cutoff:", artifact["metadata"]["forecast_cutoff"])
print("TEST customers:", evaluation["evaluation_customer_count"])
print("Purchase Clock:", artifact["metadata"]["purchase_clock_model_version"])
print("Spending model:", artifact["metadata"]["spending_model_version"])
"""
    ),
    markdown(
        """
## 04. Conditional hazard decomposition

The case below is selected by lowest eligible customer ID, not by outcome or
forecast quality. Each interval row reports its actual fitted hazard and the
largest absolute transformed logit contributions. The reconstruction is checked
against the saved fitted estimator at `rtol=1e-10`, `atol=1e-12`.
"""
    ),
    code(
        """
purchase_case = analysis["purchase_case_explanation"]
hazard_rows = []
for interval in purchase_case["interval_decompositions"]:
    largest = interval["feature_contributions"][0]
    hazard_rows.append({
        "interval_days": interval["interval_days"],
        "hazard": interval["predicted_hazard"],
        "reconstructed_hazard": interval["reconstructed_hazard"],
        "logit_intercept": interval["logit_intercept"],
        "largest_logit_feature": largest["model_feature"],
        "largest_logit_contribution": largest["logit_contribution"],
    })
display(pd.DataFrame(hazard_rows).round(6))
print("Exact reconstruction tolerance:", purchase_case["reconstruction_tolerance"])
"""
    ),
    markdown(
        """
## 05. Cumulative purchase probability explanation

The table compares the original P30/P60/P90 forecast with the combined
TRAIN-derived reference profile. Single-input sensitivities are directional
comparisons against that feature's reference replacement; they are not additive
contributions and do not sum to the total probability.
"""
    ),
    code(
        """
cumulative_rows = []
for horizon in (30, 60, 90):
    cumulative_rows.append({
        "horizon_days": horizon,
        "saved_model_probability": purchase_case["purchase_probabilities"][str(horizon)],
        "combined_train_reference_probability": purchase_case[
            "reference_profile_probabilities"
        ][str(horizon)],
    })
display(pd.DataFrame(cumulative_rows).style.format({
    "saved_model_probability": "{:.4f}",
    "combined_train_reference_probability": "{:.4f}",
}))
effect_rows = []
for effect in purchase_case["feature_effects"]:
    effect_rows.append({
        "feature": effect["feature"],
        "original_value": effect["original_value"],
        "train_reference": effect["reference_value"],
        "P30_effect": effect["probability_effects"]["30"],
        "P60_effect": effect["probability_effects"]["60"],
        "P90_effect": effect["probability_effects"]["90"],
    })
display(pd.DataFrame(effect_rows).round(5))
print("Direction:", "original probability minus reference-replacement probability")
print("Limitations:", *purchase_case["model_input_limitations"], sep="\\n- ")
"""
    ),
    markdown(
        """
## 06. Conditional spending explanation

Each horizon uses its own saved spending pipeline and TRAIN reference profile.
The log score is reconstructed from the fitted Ridge intercept and transformed
feature contributions. Currency output is the saved pipeline's smearing-adjusted
conditional estimate; individual log-space terms are not additive pound values.
"""
    ),
    code(
        """
case_features = (
    test_features.sort_values("Customer ID")
    .iloc[[0]]
    .loc[:, list(sm.BASE_FEATURE_COLUMNS)]
    .reset_index(drop=True)
)
spending_rows = []
spending_explanations = {}
for horizon in (30, 60, 90):
    explanation = explain_conditional_spending(
        analysis["spending_bundle"],
        case_features,
        horizon,
        reference_profile["spending"][str(horizon)]["reference_values"],
    )
    spending_explanations[horizon] = explanation
    spending_rows.append({
        "horizon_days": horizon,
        "conditional_expected_spending": explanation["conditional_expected_spending"],
        "log_score": explanation["log_score"],
        "retransformation": explanation["retransformation_method"],
        "largest_log_score_feature": explanation["log_score_contributions"][0][
            "model_feature"
        ],
    })
display(pd.DataFrame(spending_rows).round(4))
"""
    ),
    markdown(
        """
## 07. Expected revenue decomposition

The saved forecast is checked as purchase probability multiplied by
conditional expected spending. All three values come from the actual saved
model pipelines for the selected TEST customer; no near-zero division is used.
"""
    ),
    code(
        """
case_id = int(case_features.iloc[0]["Customer ID"])
saved_case_forecast = test_predictions.loc[
    test_predictions["Customer ID"].eq(case_id)
].iloc[0]
revenue_rows = []
for horizon in (30, 60, 90):
    saved_probability = float(saved_case_forecast[f"personalized_P{horizon}"])
    saved_revenue = float(
        saved_case_forecast[f"personalized_expected_revenue_{horizon}d"]
    )
    decomposition = decompose_expected_revenue(
        saved_probability,
        spending_explanations[horizon]["conditional_expected_spending"],
        saved_revenue,
    )
    revenue_rows.append({
        "horizon_days": horizon,
        "purchase_probability": decomposition["purchase_probability"],
        "conditional_expected_spending": decomposition[
            "conditional_expected_spending"
        ],
        "saved_expected_revenue": decomposition["personalized_expected_revenue"],
        "reconstructed_expected_revenue": decomposition[
            "reconstructed_expected_revenue"
        ],
    })
display(pd.DataFrame(revenue_rows).round(4))
"""
    ),
    markdown(
        """
## 08. Calibration analysis

Calibration is evaluated retrospectively on the fixed TEST cohort after edges
were frozen from eligible validation probabilities. ECE is the bin-count-weighted
absolute gap; MCE is the largest populated-bin gap. Neither is a universal
reliability score.
"""
    ),
    code(
        """
calibration_table = pd.DataFrame(evaluation["purchase_calibration"])[[
    "horizon_days", "customer_count", "mean_predicted_probability",
    "observed_purchase_rate", "signed_calibration_gap", "brier_score",
    "log_loss", "roc_auc", "average_precision",
    "expected_calibration_error", "maximum_calibration_error",
]]
display(calibration_table.round(4))

fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharex=True, sharey=True)
for axis, result in zip(axes, evaluation["purchase_calibration"], strict=True):
    bins = pd.DataFrame(result["calibration_bins"])
    populated = bins.loc[bins["customer_count"].gt(0)]
    axis.plot([0, 1], [0, 1], color="#68756d", linestyle="--", linewidth=1)
    points = axis.scatter(
        populated["mean_predicted_probability"],
        populated["observed_purchase_rate"],
        s=20 + np.sqrt(populated["customer_count"]) * 2,
        c="#315a4c",
        alpha=0.78,
    )
    axis.set_title(f'P{result["horizon_days"]} · n={result["customer_count"]:,}')
    axis.set_xlabel("Mean predicted probability")
    axis.grid(alpha=0.18)
axes[0].set_ylabel("Observed purchase rate")
fig.suptitle("Frozen-bin historical reliability diagrams")
fig.tight_layout()
plt.show()
"""
    ),
    markdown(
        """
## 09. Calibration bin sensitivity

Edges are selected from validation predictions using a minimum support of 30
per populated bin, then maximum minimum-bin support and fewer empty bins.
Sensitivity compares the frozen selection with equal-width bins; the TEST
comparison is diagnostic only and does not change the selected policy.
"""
    ),
    code(
        """
bin_sensitivity = pd.DataFrame(evaluation["calibration_bin_sensitivity"])
display(bin_sensitivity)
selection_rows = []
for horizon, selection in artifact["validation"]["bin_selection_by_horizon"].items():
    chosen = selection["binning"]["selected_candidate"]
    selection_rows.append({
        "horizon_days": int(horizon),
        "validation_cutoff": selection["validation_cutoff"],
        "validation_customers": selection["validation_customer_count"],
        "selected_method": selection["binning"]["selected_method"],
        "minimum_populated_bin_support": chosen["minimum_populated_bin_support"],
        "empty_bins": chosen["empty_bins"],
        "minimum_required_support": selection["binning"][
            "minimum_validation_bin_support"
        ],
    })
display(pd.DataFrame(selection_rows))
"""
    ),
    markdown(
        """
## 10. Reliability by customer history

History groups are defined from cutoff-time purchase frequency: exactly one,
two to four, and five or more purchases. The 100-customer support threshold was
fixed in the analysis configuration before the TEST results were examined.
"""
    ),
    code(
        """
history_results = pd.DataFrame([
    row for row in evaluation["subgroups"]
    if row["group_type"] == "history_group"
])
history_30 = history_results.loc[history_results["horizon_days"].eq(30)].copy()
display(history_30[[
    "group", "customer_count", "mean_predicted_probability",
    "observed_purchase_rate", "brier_score", "average_precision",
    "calibration_gap", "status",
]].sort_values("group").round(4))
fig, axis = plt.subplots(figsize=(8, 4))
ordered = history_30.sort_values("group")
axis.bar(ordered["group"], ordered["brier_score"], color="#78918a")
axis.set_ylabel("Brier score · lower is better")
axis.set_title("30-day Brier score by cutoff-time purchase history")
axis.tick_params(axis="x", rotation=12)
axis.grid(axis="y", alpha=0.18)
fig.tight_layout()
plt.show()
"""
    ),
    markdown(
        """
## 11. Reliability by historical forecast-time segment

These are the saved forecast-time segment labels, not full-period
retrospective descriptive clusters. Segment metrics are historical subgroup
evidence and do not imply causal effects or future guarantees.
"""
    ),
    code(
        """
segment_results = pd.DataFrame([
    row for row in evaluation["subgroups"]
    if row["group_type"] == "Hist_Segment"
])
segment_30 = segment_results.loc[segment_results["horizon_days"].eq(30)].copy()
display(segment_30[[
    "group", "customer_count", "mean_predicted_probability",
    "observed_purchase_rate", "brier_score", "average_precision",
    "calibration_gap", "status",
]].sort_values("group").round(4))
fig, axis = plt.subplots(figsize=(8, 4))
ordered = segment_30.sort_values("group")
axis.bar(ordered["group"], ordered["calibration_gap"], color="#c57d5c")
axis.axhline(0, color="#68756d", linewidth=1)
axis.set_ylabel("Mean predicted − observed purchase rate")
axis.set_title("30-day signed calibration gap by historical segment")
axis.grid(axis="y", alpha=0.18)
fig.tight_layout()
plt.show()
"""
    ),
    markdown(
        """
## 12. Customer-level bootstrap confidence intervals

The fixed-model percentile bootstrap resamples complete customer observations
with replacement within each cutoff, horizon, and group. It quantifies
empirical group-metric uncertainty, not model-parameter uncertainty or an
individual customer's outcome probability.
"""
    ),
    code(
        """
bootstrap = pd.DataFrame(evaluation["bootstrap_intervals"])
history_bootstrap = bootstrap.loc[
    bootstrap["group_type"].eq("history_group")
    & bootstrap["horizon_days"].eq(30)
    & bootstrap["metric"].isin([
        "observed_purchase_rate", "calibration_gap", "brier_score"
    ])
]
display(history_bootstrap[[
    "group", "metric", "customer_count", "lower", "upper",
    "successful_bootstrap_samples", "status",
]].sort_values(["group", "metric"]).round(5))
revenue_intervals = bootstrap.loc[
    bootstrap["group_type"].eq("history_group")
    & bootstrap["horizon_days"].eq(30)
    & bootstrap["metric"].eq("mean_forecast_bias")
    & bootstrap["revenue_model"].eq("Personalized two-stage")
]
display(revenue_intervals[[
    "group", "revenue_model", "customer_count", "lower", "upper",
    "successful_bootstrap_samples", "status",
]].sort_values("group").round(3))
"""
    ),
    markdown(
        """
## 13. Feature-distribution support

Numeric support flags use the TRAIN-only 1st/99th percentile bounds; categorical
flags compare observed labels with the TRAIN category set. These indicate
whether a feature value is outside the chosen historical support range. They
are not probabilities of model failure.
"""
    ),
    code(
        """
purchase_bundle = analysis["purchase_bundle"]
support_customer = case_features.iloc[0].to_dict()
purchase_inputs = pc._apply_bundle_segmentation(
    purchase_bundle, case_features
).iloc[0].to_dict()
purchase_support = assess_distribution_support(
    purchase_inputs, reference_profile["purchase_clock"]
)
support_rows = [{"model_scope": "purchase_clock", **flag}
                for flag in purchase_support["flags"]]
for horizon in (30, 60, 90):
    spending_inputs = sm.apply_spending_segmentation(
        analysis["spending_bundle"], case_features, horizon
    ).iloc[0].to_dict()
    assessed = assess_distribution_support(
        spending_inputs, reference_profile["spending"][str(horizon)]
    )
    support_rows.extend(
        {"model_scope": f"spending_{horizon}d", **flag}
        for flag in assessed["flags"]
    )
display(pd.DataFrame(support_rows))
print(purchase_support["interpretation"])
"""
    ),
    markdown(
        """
## 14. Spending forecast reliability

MAE, RMSE, mean bias, and portfolio totals follow Notebook 07's original TEST
definition. Error distributions are shown without MAPE because actual zero
revenue makes that percentage undefined. Large-spender sensitivity is explicitly
retrospective and did not select the forecast or thresholds.
"""
    ),
    code(
        """
revenue_metrics = pd.DataFrame(evaluation["revenue"])
display(revenue_metrics[[
    "horizon_days", "model", "n_customers", "mae", "rmse",
    "mean_forecast_bias", "total_predicted_revenue",
    "total_actual_revenue", "total_revenue_bias",
]].round(2))
fig, axis = plt.subplots(figsize=(9, 4))
personalized = revenue_metrics.loc[
    revenue_metrics["model"].eq("Personalized two-stage")
]
axis.bar(
    personalized["horizon_days"].astype(str),
    personalized["mean_forecast_bias"],
    color="#78918a",
)
axis.axhline(0, color="#68756d", linewidth=1)
axis.set_xlabel("Forecast horizon (days)")
axis.set_ylabel("Mean predicted − actual revenue")
axis.set_title("Personalized expected-revenue bias on fixed TEST")
axis.grid(axis="y", alpha=0.18)
fig.tight_layout()
plt.show()
display(pd.DataFrame(evaluation["large_spender_sensitivity"])[[
    "horizon_days", "model", "large_spender_count",
    "actual_revenue_threshold", "interpretation",
]])
"""
    ),
    markdown(
        """
## 15. Representative customer case studies

For each available purchase-history group, the selected profile is the
lowest customer ID in the eligible TEST feature cohort. Selection uses only
history-group membership and ID, not future outcomes, calibration error, or
forecast quality. Customer rows below show saved predictions and feature
support flags, never TEST outcome labels.
"""
    ),
    code(
        """
case_source = test_features[["Customer ID", "Frequency", "Recency"]].copy()
case_source["history_group"] = np.select(
    [
        case_source["Frequency"].eq(1),
        case_source["Frequency"].between(2, 4),
        case_source["Frequency"].ge(5),
    ],
    [
        "Exactly one purchase",
        "Two to four purchases",
        "Five or more purchases",
    ],
    default="Unknown history",
)
case_summary_rows = []
case_effect_tables = {}
for group_name in [
    "Exactly one purchase",
    "Two to four purchases",
    "Five or more purchases",
]:
    available = case_source.loc[case_source["history_group"].eq(group_name)]
    if available.empty:
        continue
    chosen_id = int(available.sort_values("Customer ID").iloc[0]["Customer ID"])
    chosen_features = (
        test_features.loc[test_features["Customer ID"].eq(chosen_id)]
        .iloc[[0]]
        .loc[:, list(sm.BASE_FEATURE_COLUMNS)]
        .reset_index(drop=True)
    )
    forecast = test_predictions.loc[
        test_predictions["Customer ID"].eq(chosen_id)
    ].iloc[0]
    explanation = explain_customer_purchase_clock(
        purchase_bundle,
        chosen_features,
        reference_profile["purchase_clock"]["reference_values"],
    )
    flags = assess_distribution_support(
        pc._apply_bundle_segmentation(purchase_bundle, chosen_features)
        .iloc[0]
        .to_dict(),
        reference_profile["purchase_clock"],
    )
    case_summary_rows.append({
        "customer_id": chosen_id,
        "history_group": group_name,
        "frequency": int(available.iloc[0]["Frequency"]),
        "recency_days": float(available.iloc[0]["Recency"]),
        "P30": float(forecast["personalized_P30"]),
        "P60": float(forecast["personalized_P60"]),
        "P90": float(forecast["personalized_P90"]),
        "expected_revenue_30d": float(
            forecast["personalized_expected_revenue_30d"]
        ),
        "expected_revenue_60d": float(
            forecast["personalized_expected_revenue_60d"]
        ),
        "expected_revenue_90d": float(
            forecast["personalized_expected_revenue_90d"]
        ),
        "atypical_purchase_inputs": flags["atypical_feature_count"],
        "cutoff": artifact["metadata"]["forecast_cutoff"],
    })
    case_effect_tables[group_name] = pd.DataFrame([
        {
            "feature": effect["feature"],
            "reference_value": effect["reference_value"],
            "P30_sensitivity": effect["probability_effects"]["30"],
            "P60_sensitivity": effect["probability_effects"]["60"],
            "P90_sensitivity": effect["probability_effects"]["90"],
        }
        for effect in explanation["feature_effects"][:5]
    ])
case_studies = pd.DataFrame(case_summary_rows)
display(case_studies.round(4))
for group_name, effects in case_effect_tables.items():
    print(group_name, "· largest absolute single-input sensitivities")
    display(effects.round(5))
"""
    ),
    markdown(
        """
## 16. Limitations and interpretation

- The TEST cohort is a historical evaluation, not a live or current forecast.
- The final 90-day spending model has no eligible prospective validation
  vintage; its TEST revenue results are retrospective.
- ECE/MCE depend on the frozen bins, and some individual bins remain small.
- Bootstrap intervals quantify empirical fixed-model group metrics, not
  parameter or individual-outcome uncertainty.
- A reference profile and single-feature substitution can be unrealistic for
  correlated or derived inputs. They are not causal interventions.
- A TRAIN-range flag is a support diagnostic, not a probability of failure.
- High-spending customers can dominate portfolio errors; the TEST-defined
  99th-percentile sensitivity is retrospective only.
- No calibrator was fitted, no saved model was changed, and no unsupported
  customer reliability percentage is reported.

Aleatoric uncertainty is the remaining randomness in a future purchase;
epistemic uncertainty concerns finite-data model estimation; empirical
calibration uncertainty concerns finite evaluation groups. Only the last is
quantified here, using customer-level resampling.
"""
    ),
    markdown(
        """
## 17. Final research findings and artifact export

The saved 30/60/90-day purchase probabilities preserve the original model
outputs and ordering. This analysis adds exact transformed-space hazard
decomposition, TRAIN-reference probability sensitivity, horizon-specific
conditional-spending explanations, frozen-bin reliability diagrams, subgroup
metrics, and customer-level bootstrap intervals. Reliability remains a set of
diagnostics and evidence limitations, not a scalar customer score.

The final cell records warm endpoint latency after one in-process warm-up
request, then lists the versioned outputs written by the reusable `src/`
research code.
"""
    ),
    code(
        """
warm_api = profile_warm_api_endpoints(PROJECT_ROOT, repetitions=5)
warm_rows = [
    {
        "endpoint": name,
        "median_ms": values["median_ms"],
        "p95_ms": values["p95_ms"],
        "successful_repetitions": values["successful_repetitions"],
        "measurement": values["measurement"],
    }
    for name, values in warm_api["endpoints"].items()
]
display(pd.DataFrame(warm_rows).round(2))

artifact_paths = [
    "data/metrics/prediction_reliability_evaluation.json",
    "data/metrics/prediction_reliability_profiling.json",
    "models/prediction_reliability/metadata.json",
    "models/prediction_reliability/reference_profile.json",
]
print("Artifacts written:")
for path in artifact_paths:
    print("-", path)
print("Profiling environment:", profile["environment"])
print("Measured warm API endpoints:", warm_api["status"])
"""
    ),
]

notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.11",
        },
    },
)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(notebook, OUTPUT)
print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(cells)} cells.")
