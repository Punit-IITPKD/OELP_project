from __future__ import annotations

import json

from fastapi.testclient import TestClient

from api import research_service
from api.main import app
from app.config import METRICS_DIR
from src.final_evaluation import (
    ARTIFACT_VERSION,
    OUTPUT_PATH,
    build_final_evaluation,
    encode_final_evaluation,
)

client = TestClient(app)


def test_final_evaluation_is_deterministic_and_covers_all_notebooks() -> None:
    expected = encode_final_evaluation(build_final_evaluation())
    assert OUTPUT_PATH.read_bytes() == expected

    payload = json.loads(expected)
    assert payload["artifact_version"] == ARTIFACT_VERSION
    assert len(payload["notebook_registry"]) == 11
    assert [row["notebook_id"] for row in payload["notebook_registry"]] == [
        f"{index:02}" for index in range(1, 12)
    ]
    assert payload["research_scope"]["test_customer_count"] == 3373
    assert all(row["major_findings"] for row in payload["notebook_registry"])
    assert all(row["reproducibility_command"] for row in payload["notebook_registry"])
    assert all(row["dataset"] and row["evaluation_population"] for row in payload["notebook_registry"])
    assert {
        reference["path"] for reference in payload["source_manifest"]
    } >= {
        f"notebooks/{name}"
        for name in (
            "01_EDA_analysis.ipynb",
            "02_Customer_feature_engineering.ipynb",
            "03_Interpurchase_Distribution_Analysis.ipynb",
            "04_KMeans_Customer_Segmentation.ipynb",
            "05_Statistical_Validation_and_Temporal_Framework.ipynb",
            "06_Personalized_Purchase_Clock.ipynb",
            "07_Future_Spending_and_Revenue_Forecasting.ipynb",
            "08_Behavioral_Change_Detection.ipynb",
            "09_Prediction_Reliability_and_Explainability.ipynb",
            "10_Revenue_at_Risk_and_Retention_Planning.ipynb",
            "11_Customer_Retention_Trajectory_Analysis.ipynb",
        )
    }
    assert payload["hypothesis_status_counts"] == {
        "descriptive_only": 5,
        "inconclusive": 2,
        "not_evaluable": 1,
        "not_supported": 1,
        "supported": 2,
    }
    behavior_hypothesis = next(
        item for item in payload["research_hypotheses"] if item["id"] == "08-H1"
    )
    assert behavior_hypothesis["evaluation_horizons_days"] == [30, 60, 90]
    assert behavior_hypothesis["uncertainty_intervals"][0]["level"] == 0.95
    assert behavior_hypothesis["uncertainty_intervals"][0]["horizon_days"] == 30


def test_final_evaluation_preserves_financial_null_and_no_customer_rows() -> None:
    payload = build_final_evaluation()
    definitions = payload["financial_definitions"]
    assert definitions["reference_exposure_status"] == "not_estimable"
    assert definitions["reference_exposure_total_gbp"] is None
    assert definitions["causal_effect"] is None
    assert definitions["campaign_scenario_inputs"]["scenario_inputs_are_hypothetical"]

    serialized = json.dumps(payload).lower()
    assert '"customer_id"' not in serialized
    assert '"customer_ids"' not in serialized
    assert "futureorders_" not in serialized
    assert "purchased_30d" not in serialized


def test_research_summary_endpoint_returns_typed_aggregate_evidence() -> None:
    response = client.get("/api/research/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["artifact_version"] == ARTIFACT_VERSION
    assert len(payload["notebook_registry"]) == 11
    assert payload["financial_definitions"]["reference_exposure_total_gbp"] is None
    assert len(payload["source_manifest"]) > 0
    serialized = json.dumps(payload).lower()
    assert '"customer_id"' not in serialized
    assert "futureorders_" not in serialized


def test_research_summary_fails_explicitly_when_artifact_is_unavailable(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(research_service, "_SUMMARY_PATH", tmp_path / "missing.json")
    research_service._load_summary.cache_clear()
    try:
        response = client.get("/api/research/summary")
        assert response.status_code == 503
    finally:
        research_service._load_summary.cache_clear()
