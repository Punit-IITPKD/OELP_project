from __future__ import annotations

from datetime import date
import math

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def _get(path: str, **params):
    response = client.get(path, params=params)
    assert response.status_code == 200, response.text
    return response.json()


def test_representative_saved_customers_stay_consistent_across_modules() -> None:
    examples = {
        12918: {"frequency": 1, "history_group": "Exactly one purchase", "hist_segment": "Lapsed / At-Risk"},
        18102: {"frequency": 78, "history_group": "Five or more purchases", "hist_segment": "Recent / Active"},
        12346: {"history_sufficiency": "limited_history", "functional_eligible": False},
        12417: {"history_sufficiency": "sufficient_for_functional_analysis", "functional_eligible": True},
    }

    for customer_id, expected in examples.items():
        profile = _get(f"/api/customers/{customer_id}")
        assert profile["customer_id"] == customer_id
        assert profile["cutoff_date"] == "2010-09-10"
        for field, value in expected.items():
            if field in {"history_sufficiency", "functional_eligible"}:
                continue
            assert profile[field] == value

        purchases = _get(f"/api/customers/{customer_id}/history")
        assert purchases
        assert all(
            date.fromisoformat(row["purchase_date"][:10])
            < date.fromisoformat(profile["cutoff_date"])
            for row in purchases
        )

        forecast = _get(f"/api/customers/{customer_id}/forecast")
        assert forecast["customer_id"] == customer_id
        assert forecast["cutoff_date"] == profile["cutoff_date"]
        assert forecast["purchase_probability_30d"] == profile["purchase_probability_30d"]
        assert forecast["personalized_expected_revenue_30d"] == profile["personalized_expected_revenue_30d"]

        explanation = _get(f"/api/customers/{customer_id}/explanation", horizon_days=30)
        assert explanation["customer_id"] == customer_id
        assert explanation["cutoff_date"] == profile["cutoff_date"]
        assert explanation["purchase_probability"] == profile["purchase_probability_30d"]

        reliability = _get(f"/api/customers/{customer_id}/reliability", horizon_days=30)
        assert reliability["customer_id"] == customer_id
        assert reliability["cutoff_date"] == profile["cutoff_date"]
        assert reliability["history_group"] == profile["history_group"]

        behavior = _get(f"/api/customers/{customer_id}/behavior")
        behavior_trajectory = _get(f"/api/customers/{customer_id}/behavior/trajectory")
        assert behavior["customer_id"] == behavior_trajectory["customer_id"] == customer_id
        assert behavior["cutoff_date"] == behavior_trajectory["cutoff_date"] == profile["cutoff_date"]

        revenue = _get(f"/api/customers/{customer_id}/revenue-exposure", horizon_days=30)
        assert revenue["customer_id"] == customer_id
        assert revenue["cutoff_date"] == profile["cutoff_date"]
        assert revenue["currency_code"] == "GBP"
        assert revenue["estimated_revenue_exposure_gbp"] is None
        assert math.isclose(
            revenue["personalized_expected_revenue_gbp"],
            revenue["purchase_probability"] * revenue["conditional_expected_spending_gbp"],
            rel_tol=1e-9,
            abs_tol=1e-7,
        )
        assert math.isclose(
            revenue["nonreturn_weighted_conditional_spending_proxy_gbp"],
            revenue["nonreturn_probability"] * revenue["conditional_expected_spending_gbp"],
            rel_tol=1e-6,
            abs_tol=1e-6,
        )

        trajectory = _get(f"/api/customers/{customer_id}/trajectory")
        assert trajectory["customer_id"] == customer_id
        assert trajectory["cutoff_date"] == profile["cutoff_date"]
        if "history_sufficiency" in expected:
            assert trajectory["history_sufficiency"] == expected["history_sufficiency"]
            assert trajectory["functional_eligible"] is expected["functional_eligible"]
        if customer_id == 12918:
            assert trajectory["trajectory_cluster_id"] is None
            assert all(
                value is None
                for value in trajectory["functional_component_scores"].values()
            )
        if customer_id == 12417:
            assert trajectory["shape_cluster_eligible"] is True
            assert trajectory["trajectory_cluster_id"] is not None
            assert trajectory["functional_eligible"] is True
            assert trajectory["functional_component_scores"]

        trajectory_explanation = _get(f"/api/customers/{customer_id}/trajectory/explanation")
        assert trajectory_explanation["customer_id"] == customer_id
        assert trajectory_explanation["cutoff_date"] == profile["cutoff_date"]


def test_hypothetical_retention_scenario_stays_noncausal() -> None:
    response = client.post(
        "/api/retention/scenarios",
        json={
            "horizon_days": 30,
            "campaign_budget_gbp": 100,
            "contact_cost_gbp": 1,
            "maximum_contacts": 100,
            "assumed_response_probability": 0.2,
            "assumed_purchase_uplift_if_responded": 0.1,
            "ranking_strategy": "historical_gross_spending",
        },
    )
    assert response.status_code == 200, response.text
    scenario = response.json()
    assert scenario["causal_estimate"] is False
    assert any("hypothetical" in item.lower() for item in scenario["limitations"])
