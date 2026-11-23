from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from api import service
from api.main import app
from app.config import METRICS_DIR, PREDICTION_CUTOFF

client = TestClient(app)

SAMPLE_UPLOAD = """Order ref,Stock code,Product,Count,Bought at,Unit price,Client,Location
90001,SKU-1,Widget,2,2010-01-01 09:00:00,5.00,901001,United Kingdom
90002,SKU-2,Gadget,1,2010-01-20 12:00:00,7.00,901001,United Kingdom
90003,SKU-3,Book,1,2010-02-01 10:00:00,8.00,901002,United Kingdom
90003,SKU-3,Book,1,2010-02-01 10:00:00,8.00,901002,United Kingdom
C90004,SKU-4,Return,-1,2010-02-05 10:00:00,8.00,901002,United Kingdom
"""
SAMPLE_MAPPING = {
    "Invoice": "Order ref",
    "StockCode": "Stock code",
    "Description": "Product",
    "Quantity": "Count",
    "InvoiceDate": "Bought at",
    "Price": "Unit price",
    "Customer ID": "Client",
    "Country": "Location",
}


def test_health_endpoints_do_not_load_model_artifacts() -> None:
    service.get_analytics.cache_clear()

    health = client.get("/api/health")
    healthz = client.get("/api/healthz")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert healthz.status_code == 200
    assert service.get_analytics.cache_info().currsize == 0


def test_fastapi_paths_cover_the_generated_contract() -> None:
    api_paths = app.openapi()["paths"]
    required = {
        "/api/health": {"get"},
        "/api/healthz": {"get"},
        "/api/overview": {"get"},
        "/api/segments": {"get"},
        "/api/customers": {"get"},
        "/api/customers/{customer_id}": {"get"},
        "/api/customers/{customer_id}/history": {"get"},
        "/api/customers/{customer_id}/forecast": {"get"},
        "/api/forecasts/summary": {"get"},
        "/api/model-performance": {"get"},
        "/api/model-performance/calibration": {"get"},
        "/api/model-performance/calibration-90d": {"get"},
        "/api/model-performance/assets/{filename}": {"get"},
        "/api/upload/preview": {"post"},
        "/api/upload/analyze": {"post"},
        "/api/upload/export": {"post"},
    }
    for path, methods in required.items():
        assert path in api_paths
        assert methods.issubset(api_paths[path])


def test_real_overview_and_segment_responses_use_saved_data() -> None:
    overview = client.get("/api/overview")
    segments = client.get("/api/segments")

    assert overview.status_code == 200
    assert segments.status_code == 200
    overview_data = overview.json()
    segment_data = segments.json()
    assert overview_data["period"]["start_date"]
    assert overview_data["historical"]["orders"] > 0
    assert overview_data["historical"]["revenue"] > 0
    assert overview_data["forecast"]["cutoff_date"] == PREDICTION_CUTOFF
    assert overview_data["forecast"]["eligible_customers"] == 3373
    assert sum(item["customers"] for item in segment_data["historical_segments"]) == 3373
    assert {item["segment"] for item in segment_data["descriptive_segments"]}
    assert all(
        "segment" in item and "customers" in item
        for item in segment_data["historical_segments"]
    )


def test_customer_forecast_matches_cached_snapshot_and_is_cutoff_safe() -> None:
    bundle = service.get_analytics()
    source = bundle.snapshot.iloc[0]
    customer_id = int(source["Customer ID"])

    profile_response = client.get(f"/api/customers/{customer_id}")
    forecast_response = client.get(f"/api/customers/{customer_id}/forecast")
    history_response = client.get(f"/api/customers/{customer_id}/history")

    assert profile_response.status_code == 200
    assert forecast_response.status_code == 200
    assert history_response.status_code == 200
    profile = profile_response.json()
    forecast = forecast_response.json()
    cutoff = pd.Timestamp(PREDICTION_CUTOFF)
    assert profile["customer_id"] == customer_id
    assert profile["cutoff_date"] == PREDICTION_CUTOFF
    assert pd.Timestamp(profile["last_purchase_date"]) < cutoff
    retrospective = profile["retrospective_description"]
    assert retrospective["source_period"]["start_date"] == str(
        bundle.orders["PurchaseDate"].min().date()
    )
    assert retrospective["source_period"]["end_date"] == str(
        bundle.orders["PurchaseDate"].max().date()
    )
    assert "descriptive_segment" not in profile
    assert "at_risk_flag" not in profile
    assert "retrospective_description" not in forecast
    assert profile["purchase_probability_30d"] == source["purchase_probability_30d"]
    assert profile["purchase_probability_60d"] == source["purchase_probability_60d"]
    assert profile["purchase_probability_90d"] == source["purchase_probability_90d"]
    assert forecast["cumulative_curve"][-1]["day"] == 90
    assert (
        forecast["purchase_probability_30d"]
        <= forecast["purchase_probability_60d"]
        <= forecast["purchase_probability_90d"]
    )
    assert all(pd.Timestamp(order["purchase_date"]) < cutoff for order in history_response.json())


def test_customer_search_is_paginated_and_unknown_forecast_customer_is_404() -> None:
    bundle = service.get_analytics()
    first_page = client.get("/api/customers?page=1&page_size=5")
    assert first_page.status_code == 200
    data = first_page.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["items"]) == 5
    assert len({item["customer_id"] for item in data["items"]}) == 5
    first = data["items"][0]
    assert "retrospective_description" in first
    assert "descriptive_segment" not in first

    source = bundle.snapshot.iloc[0]
    cutoff_item = client.get(
        "/api/customers",
        params={"search": str(int(source["Customer ID"])), "page_size": 5},
    ).json()["items"][0]
    assert cutoff_item["customer_id"] == int(source["Customer ID"])
    assert cutoff_item["recency"] == source["Recency"]
    assert cutoff_item["frequency"] == source["Frequency"]
    assert cutoff_item["monetary_gross"] == source["Monetary_Gross"]

    filtered = client.get(
        "/api/customers",
        params={
            "page": 1,
            "page_size": 100,
            "hist_segment": first["hist_segment"],
            "history_group": first["history_group"],
            "retrospective_segment": first["retrospective_description"][
                "descriptive_segment"
            ],
        },
    )
    assert filtered.status_code == 200
    filtered_items = filtered.json()["items"]
    assert filtered_items
    assert all(item["hist_segment"] == first["hist_segment"] for item in filtered_items)
    assert all(item["history_group"] == first["history_group"] for item in filtered_items)
    assert all(
        item["retrospective_description"]["descriptive_segment"]
        == first["retrospective_description"]["descriptive_segment"]
        for item in filtered_items
    )
    invalid_filter = client.get(
        "/api/customers", params={"history_group": "Not a real group"}
    )
    assert invalid_filter.status_code == 400

    not_eligible = client.get("/api/customers/999999999/forecast")
    assert not_eligible.status_code == 404


def test_model_performance_is_the_saved_notebook_output() -> None:
    response = client.get("/api/model-performance")
    assert response.status_code == 200
    actual = response.json()
    saved = json.loads(
        (METRICS_DIR / "notebook_evaluation_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert actual["test_customers"] == 3373
    assert actual["purchase_metrics"] == saved["purchase_clock"]["test_metrics"]
    assert (
        actual["purchase_history_metrics"]
        == saved["purchase_clock"]["history_group_metrics"]
    )
    assert actual["revenue_metrics"] == saved["spending_forecast"]["test_metrics"]
    assert (
        actual["revenue_group_metrics"]
        == saved["spending_forecast"]["group_metrics"]
    )
    calibration_url = actual["calibration_image_url"]
    image = client.get(calibration_url)
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"
    assert image.content.startswith(b"\x89PNG")


def test_upload_preview_analysis_mapping_and_exports_are_descriptive_only() -> None:
    file_part = ("retail.csv", SAMPLE_UPLOAD.encode("utf-8"), "text/csv")
    preview = client.post("/api/upload/preview", files={"file": file_part})
    assert preview.status_code == 200
    preview_data = preview.json()
    assert preview_data["row_count"] == 5
    assert "Bought at" in preview_data["columns"]

    analysis = client.post(
        "/api/upload/analyze",
        files={"file": file_part},
        data={"mapping": json.dumps(SAMPLE_MAPPING)},
    )
    assert analysis.status_code == 200
    data = analysis.json()
    assert data["summary"]["input_rows"] == 5
    assert data["summary"]["duplicate_rows_removed"] == 1
    assert data["summary"]["retained_cancellation_rows"] == 1
    assert data["summary"]["customer_count"] == 2
    assert data["summary"]["order_count"] == 3
    assert data["trend_period"] == "Weekly"
    assert data["rfm_distributions"]
    assert "forecast" not in data
    assert "prediction" not in json.dumps(data).lower()

    export = client.post(
        "/api/upload/export",
        files={"file": file_part},
        data={
            "mapping": json.dumps(SAMPLE_MAPPING),
            "kind": "cleaned_transactions",
        },
    )
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/csv")
    assert "Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country" in export.text
    assert not (Path("data") / "uploads").exists()


def test_upload_invalid_mapping_is_rejected() -> None:
    response = client.post(
        "/api/upload/analyze",
        files={
            "file": ("retail.csv", SAMPLE_UPLOAD.encode("utf-8"), "text/csv")
        },
        data={"mapping": json.dumps({"Invoice": "Order ref"})},
    )
    assert response.status_code == 400
    assert "Choose a source column" in response.json()["detail"]


def test_overview_rejects_dates_outside_available_history() -> None:
    response = client.get(
        "/api/overview",
        params={"start_date": "2009-01-01", "end_date": "2009-01-31"},
    )
    assert response.status_code == 400
