from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from api import service
from api.main import app
from app.config import METRICS_DIR

client = TestClient(app)


def test_behavior_routes_are_in_the_generated_api_contract() -> None:
    paths = app.openapi()["paths"]
    assert "/api/behavior/summary" in paths
    assert "/api/behavior/customers" in paths
    assert "/api/behavior/evaluation" in paths
    assert "/api/customers/{customer_id}/behavior" in paths
    assert "/api/customers/{customer_id}/behavior/trajectory" in paths


def test_behavior_summary_customers_detail_and_trajectory_are_cutoff_safe() -> None:
    service._get_behavior_analytics.cache_clear()
    service._get_behavior_config.cache_clear()

    summary_response = client.get("/api/behavior/summary")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["cutoff_date"] == "2010-09-10"
    assert summary["eligible_customers"] == 3373
    assert summary["alert_policy_available"] is False
    assert sum(item["customers"] for item in summary["history_sufficiency"]) == 3373
    assert {item["field"] for item in summary["distributions"]} >= {
        "gap_deviation_score",
        "purchase_rate_ratio",
        "revenue_rate_ratio",
        "ewma_gap_change_days",
    }

    page_response = client.get(
        "/api/behavior/customers",
        params={
            "page": 1,
            "page_size": 5,
            "sort_by": "current_elapsed_gap_days",
            "sort_direction": "desc",
        },
    )
    assert page_response.status_code == 200
    page = page_response.json()
    assert page["total"] == 3373
    assert page["page_size"] == 5
    assert len(page["items"]) == 5
    first = page["items"][0]
    assert first["policy_version"] == "behavior-continuous-v1"
    assert first["cutoff_date"] == "2010-09-10"
    assert first["available_indicator_count"] >= 0

    filtered_response = client.get(
        "/api/behavior/customers",
        params={
            "search": str(first["customer_id"]),
            "history_sufficiency": first["history_sufficiency"],
        },
    )
    assert filtered_response.status_code == 200
    filtered = filtered_response.json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["customer_id"] == first["customer_id"]

    detail_response = client.get(f"/api/customers/{first['customer_id']}/behavior")
    trajectory_response = client.get(
        f"/api/customers/{first['customer_id']}/behavior/trajectory"
    )
    assert detail_response.status_code == 200
    assert trajectory_response.status_code == 200
    detail = detail_response.json()
    trajectory = trajectory_response.json()
    assert detail["alert_reasons"] == []
    assert detail["indicator_explanations"]
    assert trajectory["cutoff_date"] == "2010-09-10"
    assert trajectory["items"]
    assert all(
        pd.Timestamp(item["period_end"]) <= pd.Timestamp("2010-09-10")
        for item in trajectory["items"]
    )

    assert client.get("/api/customers/999999999/behavior").status_code == 404
    assert (
        client.get(
            "/api/customers/999999999/behavior/trajectory"
        ).status_code
        == 404
    )
    assert (
        client.get(
            "/api/behavior/customers", params={"sort_by": "unknown"}
        ).status_code
        == 422
    )
    assert (
        client.get(
            "/api/behavior/customers",
            params={"history_sufficiency": "unsupported"},
        ).status_code
        == 422
    )


def test_behavior_evaluation_api_matches_saved_versioned_results() -> None:
    response = client.get("/api/behavior/evaluation")
    assert response.status_code == 200
    actual = response.json()
    saved = json.loads(
        (METRICS_DIR / "behavior_monitor_evaluation.json").read_text(
            encoding="utf-8"
        )
    )
    assert actual["evaluation_version"] == saved["evaluation_version"]
    assert actual["test_cutoff_date"] == "2010-09-10"
    assert actual["candidate_f_status"].startswith("not_fitted:")
    assert len(actual["selection_results"]) == 3
    assert actual["model_comparison"] == saved["model_comparison"]
    assert actual["bootstrap_comparisons"] == saved["bootstrap_comparisons"]
    assert actual["subgroup_results"] == saved["subgroup_results"]
    assert actual["hypotheses"] == saved["hypotheses"]


def test_behavior_metadata_is_required_and_versioned() -> None:
    metadata_path = Path("models/behavior_monitor/metadata.json")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["feature_version"] == "behavior-monitor-v1"
    assert metadata["policy_version"] == "behavior-continuous-v1"
    assert metadata["alert_policy_available"] is False
    assert metadata["test_outcomes_used_for_selection_or_training"] is False
    assert metadata["config"]["ewma_lambda"] == metadata[
        "serving_ewma_lambda_selected_on_validation"
    ]
