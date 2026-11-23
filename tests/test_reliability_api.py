from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_aggregate_reliability_endpoints_return_historical_evidence():
    summary = client.get("/api/reliability/summary")
    calibration = client.get("/api/reliability/calibration")
    subgroups = client.get("/api/reliability/subgroups?horizon_days=30")
    revenue = client.get("/api/reliability/revenue")

    assert summary.status_code == 200
    assert summary.json()["test_customer_count"] == 3373
    assert calibration.status_code == 200
    assert len(calibration.json()["horizons"]) == 3
    assert subgroups.status_code == 200
    assert all(item["horizon_days"] == 30 for item in subgroups.json()["items"])
    assert revenue.status_code == 200
    assert len(revenue.json()["metrics"]) == 9

    payload = summary.json()
    assert "observed_outcome" not in payload
    assert "customer_id" not in payload
    assert "FutureRevenue_30d" not in str(payload)


def test_customer_explanation_and_reliability_use_saved_forecast_only():
    customer_id = 12346
    forecast = client.get(f"/api/customers/{customer_id}/forecast")
    explanation = client.get(
        f"/api/customers/{customer_id}/explanation?horizon_days=30"
    )
    reliability = client.get(
        f"/api/customers/{customer_id}/reliability?horizon_days=30"
    )

    assert forecast.status_code == 200
    assert explanation.status_code == 200
    assert reliability.status_code == 200
    explained = explanation.json()
    assert explained["customer_id"] == customer_id
    assert explained["horizon_days"] == 30
    assert explained["purchase_probability"] == forecast.json()["purchase_probability_30d"]
    assert explained["personalized_expected_revenue"] == (
        forecast.json()["personalized_expected_revenue_30d"]
    )
    assert explained["conditional_expected_spending"] >= 0
    assert 0 <= explained["reference_probability"] <= 1
    assert "not causal" in " ".join(explained["model_input_limitations"]).lower()
    assert "observed_outcome" not in explained
    assert "actual_purchase" not in str(explained).lower()

    reliability_data = reliability.json()
    assert reliability_data["customer_id"] == customer_id
    assert reliability_data["evaluation_group_count"] >= 100
    assert reliability_data["reliability_status"] in {
        "well_supported_historical_evaluation_group",
        "insufficient_evaluation_support",
        "single_outcome_class",
    }
    assert reliability_data["distribution_support_flags"]
    assert "individual" in " ".join(reliability_data["limitations"]).lower()


def test_customer_endpoints_validate_unknown_ids_and_horizons():
    unknown = client.get("/api/customers/999999999/explanation")
    invalid_explanation = client.get(
        "/api/customers/12346/explanation?horizon_days=45"
    )
    invalid_reliability = client.get(
        "/api/customers/12346/reliability?horizon_days=45"
    )
    invalid_subgroups = client.get("/api/reliability/subgroups?horizon_days=45")

    assert unknown.status_code == 404
    assert invalid_explanation.status_code == 422
    assert invalid_reliability.status_code == 422
    assert invalid_subgroups.status_code == 422


def test_missing_reliability_artifact_returns_service_unavailable(monkeypatch):
    from api import service

    def missing_artifact():
        raise FileNotFoundError("missing evaluation artifact")

    monkeypatch.setattr(service, "get_reliability_artifact", missing_artifact)
    response = client.get("/api/reliability/summary")
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_reliability_openapi_contract_has_six_routes_and_bounded_horizons():
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    expected = {
        "/api/reliability/summary",
        "/api/reliability/calibration",
        "/api/reliability/subgroups",
        "/api/reliability/revenue",
        "/api/customers/{customer_id}/explanation",
        "/api/customers/{customer_id}/reliability",
    }
    assert expected.issubset(paths)
    horizon_parameter = next(
        parameter
        for parameter in paths["/api/customers/{customer_id}/explanation"]["get"][
            "parameters"
        ]
        if parameter["name"] == "horizon_days"
    )
    horizon_schema = horizon_parameter["schema"]
    if "$ref" in horizon_schema:
        schema_name = horizon_schema["$ref"].rsplit("/", 1)[-1]
        horizon_schema = openapi["components"]["schemas"][schema_name]
    assert horizon_schema["enum"] == [30, 60, 90]


def test_existing_model_performance_endpoint_remains_unchanged():
    response = client.get("/api/model-performance")
    assert response.status_code == 200
    assert response.json()["test_customers"] == 3373
