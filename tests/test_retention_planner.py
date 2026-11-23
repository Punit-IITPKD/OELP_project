from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.retention_planner import (
    EligibilityPolicy,
    RetentionScenario,
    allocate_contact_budget,
    calculate_break_even_conditions,
    compare_retention_strategies,
    rank_retention_candidates,
    simulate_retention_scenario,
)


def forecasts() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [30, 10, 20, 40],
            "purchase_probability": [0.2, 0.8, 0.5, 0.9],
            "conditional_expected_spending_gbp": [100.0, 250.0, 300.0, 0.0],
            "historical_gross_spending_gbp": [500.0, 1000.0, 700.0, 50.0],
            "recency_days": [90.0, 10.0, 50.0, 120.0],
            "nonreturn_weighted_conditional_spending_proxy_gbp": [80.0, 50.0, 150.0, 0.0],
            "hist_segment": ["Lapsed / At-Risk", "Recent / Active", "Lapsed / At-Risk", "Lapsed / At-Risk"],
            "history_group": ["Five or more purchases", "Exactly one purchase", "Two to four purchases", "Exactly one purchase"],
            "history_sufficiency": ["sufficient", "sufficient", "limited", "insufficient"],
            "purchase_rate_ratio": [0.4, 1.2, 0.8, np.nan],
            "revenue_rate_ratio": [0.7, 1.3, 0.6, np.nan],
        }
    )


def scenario(**overrides) -> RetentionScenario:
    values = {
        "horizon_days": 30,
        "campaign_budget_gbp": 10.0,
        "contact_cost_gbp": 3.25,
        "maximum_contacts": 5,
        "assumed_response_probability": 0.5,
        "assumed_purchase_uplift_if_responded": 0.2,
        "assumed_gross_margin_rate": 0.4,
    }
    values.update(overrides)
    return RetentionScenario(**values)


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"horizon_days": 45}, "horizon_days"),
        ({"campaign_budget_gbp": np.inf}, "campaign_budget_gbp"),
        ({"campaign_budget_gbp": -1}, "campaign_budget_gbp"),
        ({"campaign_budget_gbp": 1.001}, "two decimal"),
        ({"contact_cost_gbp": 0}, "must be positive"),
        ({"maximum_contacts": -1}, "maximum_contacts"),
        ({"maximum_contacts": True}, "maximum_contacts"),
        ({"assumed_response_probability": 1.1}, "assumed_response_probability"),
        ({"assumed_purchase_uplift_if_responded": -0.1}, "assumed_purchase_uplift"),
        ({"assumed_gross_margin_rate": 1.1}, "gross_margin"),
    ],
)
def test_scenario_rejects_invalid_assumptions(overrides, message) -> None:
    with pytest.raises(ValueError, match=message):
        scenario(**overrides)


def test_rankings_use_explicit_scores_and_stable_customer_id_ties() -> None:
    table = forecasts()
    table.loc[1, "historical_gross_spending_gbp"] = 500
    ranked = rank_retention_candidates(table, "historical_gross_spending")
    assert ranked["customer_id"].tolist() == [20, 10, 30, 40]
    assert ranked["priority_score_unit"].eq("GBP historical gross spending").all()

    risk = rank_retention_candidates(table, "nonreturn_probability")
    assert risk["customer_id"].tolist() == [30, 20, 10, 40]
    proxy = rank_retention_candidates(table, "nonreturn_spending_proxy")
    assert proxy["customer_id"].tolist()[:2] == [20, 30]


def test_pareto_ranking_is_deterministic_and_keeps_duplicate_fronts_equal() -> None:
    table = pd.DataFrame(
        {
            "customer_id": [3, 1, 2, 4],
            "purchase_probability": [0.1, 0.2, 0.2, 0.8],
            "conditional_expected_spending_gbp": [100, 100, 100, 50],
            "historical_gross_spending_gbp": [100, 100, 100, 100],
            "recency_days": [10, 10, 10, 10],
            "nonreturn_weighted_conditional_spending_proxy_gbp": [90, 80, 80, 10],
        }
    )
    first = rank_retention_candidates(table, "pareto_risk_value")
    second = rank_retention_candidates(table.sample(frac=1, random_state=7), "pareto_risk_value")
    assert first["customer_id"].tolist() == second["customer_id"].tolist()
    assert first.loc[first["customer_id"].isin([1, 2]), "pareto_front"].nunique() == 1
    assert first.iloc[0]["customer_id"] == 3
    assert first.iloc[0]["pareto_front"] == 1


def test_behavior_and_history_filters_are_explicit_not_numeric_weights() -> None:
    ranked = rank_retention_candidates(
        forecasts(),
        "nonreturn_spending_proxy",
        EligibilityPolicy(
            hist_segments=("Lapsed / At-Risk",),
            require_sufficient_behavior_history=True,
            behavior_filter="declining_purchase_rate",
        ),
    )
    assert ranked["customer_id"].tolist() == [30]
    assert ranked["selection_eligible"].all()
    assert "reliability_weight" not in ranked
    with pytest.raises(ValueError, match="purchase_rate_ratio"):
        rank_retention_candidates(
            forecasts().drop(columns="purchase_rate_ratio"),
            "nonreturn_probability",
            EligibilityPolicy(behavior_filter="declining_purchase_rate"),
        )


def test_invalid_rank_inputs_are_not_silently_dropped() -> None:
    invalid = forecasts()
    invalid.loc[0, "purchase_probability"] = np.nan
    with pytest.raises(ValueError, match="finite"):
        rank_retention_candidates(invalid, "nonreturn_probability")
    with pytest.raises(ValueError, match="strategy"):
        rank_retention_candidates(forecasts(), "arbitrary_score")


def test_equal_cost_budget_has_exact_pence_boundary_and_zero_budget_behavior() -> None:
    ranked = rank_retention_candidates(forecasts(), "nonreturn_spending_proxy")
    selected = allocate_contact_budget(
        ranked, campaign_budget_gbp=9.75, contact_costs=3.25, maximum_contacts=9
    )
    assert len(selected) == 3
    assert selected["contact_cost_gbp"].sum() == pytest.approx(9.75)
    assert selected["cumulative_contact_cost_gbp"].iloc[-1] == pytest.approx(9.75)
    assert selected["allocation_method"].eq(
        "deterministic_greedy_by_screening_rank"
    ).all()
    empty = allocate_contact_budget(
        ranked, campaign_budget_gbp=0, contact_costs=3.25, maximum_contacts=9
    )
    assert empty.empty
    assert allocate_contact_budget(
        ranked, campaign_budget_gbp=100, contact_costs=3.25, maximum_contacts=0
    ).empty
    assert len(
        allocate_contact_budget(
            ranked, campaign_budget_gbp=100, contact_costs=3.25, maximum_contacts=2
        )
    ) == 2


def test_invalid_contact_costs_and_alignment_fail() -> None:
    ranked = rank_retention_candidates(forecasts(), "nonreturn_probability")
    with pytest.raises(ValueError, match="positive"):
        allocate_contact_budget(ranked, 10, 0, 2)
    with pytest.raises(ValueError, match="two decimal"):
        allocate_contact_budget(ranked, 10, 1.005, 2)
    with pytest.raises(ValueError, match="align"):
        allocate_contact_budget(
            ranked, 10, pd.Series([2.0, 2.0]), 2
        )


def test_variable_costs_use_documented_greedy_benefit_per_cost() -> None:
    candidates = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "hypothetical_incremental_revenue_gbp": [12.0, 10.0, 5.0],
            "contact_cost_gbp": [6.0, 2.0, 1.0],
        }
    )
    selected = allocate_contact_budget(
        candidates,
        campaign_budget_gbp=3,
        contact_costs="contact_cost_gbp",
        maximum_contacts=2,
        allocation_objective="hypothetical_benefit_per_cost",
    )
    assert selected["customer_id"].tolist() == [2, 3]
    assert selected["contact_cost_gbp"].sum() == pytest.approx(3)
    assert selected["selection_is_globally_optimal"].eq(False).all()
    with pytest.raises(ValueError, match="hypothetical_benefit_per_cost"):
        allocate_contact_budget(
            candidates,
            campaign_budget_gbp=3,
            contact_costs="contact_cost_gbp",
            maximum_contacts=2,
        )


def test_scenario_equations_cap_at_remaining_purchase_probability() -> None:
    customer = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "purchase_probability": [0.9, 0.2],
            "conditional_expected_spending_gbp": [100, 200],
        }
    )
    output = simulate_retention_scenario(
        customer,
        scenario(campaign_budget_gbp=10, contact_cost_gbp=2, maximum_contacts=2),
    )
    # Customer 1 is capped at 1 - p = .1, customer 2 receives .5 * .2 = .1.
    assert output["hypothetical_incremental_revenue_gbp"] == pytest.approx(30)
    assert output["campaign_cost_gbp"] == 4
    assert output["hypothetical_incremental_contribution_gbp"] == pytest.approx(8)
    assert output["break_even_information"]["status"] == "break_even_reached"
    assert output["break_even_information"][
        "minimum_response_probability_for_break_even"
    ] <= 0.5
    assert output["causal_estimate"] is False
    assert "hypothetical assumptions" in output["limitations"][0]
    assert "No randomized intervention data" in output["limitations"][1]


def test_scenario_cost_and_contact_limits_are_enforced() -> None:
    selected = forecasts().iloc[:2].copy()
    selected["purchase_probability"] = [0.2, 0.3]
    selected["conditional_expected_spending_gbp"] = [100, 100]
    with pytest.raises(ValueError, match="maximum_contacts"):
        simulate_retention_scenario(
            selected,
            scenario(maximum_contacts=1),
        )
    with pytest.raises(ValueError, match="budget"):
        simulate_retention_scenario(
            selected,
            scenario(campaign_budget_gbp=1, contact_cost_gbp=1),
        )


def test_repeated_scenarios_are_deterministic_and_uplift_is_monotone() -> None:
    ranked = rank_retention_candidates(forecasts(), "nonreturn_probability")
    chosen = allocate_contact_budget(ranked, 10, 2, 2)
    low = simulate_retention_scenario(
        chosen, scenario(campaign_budget_gbp=10, contact_cost_gbp=2, maximum_contacts=2, assumed_purchase_uplift_if_responded=0.1)
    )
    repeated = simulate_retention_scenario(
        chosen, scenario(campaign_budget_gbp=10, contact_cost_gbp=2, maximum_contacts=2, assumed_purchase_uplift_if_responded=0.1)
    )
    high = simulate_retention_scenario(
        chosen, scenario(campaign_budget_gbp=10, contact_cost_gbp=2, maximum_contacts=2, assumed_purchase_uplift_if_responded=0.2)
    )
    assert low == repeated
    assert high["hypothetical_incremental_revenue_gbp"] >= low["hypothetical_incremental_revenue_gbp"]


def test_break_even_is_explicitly_unavailable_without_margin() -> None:
    table = pd.DataFrame(
        {
            "customer_id": [1, 2],
            "purchase_probability": [0.8, 0.99],
            "conditional_expected_spending_gbp": [100.0, 100.0],
        }
    )
    no_margin = calculate_break_even_conditions(table, 5, None)
    assert no_margin["status"].eq("not_estimable_without_margin").all()
    assert no_margin["required_purchase_probability_increment"].isna().all()


def test_break_even_uses_supplied_margin_and_response_scenario() -> None:
    table = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "purchase_probability": [0.8, 0.99, 0.5],
            "conditional_expected_spending_gbp": [100.0, 100.0, 0.0],
        }
    )
    result = calculate_break_even_conditions(
        table,
        5,
        0.5,
        assumed_response_probability=0.5,
    )
    assert result.loc[0, "required_purchase_probability_increment"] == pytest.approx(0.1)
    assert result.loc[0, "required_purchase_uplift_if_responded"] == pytest.approx(0.2)
    assert bool(result.loc[0, "break_even_feasible_under_supplied_assumptions"])
    assert not bool(result.loc[1, "break_even_feasible_under_supplied_assumptions"])
    assert not bool(result.loc[2, "break_even_feasible_under_supplied_assumptions"])


def test_strategy_comparison_keeps_scenario_results_hypothetical() -> None:
    compared = compare_retention_strategies(
        forecasts(),
        [scenario()],
        strategies=("historical_gross_spending", "nonreturn_spending_proxy"),
    )
    assert len(compared) == 2
    assert compared["causal_estimate"].eq(False).all()
    assert compared["selected_customer_count"].le(3).all()
    assert compared["campaign_cost_gbp"].le(10).all()
