"""FastAPI routes for the saved-model OELP customer-intelligence application."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, File, Form, HTTPException, Path as PathParameter, Query, UploadFile
from fastapi.responses import FileResponse, Response

from app.config import MAX_UPLOAD_BYTES
from api import service
from api.schemas import (
    CalibrationAsset,
    CustomerForecast,
    CustomerPage,
    CustomerProfile,
    ForecastSummary,
    HealthStatus,
    ModelPerformance,
    OverviewResponse,
    PurchaseOrder,
    SegmentOverview,
    UploadAnalysis,
    UploadExportKind,
    UploadPreview,
)

app = FastAPI(
    title="OELP Customer Intelligence API",
    version="0.2.0",
    description=(
        "Historical analytics backed by saved OELP models. Requests never train "
        "models and uploaded data is analyzed in memory for descriptive use only."
    ),
)
router = APIRouter(prefix="/api")


def _bad_upload(error: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(error))


async def _read_upload(file: UploadFile) -> tuple[str, bytes]:
    file_name = file.filename or "upload.csv"
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File is larger than the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.",
        )
    return file_name, data


def _parse_mapping(mapping: str) -> dict[str, Any]:
    try:
        parsed = json.loads(mapping)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="Column mapping must be a valid JSON object.",
        ) from error
    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=400,
            detail="Column mapping must be a JSON object.",
        )
    return parsed


@router.get("/health", response_model=HealthStatus)
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/healthz", response_model=HealthStatus)
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/overview", response_model=OverviewResponse)
def overview(
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict[str, Any]:
    try:
        return service.get_overview(
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/segments", response_model=SegmentOverview)
def segments() -> dict[str, Any]:
    return service.get_segments()


@router.get("/customers", response_model=CustomerPage)
def customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    search: str | None = None,
    retrospective_segment: str | None = None,
    hist_segment: str | None = None,
    history_group: str | None = None,
) -> dict[str, Any]:
    if history_group is not None and history_group not in service.HISTORY_GROUPS:
        raise HTTPException(status_code=400, detail="Unknown purchase-history group.")
    return service.get_customers(
        page=page,
        page_size=page_size,
        search=search,
        retrospective_segment=retrospective_segment,
        hist_segment=hist_segment,
        history_group=history_group,
    )


@router.get("/customers/{customer_id}", response_model=CustomerProfile)
def customer(
    customer_id: int = PathParameter(gt=0),
) -> dict[str, Any]:
    try:
        return service.get_customer_profile(customer_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff forecast cohort.",
        ) from error


@router.get(
    "/customers/{customer_id}/history",
    response_model=list[PurchaseOrder],
)
def customer_history(
    customer_id: int = PathParameter(gt=0),
) -> list[dict[str, Any]]:
    try:
        return service.get_customer_history(customer_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff forecast cohort.",
        ) from error


@router.get(
    "/customers/{customer_id}/forecast",
    response_model=CustomerForecast,
)
def customer_forecast(
    customer_id: int = PathParameter(gt=0),
) -> dict[str, Any]:
    try:
        profile = service.get_customer_profile(customer_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff forecast cohort.",
        ) from error
    return {
        key: value
        for key, value in profile.items()
        if key != "retrospective_description"
    }


@router.get("/forecasts/summary", response_model=ForecastSummary)
def forecast_summary(
    hist_segment: str | None = None,
    history_group: str | None = None,
) -> dict[str, Any]:
    if history_group is not None and history_group not in service.HISTORY_GROUPS:
        raise HTTPException(status_code=400, detail="Unknown purchase-history group.")
    return service.get_forecast_summary(hist_segment, history_group)


@router.get("/model-performance", response_model=ModelPerformance)
def model_performance() -> dict[str, Any]:
    return service.get_model_performance()


@router.get("/model-performance/calibration", response_model=CalibrationAsset)
def calibration_image() -> dict[str, str]:
    return {"url": "/api/model-performance/assets/purchase_clock_test_calibration.png"}


@router.get(
    "/model-performance/calibration-90d",
    response_model=CalibrationAsset,
)
def calibration_image_90d() -> dict[str, str]:
    return {
        "url": "/api/model-performance/assets/purchase_clock_test_calibration_90d.png"
    }


@router.get("/model-performance/assets/{filename}")
def calibration_asset(filename: str) -> FileResponse:
    allowed = {
        "purchase_clock_test_calibration.png": False,
        "purchase_clock_test_calibration_90d.png": True,
    }
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="Calibration asset not found.")
    try:
        path = service.get_calibration_asset(ninety_day=allowed[filename])
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Calibration asset not found.") from error
    return FileResponse(path, media_type="image/png", filename=Path(filename).name)


@router.post("/upload/preview", response_model=UploadPreview)
async def upload_preview(
    file: UploadFile = File(...),
) -> dict[str, Any]:
    file_name, data = await _read_upload(file)
    try:
        frame = service.parse_upload(file_name, data)
        service.validate_source_headers(frame)
    except (ValueError, TypeError, OSError) as error:
        raise _bad_upload(error) from error
    return {
        "file_name": file_name,
        "row_count": int(len(frame)),
        "columns": [str(column) for column in frame.columns],
        "preview_rows": json.loads(
            frame.head(20).to_json(orient="records", date_format="iso")
        ),
    }


@router.post("/upload/analyze", response_model=UploadAnalysis)
async def upload_analyze(
    file: UploadFile = File(...),
    mapping: str = Form(...),
) -> dict[str, Any]:
    file_name, data = await _read_upload(file)
    parsed_mapping = _parse_mapping(mapping)
    try:
        return service.analyze_upload(file_name, data, parsed_mapping)
    except (ValueError, TypeError, KeyError, OSError) as error:
        raise _bad_upload(error) from error


@router.post("/upload/export")
async def upload_export(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    kind: UploadExportKind = Form(...),
) -> Response:
    file_name, data = await _read_upload(file)
    parsed_mapping = _parse_mapping(mapping)
    try:
        csv_text, download_name = service.export_upload(
            file_name,
            data,
            parsed_mapping,
            kind,
        )
    except (ValueError, TypeError, KeyError, OSError) as error:
        raise _bad_upload(error) from error
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )


app.include_router(router)
