from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from app.services.upload_service import inspect_upload, parse_uploaded_file
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
    assert result["summary"]["cancellation_rows"] == 1
    assert result["summary"]["cleaning_report"]["duplicate_rows_removed"] == 1
    assert result["summary"]["cleaning_report"]["missing_customer_rows_removed"] == 1
    assert set(result) == {
        "cleaned_transactions",
        "customer_features",
        "missing_values",
        "summary",
    }
    assert result["customer_features"]["Customer ID"].tolist() == [91001]


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
    with pytest.raises(ValueError, match="Required transaction columns"):
        inspect_upload(pd.DataFrame({"wrong": [1]}))

    invalid_dates = sample.copy()
    invalid_dates.loc[0, "InvoiceDate"] = "not-a-date"
    with pytest.raises(ValueError, match="invalid invoice dates"):
        inspect_upload(invalid_dates)


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
