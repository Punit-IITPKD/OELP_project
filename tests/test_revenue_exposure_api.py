from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_revenue_exposure_summary_preserves_null_reference_and_models() -> None:
    response = client.get("/api/revenue-exposure/summary?horizon_days=30")

    assert response.status_code == 200
    payload = response.json()
    assert payload["eligible_customers"] == 3373
    assert payload["currency_code"] == "GBP"
    assert payload["estimated_revenue_exposure_total_gbp"] is None
    assert payload["exposure_status"] == "not_estimable"
    assert payload["personalized_expected_revenue_total_gbp"] > 0
    assert payload["forecast_disagreement"]


def test_customer_page_scatter_and_concentration_return_real_cohort() -> None:
    customers = client.get(
        "/api/revenue-exposure/customers",
        params={
            "horizon_days": 30,
            "page": 1,
            "page_size": 8,
            "ranking_strategy": "nonreturn_spending_proxy",
        },
    )
    assert customers.status_code == 200
    page = customers.json()
    assert page["total"] == 3373
    assert len(page["items"]) == 8
    assert page["items"][0]["priority_rank"] == 1
    assert page["items"][0]["exposure_status"] == "not_estimable"
    assert page["items"][0]["selection_eligible"] is True

    scatter = client.get(
        "/api/revenue-exposure/scatter",
        params={"horizon_days": 30, "limit": 12},
    )
    assert scatter.status_code == 200
    assert len(scatter.json()["points"]) == 12
    assert scatter.json()["eligible_customers"] == 3373
    assert scatter.json()["returned_points"] == 12
    assert scatter.json()["x_axis"] == "nonreturn_probability"
    assert scatter.json()["y_axis"] == "conditional_expected_spending_gbp"
    assert all("reliability_status" in row for row in scatter.json()["points"])

    filtered_scatter = client.get(
        "/api/revenue-exposure/scatter",
        params={
            "horizon_days": 30,
            "limit": 12,
            "history_sufficiency": "sufficient",
        },
    )
    assert filtered_scatter.status_code == 200
    assert filtered_scatter.json()["eligible_customers"] == 725
    assert filtered_scatter.json()["returned_points"] == 12
    assert len(filtered_scatter.json()["points"]) == 12
    assert all(
        row["history_sufficiency"] == "sufficient"
        for row in filtered_scatter.json()["points"]
    )

    concentration = client.get(
        "/api/revenue-exposure/concentration?horizon_days=30"
    )
    assert concentration.status_code == 200
    assert len(concentration.json()["items"]) == 15


def test_behavior_and_segment_filters_are_supported_and_validated() -> None:
    filtered = client.get(
        "/api/revenue-exposure/customers",
        params={
            "horizon_days": 60,
            "page_size": 5,
            "history_sufficiency": "sufficient",
            "behavior_filter": "declining_purchase_rate",
        },
    )
    assert filtered.status_code == 200
    assert all(
        item["history_sufficiency"] == "sufficient"
        for item in filtered.json()["items"]
    )

    searched = client.get(
        "/api/revenue-exposure/customers",
        params={"search": "12346", "sort_by": "customer_id"},
    )
    assert searched.status_code == 200
    assert searched.json()["total"] == 1
    assert searched.json()["items"][0]["customer_id"] == 12346

    invalid = client.get(
        "/api/revenue-exposure/customers",
        params={"ranking_strategy": "causal_uplift"},
    )
    assert invalid.status_code == 400


def test_customer_detail_has_limitations_and_unknown_customer_is_404() -> None:
    response = client.get("/api/customers/12346/revenue-exposure?horizon_days=30")
    assert response.status_code == 200
    customer = response.json()
    assert customer["customer_id"] == 12346
    assert customer["estimated_revenue_exposure_gbp"] is None
    assert customer["reliability_is_individual_guarantee"] is False
    assert customer["selection_eligible"] is None
    assert len(customer["limitations"]) >= 3

    missing = client.get("/api/customers/99999999/revenue-exposure")
    assert missing.status_code == 404


def test_aggregate_evaluation_has_no_per_customer_test_outcomes() -> None:
    response = client.get("/api/revenue-exposure/evaluation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["hypotheses"]["H6_predictive_ranking"]["status"] == (
        "not_supported_on_locked_test"
    )
    assert payload["metadata"]["test_outcomes_used_for_selection"] is False
    assert "selected_customer_ids" not in response.text
    assert "ranking_method_comparisons" in payload


def test_scenario_and_strategy_comparison_are_explicitly_noncausal() -> None:
    scenario = {
        "horizon_days": 30,
        "campaign_budget_gbp": 100.0,
        "contact_cost_gbp": 2.0,
        "maximum_contacts": 50,
        "assumed_response_probability": 0.1,
        "assumed_purchase_uplift_if_responded": 0.05,
        "assumed_gross_margin_rate": None,
        "ranking_strategy": "nonreturn_spending_proxy",
        "eligibility_filters": {},
    }
    response = client.post("/api/retention/scenarios", json=scenario)

    assert response.status_code == 200
    result = response.json()
    assert result["causal_estimate"] is False
    assert result["is_causal_estimate"] is False
    assert result["break_even_information"]["status"] == "margin_not_supplied"
    assert result["selected_customer_count"] <= 50
    assert result["campaign_cost_gbp"] <= 100
    assert result["hypothetical_incremental_contribution_gbp"] is None
    assert len(result["selected_customers"]) == result["selected_customer_count"]

    comparison = client.post(
        "/api/retention/compare-strategies",
        json={
            "scenario": {
                key: value
                for key, value in scenario.items()
                if key not in {"ranking_strategy", "eligibility_filters"}
            },
            "ranking_strategies": [
                "historical_gross_spending",
                "nonreturn_spending_proxy",
            ],
            "eligibility_filters": {},
        },
    )
    assert comparison.status_code == 200
    items = comparison.json()["strategy_results"]
    assert len(items) == 2
    assert all(item["causal_estimate"] is False for item in items)
    assert all("break_even_information" in item for item in items)
    assert all(
        item["selected_customer_count"] <= 50
        for item in items
    )


def test_invalid_campaign_probability_is_rejected() -> None:
    response = client.post(
        "/api/retention/scenarios",
        json={
            "horizon_days": 30,
            "campaign_budget_gbp": 10,
            "contact_cost_gbp": 1,
            "maximum_contacts": 2,
            "assumed_response_probability": 1.2,
            "assumed_purchase_uplift_if_responded": 0.1,
            "ranking_strategy": "nonreturn_probability",
        },
    )
    assert response.status_code == 422
