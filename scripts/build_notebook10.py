from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "10_Revenue_at_Risk_and_Retention_Planning.ipynb"


def markdown(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


cells = [
    markdown(
        r"""
# Notebook 10 — Revenue Exposure and Retention Planning

**Research project:** Customer Segmentation and Retention Analysis Using Machine Learning and Statistical Modelling<br>
**Forecast cutoff:** September 10, 2010 · **TEST cohort:** 3,373 customers<br>
**Currency:** GBP · **Models:** existing saved Purchase Clock and spending forecasts

> Historical research demonstration. It is not a current-business forecast, treatment-effect estimate, promise of recovered revenue, or individual guarantee.
"""
    ),
    markdown(
        """
## 01. Research objective and predeclared financial definitions

This notebook separates five different quantities:

1. **Current expected revenue:** saved purchase probability multiplied by saved
   conditional expected spending.
2. **Model disagreement:** differences between the personalized, historical-rate,
   and segment-aware forecasts. Alternative models are not counterfactuals.
3. **Revenue exposure:** a positive shortfall from a documented, same-customer,
   same-cutoff, same-horizon business reference. No eligible reference exists in
   the saved artifacts, so exposure is **not estimable**, not zero.
4. **Nonreturn-spending proxy:** `(1 − purchase probability) × conditional
   expected spending`. This is a screening proxy, not observed loss or
   recoverable revenue.
5. **Campaign scenarios:** explicitly hypothetical response and uplift inputs.
   No randomized intervention outcomes exist, so causal lift is not estimable.

The saved Purchase Clock and spending models are loaded without retraining or
modifying their artifacts. Future outcomes are kept separate from ranking
features and joined only after candidate rankings are frozen for evaluation.
"""
    ),
    code(
        """
import sys
from pathlib import Path

candidate_roots = [Path.cwd(), *Path.cwd().parents]
PROJECT_ROOT = next(
    root for root in candidate_roots
    if (root / "src" / "retention_research.py").is_file()
    and (root / "models" / "purchase_clock").is_dir()
)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

from src.retention_planner import (
    RANKING_STRATEGIES,
    RetentionScenario,
    allocate_contact_budget,
    rank_retention_candidates,
    simulate_retention_scenario,
)
from src.retention_research import (
    profile_warm_revenue_api,
    run_revenue_exposure_analysis,
)

analysis = run_revenue_exposure_analysis(PROJECT_ROOT)
evaluation = analysis["evaluation"]
scenario_sensitivity = analysis["scenario_sensitivity"]
profiling = analysis["profiling"]

print("Project root:", PROJECT_ROOT)
print("TEST cutoff:", evaluation["metadata"]["forecast_cutoff"])
print("TEST customers:", evaluation["metadata"]["evaluation_customer_count"])
print("Saved Purchase Clock:", evaluation["metadata"]["purchase_clock_model_version"])
print("Saved spending model:", evaluation["metadata"]["spending_model_version"])
model_metadata = json.loads(
    (PROJECT_ROOT / "models" / "revenue_exposure" / "metadata.json")
    .read_text(encoding="utf-8")
)
print("Research metadata only; no fitted model created:",
      model_metadata["fitted_model_created"] is False)
"""
    ),
    markdown(
        """
## 02. Current expected revenue, disagreements, and exposure status

The summary below reports portfolio totals from the saved forecasts. A model
difference is shown as a disagreement, not as a shortfall. Since a defensible
matched reference forecast is unavailable, the reference-based exposure field
must remain null.
"""
    ),
    code(
        """
portfolio = pd.DataFrame([
    {"horizon_days": int(horizon), **summary}
    for horizon, summary in evaluation["portfolio_by_horizon"].items()
])
display(
    portfolio[
        [
            "horizon_days",
            "eligible_customers",
            "personalized_expected_revenue_total_gbp",
            "historical_rate_forecast_total_gbp",
            "segment_forecast_total_gbp",
            "estimated_revenue_exposure_total_gbp",
            "exposure_status",
            "opportunity_proxy_total_gbp",
        ]
    ].round(2)
)
display(pd.DataFrame(evaluation["forecast_disagreements"]).T)

assert portfolio["exposure_status"].eq("not_estimable").all()
assert portfolio["estimated_revenue_exposure_total_gbp"].isna().all()
assert evaluation["financial_definitions"]["causal_effect"] is None
"""
    ),
    markdown(
        """
## 03. Customer and portfolio concentration

Historical gross spending is an observed historical quantity; personalized
expected revenue is a model output; the nonreturn proxy is a screening signal.
The top-customer shares below are descriptive concentrations only.
"""
    ),
    code(
        """
concentration = pd.DataFrame(evaluation["concentration"])
top_ten = concentration.loc[concentration["top_customer_share"].eq(0.10)]
display(
    top_ten.pivot(
        index="horizon_days",
        columns="metric",
        values="portfolio_share",
    ).round(3)
)

historical = top_ten.loc[
    top_ten["metric"].eq("historical_gross_spending_gbp")
].sort_values("horizon_days")
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(historical["horizon_days"].astype(str), historical["portfolio_share"] * 100,
       color="#246B5A", width=0.58)
ax.axhline(50, color="#B95532", linestyle="--", linewidth=1.2,
           label="Predeclared 50% threshold")
ax.set(title="Historical gross spending from the top 10% of customers",
       xlabel="Forecast horizon (days)", ylabel="Share of historical gross spending (%)")
ax.set_ylim(0, 100)
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.show()
"""
    ),
    markdown(
        """
## 04. Retention-ranking comparisons

Six deterministic screening strategies are compared at the top 1%, 5%, 10%,
and 20% budgets. For 30 and 60 days, one strategy is selected using prospective
validation outcomes among customers above the horizon-specific TRAIN 75th
percentile of historical gross spending. That rule is then frozen and assessed
on the September 10 TEST cohort. The 90-day cutoff has no prospective saved
vintage and is therefore descriptive only.

The target is the observed future nonpurchase rate—not recovered revenue or
campaign effectiveness. TEST outcomes do not choose the policy.
"""
    ),
    code(
        """
validation_selected = evaluation["validation_selected_strategy_evaluation"]
for horizon, result in validation_selected.items():
    print(f"{horizon}-day:", json.dumps(result, indent=2))

comparison_rows = []
for horizon, comparison in evaluation["ranking_selection_and_test_evaluation"].items():
    for item in comparison["test_historically_valuable_baseline_comparisons"]:
        comparison_rows.append({
            "horizon_days": int(horizon),
            "budget_fraction": item["budget_fraction"],
            "strategy": item["ranking_strategy"],
            "selected_customers": item["selected_customers"],
            "historically_valuable_future_nonpurchase_rate":
                item["future_nonpurchase_rate"],
            "selected_on_validation":
                item["ranking_strategy"] == comparison["selected_strategy_from_validation"],
        })
ranking_test = pd.DataFrame(comparison_rows)
display(ranking_test.pivot(
    index=["strategy", "budget_fraction"],
    columns="horizon_days",
    values="historically_valuable_future_nonpurchase_rate",
).round(3))
display(pd.DataFrame(evaluation["ranking_method_comparisons"]["30"]["comparisons"]).head(12))

assert evaluation["metadata"]["test_outcomes_used_for_selection"] is False
assert evaluation["ranking_selection_and_test_evaluation"]["90"][
    "selected_strategy_from_validation"
] is None
"""
    ),
    markdown(
        """
## 05. Ranking overlap and evidence limits

Low overlap means methods surface different customers; it does not establish
which group will respond to outreach. Bootstrap intervals below describe
nonpurchase-rate uncertainty within the fixed validation-selected TEST
selection. They do not include model-selection uncertainty or campaign uplift.
"""
    ),
    code(
        """
for horizon in ("30", "60"):
    rows = evaluation["ranking_method_comparisons"][horizon][
        "selection_overlap_at_10_percent"
    ]
    matrix = pd.DataFrame(rows).pivot(
        index="strategy_a",
        columns="strategy_b",
        values="jaccard_similarity",
    )
    print(f"{horizon}-day top-10% Jaccard overlap")
    display(matrix.round(2))

for horizon in ("30", "60"):
    result = validation_selected[horizon]
    print(
        horizon,
        "days: selected on validation =",
        result["selected_on_validation"],
        "| TEST high-value nonpurchase rate =",
        round(result["test_high_value_nonpurchase_rate"], 3),
        "| 95% fixed-cohort bootstrap =",
        result["test_selected_cohort_bootstrap_95"]["lower"],
        "to",
        result["test_selected_cohort_bootstrap_95"]["upper"],
        "| better than all matched TEST baselines =",
        result["improved_on_all_test_baselines"],
    )
"""
    ),
    markdown(
        """
## 06. Behavior indicators and historical reliability

Notebook 08 indicators are descriptive, optional eligibility filters. Sparse
history is surfaced as a coverage limitation; no numerical reliability
multiplier is applied to customer scores. Notebook 09 subgroup metrics describe
historical groups and do not guarantee an individual forecast.
"""
    ),
    code(
        """
behavior_support_rows = []
for horizon, forecast in analysis["forecast_tables"].items():
    for history_group, group in forecast.groupby("history_group", dropna=False):
        behavior_support_rows.append({
            "horizon_days": horizon,
            "history_group": history_group,
            "customers": int(len(group)),
            "sufficient_behavior_history":
                int(group["history_sufficiency"].eq("sufficient").sum()),
            "declining_purchase_rate":
                int(pd.to_numeric(group["purchase_rate_ratio"], errors="coerce").lt(1).sum()),
            "historical_reliability_status":
                group["reliability_status"].iloc[0],
            "historical_reliability_group_count":
                int(group["reliability_evidence_count"].iloc[0]),
        })
display(pd.DataFrame(behavior_support_rows))

print("Reliability evidence cutoff:", evaluation["metadata"]["forecast_cutoff"])
print("Reliability evidence is an individual guarantee:",
      analysis["forecast_tables"][30]["reliability_is_individual_guarantee"].any())
"""
    ),
    markdown(
        """
## 07. Hypothetical contact-budget scenarios

Each scenario varies a user-defined response probability, purchase uplift if
responded, contact cost, and campaign budget. Benefits use
`Δp = min(1 − p, response × uplift)` and `Δrevenue = Δp × conditional spending`.
No gross margin is assumed unless a user supplies one. The output is a planning
illustration, not a causal estimate or net-profit forecast.

### Illustrative break-even check

When an analyst supplies a gross-margin assumption, the code reports the
hypothetical response or purchase-uplift conditions required to cover contact
costs. Without margin, only revenue and contact cost are reported. These
algebraic thresholds are not observed or recommended campaign rates.
"""
    ),
    code(
        """
scenario_rows = pd.DataFrame(scenario_sensitivity["scenario_results"])
print("Scenario combinations:", len(scenario_rows))
display(
    scenario_rows.groupby(
        ["horizon_days", "ranking_strategy"], as_index=False
    ).agg(
        median_selected_contacts=("selected_customer_count", "median"),
        median_cost_gbp=("campaign_cost_gbp", "median"),
        median_hypothetical_revenue_gbp=(
            "hypothetical_incremental_revenue_gbp", "median"
        ),
        causal_estimate=("causal_estimate", "max"),
    ).head(18).round(2)
)

stability = [
    row
    for horizon in scenario_sensitivity["scenario_selection_stability"].values()
    for row in horizon["selection_stability"]
]
display(pd.DataFrame(stability).head(12))
assert not scenario_rows["causal_estimate"].any()

demo_scenario = RetentionScenario(
    horizon_days=30,
    campaign_budget_gbp=500,
    contact_cost_gbp=3,
    maximum_contacts=150,
    assumed_response_probability=0.20,
    assumed_purchase_uplift_if_responded=0.05,
    assumed_gross_margin_rate=0.35,
)
demo_ranked = rank_retention_candidates(
    analysis["forecast_tables"][30], "nonreturn_spending_proxy"
)
demo_contacts = allocate_contact_budget(
    demo_ranked, 500, 3, 150
)
demo_result = simulate_retention_scenario(demo_contacts, demo_scenario)
display(pd.DataFrame([{
    "selected_contacts": demo_result["selected_customer_count"],
    "campaign_cost_gbp": demo_result["campaign_cost_gbp"],
    "hypothetical_incremental_revenue_gbp":
        demo_result["hypothetical_incremental_revenue_gbp"],
    "hypothetical_contribution_gbp":
        demo_result["hypothetical_incremental_contribution_gbp"],
}]))
display(pd.DataFrame([demo_result["break_even_information"]]).T)
"""
    ),
    markdown(
        """
## 08. Forecast perturbation and hypothesis results

Probability and conditional-spending perturbations are illustrative sensitivity
checks—not calibrated confidence intervals. The final table reports each
predeclared research hypothesis from the corresponding data and frozen
evaluation procedure.
"""
    ),
    code(
        """
display(pd.DataFrame(scenario_sensitivity["forecast_perturbation_sensitivity"]).head(18))
display(pd.DataFrame([
    {"hypothesis": name, **details}
    for name, details in evaluation["hypotheses"].items()
]))

print("Validation cutoffs:")
display(pd.DataFrame(evaluation["validation_cutoffs"]).T)
"""
    ),
    markdown(
        """
## 09. Reproducibility, runtime, and saved outputs

This analysis uses saved data and model artifacts, does not fit a new model, and
does not modify the Purchase Clock or spending forecast artifacts. Runtime
measurements come from the current locked Python environment; API timings are
measured after an initial warm-up request using FastAPI's in-process client.
"""
    ),
    code(
        """
display(pd.DataFrame([
    {"operation": name, "milliseconds": value}
    for name, value in profiling["timings"].items()
]))
api_profile = profile_warm_revenue_api(PROJECT_ROOT, repetitions=5)
profiling = json.loads(
    (PROJECT_ROOT / "data" / "metrics" / "revenue_exposure_profiling.json")
    .read_text(encoding="utf-8")
)
display(pd.DataFrame([
    {
        "endpoint": name,
        "median_ms": details["median_ms"],
        "p95_ms": details["p95_ms"],
        "status_codes": details["status_codes"],
    }
    for name, details in api_profile["endpoints"].items()
]))
print("Environment:", profiling["environment"])
print("Saved metrics:")
for name in (
    "revenue_exposure_evaluation.json",
    "retention_scenario_sensitivity.json",
    "revenue_exposure_profiling.json",
):
    print(" -", PROJECT_ROOT / "data" / "metrics" / name)
print("Saved metadata:", PROJECT_ROOT / "models" / "revenue_exposure" / "metadata.json")
"""
    ),
    markdown(
        """
## 10. Conclusions and limitations

The research reports distinct financial quantities and avoids treating alternate
forecasts as revenue losses. A matched, documented reference is absent, so
reference-based exposure remains not estimable. The nonreturn proxy can support
screening, but not a financial loss claim. Contact scenarios depend on
hypothetical assumptions and cannot estimate causal benefit.

Ranking rules are selected on validation and evaluated on one locked TEST
cohort. A policy that fails to outperform simple baselines on TEST is reported
as such; the policy is not retuned on TEST. The 90-day ranking results are
exploratory because no eligible prospective validation vintage exists.
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
        "language_info": {"name": "python"},
    },
)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(notebook, OUTPUT)
print(OUTPUT)
