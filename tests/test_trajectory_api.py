from __future__ import annotations

from fastapi.testclient import TestClient

from api import trajectory_service
from api.main import app

client = TestClient(app)


def test_trajectory_api_contract_and_historical_summary() -> None:
    trajectory_service._get_trajectory_bundle.cache_clear()

    paths = app.openapi()["paths"]
    assert "/api/trajectories/summary" in paths
    assert "/api/trajectories/clusters" in paths
    assert "/api/trajectories/customers" in paths
    assert "/api/trajectories/evaluation" in paths
    assert "/api/customers/{customer_id}/trajectory" in paths
    assert "/api/customers/{customer_id}/trajectory/explanation" in paths

    summary = client.get("/api/trajectories/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["cutoff_date"] == "2010-09-10"
    assert body["total_customers"] == 3373
    assert sum(body["history_sufficiency_counts"].values()) == 3373
    assert (
        body["clustered_customer_count"] + body["unassigned_customer_count"]
        == body["total_customers"]
    )
    assert body["clustered_customer_count"] > 0
    assert body["unassigned_customer_count"] + body["clustered_customer_count"] == 3373
    assert "train_fitted_curve_shape_clustering" in (
        body["available_trajectory_methods"]
    )
    assert "train_fitted_grid_based_functional_pca" in (
        body["available_trajectory_methods"]
    )
    assert "curve_shape_clustering" in body["selected_representation"]
    assert "exposure_adjusted_30_day_rolling_trajectories" in (
        body["available_trajectory_methods"]
    )


def test_trajectory_customer_listing_filters_and_detail_are_validated() -> None:
    trajectory_service._get_trajectory_bundle.cache_clear()
    page = client.get("/api/trajectories/customers", params={"page_size": 5})
    assert page.status_code == 200
    payload = page.json()
    assert payload["total"] == 3373
    assert len(payload["items"]) == 5

    first = payload["items"][0]
    customer_id = first["customer_id"]
    filtered = client.get(
        "/api/trajectories/customers",
        params={
            "search": str(customer_id),
            "history_sufficiency": first["history_sufficiency"],
        },
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["customer_id"] == customer_id

    clusters = client.get("/api/trajectories/clusters").json()["clusters"]
    assert clusters
    selected_cluster = clusters[0]["cluster_id"]
    cluster_page = client.get(
        "/api/trajectories/customers",
        params={"cluster_id": selected_cluster, "page_size": 5},
    )
    assert cluster_page.status_code == 200
    assert cluster_page.json()["total"] == clusters[0]["customer_count"]
    assert all(
        item["trajectory_cluster_id"] == selected_cluster
        for item in cluster_page.json()["items"]
    )

    detail = client.get(f"/api/customers/{customer_id}/trajectory")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["cutoff_date"] == "2010-09-10"
    assert detail_body["purchase_rate_trajectory"]
    assert detail_body["trajectory_cluster_id"] is None or isinstance(
        detail_body["trajectory_cluster_id"], int
    )
    assert set(detail_body["functional_component_scores"]) <= {
        "functional_component_1",
        "functional_component_2",
        "functional_component_3",
    }
    assert "future_purchase" not in str(detail_body).lower()

    explanation = client.get(
        f"/api/customers/{customer_id}/trajectory/explanation"
    )
    assert explanation.status_code == 200
    assert explanation.json()["supported_features"]["active_purchase_windows"] >= 0


def test_cluster_and_evaluation_endpoints_expose_saved_methods() -> None:
    trajectory_service._get_trajectory_bundle.cache_clear()
    clusters = client.get("/api/trajectories/clusters")
    evaluation = client.get("/api/trajectories/evaluation")

    assert clusters.status_code == 200
    assert clusters.json()["available"] is True
    assert clusters.json()["clusters"]
    assert sum(item["customer_count"] for item in clusters.json()["clusters"]) == (
        client.get("/api/trajectories/summary").json()["clustered_customer_count"]
    )
    assert evaluation.status_code == 200
    assert evaluation.json()["status"] == "completed_with_method_specific_availability"
    functional = evaluation.json()["results"]["functional_analysis"]
    assert functional["status"] == "grid_based_pca_fitted_on_train"
    assert len(functional["test_score_points"]) == functional["test_evaluation"]["evaluated_curves"]
    assert functional["test_evaluation"]["component_count"] == 3


def test_trajectory_api_rejects_invalid_filters_and_unknown_customers() -> None:
    trajectory_service._get_trajectory_bundle.cache_clear()
    assert (
        client.get(
            "/api/trajectories/customers",
            params={"history_sufficiency": "unobserved"},
        ).status_code
        == 422
    )
    assert (
        client.get(
            "/api/trajectories/customers",
            params={"page_size": 1000},
        ).status_code
        == 422
    )
    assert client.get("/api/customers/999999999/trajectory").status_code == 404
