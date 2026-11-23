from __future__ import annotations

import pandas as pd
import pytest

from src import retention_research
from src.retention_planner import RANKING_STRATEGIES, RetentionScenario
from src.retention_research import (
    bootstrap_ranking_metrics,
    compare_ranking_baselines,
    evaluate_ranking_at_budget,
    evaluate_scenario_sensitivity,
    measure_selection_overlap,
)


def _rank(ids: list[int]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ids,
            "priority_rank": range(1, len(ids) + 1),
            "priority_score": range(len(ids), 0, -1),
        }
    )


def test_ranking_metrics_require_exact_outcome_alignment() -> None:
    scores = _rank([1, 2, 3, 4])
    outcomes = pd.DataFrame(
        {"customer_id": [1, 2, 3, 4], "purchased": [0, 0, 1, 1]}
    )
    result = evaluate_ranking_at_budget(scores, outcomes, 0.5)
    assert result["selected_customers"] == 2
    assert result["future_nonpurchase_rate"] == 1
    assert "selected_customer_ids" not in result

    with pytest.raises(ValueError, match="match exactly"):
        evaluate_ranking_at_budget(scores, outcomes.iloc[:-1], 0.5)


def test_validation_selects_policy_without_reading_test_for_selection() -> None:
    validation = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4],
            "purchased": [0, 0, 1, 1],
            "historically_valuable": [True] * 4,
        }
    )
    test = pd.DataFrame(
        {
            "customer_id": [11, 12, 13, 14],
            "purchased": [1, 1, 0, 0],
            "historically_valuable": [True] * 4,
        }
    )
    policies = {
        "historical_gross_spending": {
            "validation": _rank([3, 4, 1, 2]),
            "test": _rank([11, 12, 13, 14]),
        },
        "recency_only": {
            "validation": _rank([1, 2, 3, 4]),
            "test": _rank([13, 14, 11, 12]),
        },
    }
    result = compare_ranking_baselines(
        validation,
        test,
        policies,
        budget_fractions=(0.5,),
        selection_fraction=0.5,
    )
    assert result["selected_strategy_from_validation"] == "recency_only"
    assert result["test_selection_used"] is False
    assert result["validation_selected_test_result"]["future_nonpurchase_rate"] == 1
    assert "selected_customer_ids" not in str(result)
    assert len(result["test_historically_valuable_baseline_comparisons"]) == 2


def test_no_prospective_validation_means_no_selected_test_winner() -> None:
    test = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "purchased": [0, 1],
            "historically_valuable": [True, True],
        }
    )
    result = compare_ranking_baselines(
        None,
        test,
        {"recency_only": {"test": _rank([1, 2])}},
    )
    assert result["selected_strategy_from_validation"] is None
    assert result["validation_selected_test_result"] is None
    assert result["validation_status"] == "no_prospective_validation"


def test_bootstrap_is_reproducible_and_reports_only_fixed_cohort_metric() -> None:
    cohort = pd.DataFrame({"customer_id": [1, 2, 3, 4], "purchased": [0, 0, 1, 1]})
    first = bootstrap_ranking_metrics(cohort, {"resamples": 200, "seed": 7})
    second = bootstrap_ranking_metrics(cohort, {"resamples": 200, "seed": 7})
    assert first == second
    assert first["estimate"] == 0.5
    assert first["method"].startswith("customer-level percentile bootstrap")


def test_selection_overlap_is_pairwise_and_handles_empty_sets() -> None:
    overlap = measure_selection_overlap(
        {"a": [1, 2, 3], "b": [2, 3, 4], "empty": []}
    )
    pair = overlap.loc[
        overlap["strategy_a"].eq("a") & overlap["strategy_b"].eq("b")
    ].iloc[0]
    assert pair["intersection"] == 2
    assert pair["jaccard_similarity"] == pytest.approx(0.5)
    empty = overlap.loc[
        overlap["strategy_a"].eq("empty") & overlap["strategy_b"].eq("empty")
    ].iloc[0]
    assert pd.isna(empty["jaccard_similarity"])


def test_scenario_sensitivity_reuses_allocations_and_stays_hypothetical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    forecasts = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "horizon_days": [30] * 3,
            "purchase_probability": [0.1, 0.5, 0.9],
            "conditional_expected_spending_gbp": [100.0, 200.0, 300.0],
            "historical_gross_spending_gbp": [50.0, 200.0, 300.0],
            "recency_days": [90.0, 30.0, 10.0],
            "nonreturn_probability": [0.9, 0.5, 0.1],
            "nonreturn_weighted_conditional_spending_proxy_gbp": [
                90.0,
                100.0,
                30.0,
            ],
        }
    )
    scenarios = [
        RetentionScenario(
            horizon_days=30,
            campaign_budget_gbp=10,
            contact_cost_gbp=1,
            maximum_contacts=10,
            assumed_response_probability=response,
            assumed_purchase_uplift_if_responded=uplift,
        )
        for response in (0.1, 0.2)
        for uplift in (0.05, 0.1)
    ]
    original_allocate = retention_research.allocate_contact_budget
    allocation_calls = 0

    def counted_allocate(*args, **kwargs):
        nonlocal allocation_calls
        allocation_calls += 1
        return original_allocate(*args, **kwargs)

    monkeypatch.setattr(
        retention_research, "allocate_contact_budget", counted_allocate
    )
    result = evaluate_scenario_sensitivity(
        forecasts,
        scenarios,
        strategies=("historical_gross_spending",),
    )
    assert result["scenario_count"] == 4
    assert result["strategy_count"] == 1
    assert allocation_calls == 1
    assert all(not row["causal_estimate"] for row in result["results"])
    assert result["selection_stability"][0][
        "same_budget_response_uplift_jaccard_min"
    ] == 1


def test_ranking_strategy_inventory_is_frozen() -> None:
    assert len(RANKING_STRATEGIES) == 6


def test_scenario_sensitivity_preserves_margin_contribution_equation() -> None:
    forecasts = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "horizon_days": [30] * 3,
            "purchase_probability": [0.1, 0.5, 0.9],
            "conditional_expected_spending_gbp": [100.0, 200.0, 300.0],
            "historical_gross_spending_gbp": [50.0, 200.0, 300.0],
            "recency_days": [90.0, 30.0, 10.0],
            "nonreturn_probability": [0.9, 0.5, 0.1],
            "nonreturn_weighted_conditional_spending_proxy_gbp": [
                90.0,
                100.0,
                30.0,
            ],
        }
    )
    scenario = RetentionScenario(
        horizon_days=30,
        campaign_budget_gbp=1,
        contact_cost_gbp=1,
        maximum_contacts=1,
        assumed_response_probability=0.5,
        assumed_purchase_uplift_if_responded=0.2,
        assumed_gross_margin_rate=0.4,
    )
    result = evaluate_scenario_sensitivity(
        forecasts,
        [scenario],
        strategies=("historical_gross_spending",),
    )["results"][0]
    assert result["selected_customer_count"] == 1
    assert result["hypothetical_incremental_revenue_gbp"] == pytest.approx(30)
    assert result["hypothetical_incremental_contribution_gbp"] == pytest.approx(11)
