from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from app.services.demo_service import (
    ALL_ELIGIBLE_CUSTOMERS,
    load_forecast_snapshot,
    lookup_customer_record,
    summarize_forecast_cohort,
)
from app.services.upload_service import (
    build_order_frequency_distribution,
    build_revenue_trend,
    inspect_upload,
    parse_uploaded_file,
)
from scripts.export_notebook_evaluation import export_notebook_evaluation

ROOT = Path(__file__).resolve().parents[1]


def _upload_sample() -> pd.DataFrame:
    rows = [
        {
            "Invoice": "A100",
            "StockCode": "ITEM-1",
            "Description": "Sample item",
            "Quantity": 2,
            "InvoiceDate": "2024-01-02 10:00:00",
            "Price": 12.5,
            "Customer ID": 91001,
            "Country": "United Kingdom",
        },
        {
            "Invoice": "A100",
            "StockCode": "ITEM-2",
            "Description": "Second item",
            "Quantity": 1,
            "InvoiceDate": "2024-01-02 10:00:00",
            "Price": 8.0,
            "Customer ID": 91001,
            "Country": "United Kingdom",
        },
        {
            "Invoice": "A100",
            "StockCode": "ITEM-2",
            "Description": "Second item",
            "Quantity": 1,
            "InvoiceDate": "2024-01-02 10:00:00",
            "Price": 8.0,
            "Customer ID": 91001,
            "Country": "United Kingdom",
        },
        {
            "Invoice": "C100",
            "StockCode": "ITEM-1",
            "Description": "Returned item",
            "Quantity": -1,
            "InvoiceDate": "2024-01-05 10:00:00",
            "Price": 12.5,
            "Customer ID": 91001,
            "Country": "United Kingdom",
        },
        {
            "Invoice": "A101",
            "StockCode": "ITEM-3",
            "Description": "Missing customer",
            "Quantity": 1,
            "InvoiceDate": "2024-01-06 10:00:00",
            "Price": 5.0,
            "Customer ID": None,
            "Country": "United Kingdom",
        },
    ]
    return pd.DataFrame(rows)


def test_csv_upload_is_cleaned_and_remains_descriptive_only():
    original = _upload_sample()
    csv_bytes = original.to_csv(index=False).encode("utf-8")
    parsed = parse_uploaded_file("sample.csv", csv_bytes)
    result = inspect_upload(parsed)

    assert result["summary"]["input_rows"] == 5
    assert result["summary"]["cleaned_rows"] == 3
    assert result["summary"]["customer_count"] == 1
    assert result["summary"]["order_count"] == 1
    assert result["summary"]["positive_order_count"] == 1
    assert result["summary"]["positive_gross_revenue"] == pytest.approx(33.0)
    assert result["summary"]["cancellation_rows"] == 1
    assert result["summary"]["cleaning_report"]["duplicate_rows_removed"] == 1
    assert result["summary"]["cleaning_report"]["missing_customer_rows_removed"] == 1
    assert set(result) == {
        "cleaned_transactions",
        "customer_features",
        "orders",
        "missing_values",
        "summary",
    }
    assert result["customer_features"]["Customer ID"].tolist() == [91001]
    assert result["orders"][["Customer ID", "Invoice", "GrossRevenue"]].to_dict(
        "records"
    ) == [{"Customer ID": 91001, "Invoice": "A100", "GrossRevenue": 33.0}]
    assert build_order_frequency_distribution(result["orders"]).to_dict("records") == [
        {"Purchase frequency": "1 purchase", "Customers": 1},
        {"Purchase frequency": "2 purchases", "Customers": 0},
        {"Purchase frequency": "3 purchases", "Customers": 0},
        {"Purchase frequency": "4+ purchases", "Customers": 0},
    ]
    trend, period, message = build_revenue_trend(result["orders"])
    assert trend is None
    assert period is None
    assert "At least 14 days" in message


def test_xlsx_upload_and_invalid_inputs_are_reported():
    sample = _upload_sample()
    # pandas writes to a buffer when one is supplied.
    from io import BytesIO

    buffer = BytesIO()
    sample.to_excel(buffer, index=False, engine="openpyxl")
    parsed = parse_uploaded_file("sample.xlsx", buffer.getvalue())
    assert len(parsed) == len(sample)
    assert inspect_upload(parsed)["summary"]["input_rows"] == 5

    with pytest.raises(ValueError, match="larger than"):
        parse_uploaded_file("sample.csv", b"0123456789", max_bytes=4)
    with pytest.raises(ValueError, match="CSV file or an Excel"):
        parse_uploaded_file("sample.txt", b"not a supported file")
    with pytest.raises(ValueError, match="empty"):
        parse_uploaded_file("empty.csv", b"")
    with pytest.raises(ValueError, match="Could not read this CSV"):
        parse_uploaded_file("broken.csv", b"\xff\xfe")
    with pytest.raises(ValueError, match="valid .xlsx"):
        parse_uploaded_file("broken.xlsx", b"not an excel workbook")
    with pytest.raises(ValueError, match="Required transaction columns"):
        inspect_upload(pd.DataFrame({"wrong": [1]}))

    invalid_dates = sample.copy()
    invalid_dates.loc[0, "InvoiceDate"] = "not-a-date"
    with pytest.raises(ValueError, match="invalid invoice dates"):
        inspect_upload(invalid_dates)

    cancellation_only = sample.loc[sample["Invoice"].eq("C100")]
    with pytest.raises(ValueError, match="No valid purchase orders remain"):
        inspect_upload(cancellation_only)


def test_forecast_cohorts_use_historical_segments_and_reconcile():
    snapshot = pd.DataFrame(
        {
            "Customer ID": [101, 102, 103],
            "Hist_Segment": ["Early", "Recent", "Early"],
            "Descriptive_Segment": ["Recent", "Early", "Recent"],
            "purchase_probability_30d": [0.1, 0.2, 0.3],
            "purchase_probability_60d": [0.2, 0.4, 0.5],
            "purchase_probability_90d": [0.4, 0.6, 0.7],
            "personalized_expected_revenue_30d": [10.0, 20.0, 30.0],
            "personalized_expected_revenue_60d": [15.0, 25.0, 35.0],
            "personalized_expected_revenue_90d": [18.0, 28.0, 38.0],
        }
    )
    full = summarize_forecast_cohort(snapshot, ALL_ELIGIBLE_CUSTOMERS)
    early = summarize_forecast_cohort(snapshot, "Early")

    assert full["cohort"]["Customer ID"].tolist() == [101, 102, 103]
    assert early["cohort"]["Customer ID"].tolist() == [101, 103]
    assert early["cohort"]["Descriptive_Segment"].tolist() == ["Recent", "Recent"]
    assert early["eligible_customer_count"] == 2
    assert early["expected_returners"] == {
        30: pytest.approx(0.4),
        60: pytest.approx(0.7),
        90: pytest.approx(1.1),
    }
    assert early["expected_revenue"] == {
        30: pytest.approx(40.0),
        60: pytest.approx(50.0),
        90: pytest.approx(56.0),
    }
    for horizon in (30, 60, 90):
        assert full["expected_returners"][horizon] == pytest.approx(
            snapshot[f"purchase_probability_{horizon}d"].sum()
        )
        assert full["expected_revenue"][horizon] == pytest.approx(
            snapshot[f"personalized_expected_revenue_{horizon}d"].sum()
        )


def test_customer_lookup_requires_an_existing_eligible_id():
    snapshot = pd.DataFrame(
        {"Customer ID": [101, 102], "Hist_Segment": ["Early", "Recent"]}
    )
    assert lookup_customer_record(snapshot, "101")["Customer ID"] == 101
    assert lookup_customer_record(snapshot, "999") is None
    assert lookup_customer_record(snapshot, "not-a-number") is None
    assert lookup_customer_record(snapshot, "") is None


def test_revenue_trend_uses_weekly_and_monthly_order_aggregates():
    orders = pd.DataFrame(
        {
            "Customer ID": [101, 101, 102],
            "Invoice": ["A1", "A2", "A3"],
            "PurchaseDate": pd.to_datetime(
                ["2024-01-01", "2024-01-15", "2024-04-02"]
            ),
            "GrossRevenue": [10.0, 5.0, 20.0],
        }
    )
    weekly, weekly_label, weekly_message = build_revenue_trend(orders.iloc[:2].copy())
    monthly, monthly_label, monthly_message = build_revenue_trend(orders)

    assert weekly_message is None
    assert weekly_label == "Weekly"
    assert weekly["GrossRevenue"].sum() == pytest.approx(15.0)
    assert weekly["Orders"].sum() == 2
    assert monthly_message is None
    assert monthly_label == "Monthly"
    assert monthly["GrossRevenue"].sum() == pytest.approx(35.0)
    assert monthly["Orders"].sum() == 3


def test_upload_page_renders_actual_transaction_charts():
    chart_rows = [
        {
            "Invoice": invoice,
            "StockCode": stock_code,
            "Description": "Sample item",
            "Quantity": quantity,
            "InvoiceDate": purchase_date,
            "Price": price,
            "Customer ID": customer_id,
            "Country": "United Kingdom",
        }
        for invoice, stock_code, quantity, purchase_date, price, customer_id in (
            ("A200", "I1", 2, "2024-01-01 10:00:00", 10.0, 92001),
            ("A200", "I2", 1, "2024-01-01 10:00:00", 5.0, 92001),
            ("A201", "I1", 1, "2024-01-15 10:00:00", 30.0, 92001),
            ("A202", "I1", 1, "2024-04-10 10:00:00", 20.0, 92002),
        )
    ]
    csv_bytes = pd.DataFrame(chart_rows).to_csv(index=False).encode("utf-8")
    app = AppTest.from_file(
        str(ROOT / "app" / "pages" / "5_Data_Upload.py"),
        default_timeout=120,
    ).run()
    app.file_uploader[0].set_value(
        ("chart-sample.csv", csv_bytes, "text/csv")
    ).run()

    assert not app.exception
    assert len(app.get("plotly_chart")) == 6
    assert any(
        "not saved to project files or used for model predictions" in item.value
        for item in app.warning
    )
    assert len(app.get("download_button")) == 2


def test_model_performance_summary_is_regenerated_from_saved_notebook_outputs(tmp_path):
    summary_path = tmp_path / "evaluation.json"
    assets_path = tmp_path / "metrics"
    extracted = export_notebook_evaluation(
        root=ROOT,
        output_path=summary_path,
        assets_dir=assets_path,
    )
    saved = json.loads(summary_path.read_text(encoding="utf-8"))

    assert saved == extracted
    assert len(saved["purchase_clock"]["test_metrics"]) == 9
    assert len(saved["spending_forecast"]["test_metrics"]) == 9
    assert len(saved["purchase_clock"]["history_group_metrics"]) == 9
    assert len(saved["spending_forecast"]["group_metrics"]) == 45
    assert saved["source"]["purchase_clock"]["cutoff_date"] == "2010-09-10"
    assert (assets_path / "purchase_clock_test_calibration.png").is_file()
    assert (assets_path / "purchase_clock_test_calibration_90d.png").is_file()


def test_all_streamlit_pages_render_without_exceptions():
    app_files = [
        ROOT / "app" / "main.py",
        *sorted((ROOT / "app" / "pages").glob("*.py")),
    ]
    for app_file in app_files:
        app = AppTest.from_file(str(app_file), default_timeout=120).run()
        assert not app.exception, (
            f"{app_file.name} raised: "
            + "; ".join(error.message for error in app.exception)
        )
        if app_file.name == "1_Business_Overview.py":
            forecast_filter = next(
                item
                for item in app.selectbox
                if item.label == "Forecast-time customer segment"
            )
            assert forecast_filter.value == ALL_ELIGIBLE_CUSTOMERS
            assert forecast_filter.options[0] == ALL_ELIGIBLE_CUSTOMERS
            forecast_filter.set_value(forecast_filter.options[1]).run()
            assert not app.exception
        elif app_file.name == "3_Customer_Intelligence.py":
            assert any(
                "Enter a customer ID" in element.value for element in app.info
            )
            customer_id = int(load_forecast_snapshot()["Customer ID"].iloc[0])
            app.text_input[0].set_value(str(customer_id)).run()
            assert not app.exception
            assert any(
                f"Customer {customer_id:,}" in element.value
                for element in app.subheader
            )
            app.text_input[0].set_value("999999999").run()
            assert not app.exception
            assert any(
                "not in the eligible pre-cutoff cohort" in element.value
                for element in app.warning
            )
