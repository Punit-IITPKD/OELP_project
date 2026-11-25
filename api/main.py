"""FastAPI routes for the saved-model OELP customer-intelligence application."""

from __future__ import annotations

import json
from datetime import date
from enum import IntEnum
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, FastAPI, File, Form, HTTPException, Path as PathParameter, Query, UploadFile
from fastapi.responses import FileResponse, Response

from app.config import MAX_UPLOAD_BYTES
from api import service
from api import revenue_service
from api import research_service
from api import trajectory_service
from api.schemas import (
    BehaviorCustomerDetail,
    BehaviorCustomerPage,
    BehaviorEvaluation,
    BehaviorSummary,
    BehaviorTrajectoryResponse,
    CalibrationAsset,
    CustomerForecast,
    CustomerExplanation,
    CustomerPage,
    CustomerProfile,
    CustomerReliability,
    CustomerTrajectoryExplanation,
    CustomerTrajectoryResponse,
    EligibilityFilters,
    FinalResearchSummary,
    ForecastSummary,
    HealthStatus,
    ModelPerformance,
    OverviewResponse,
    PurchaseOrder,
    ReliabilityCalibration,
    ReliabilityRevenue,
    ReliabilitySubgroups,
    ReliabilitySummary,
    RevenueConcentrationResponse,
    RevenueCustomerDetail,
    RevenueCustomerPage,
    RevenueExposureEvaluation,
    RevenueExposureSummary,
    RevenueScatterResponse,
    RetentionScenarioRequest,
    RetentionScenarioResponse,
    RetentionStrategyComparisonRequest,
    RetentionStrategyComparisonResponse,
    SegmentOverview,
    TrajectoryClustersResponse,
    TrajectoryCustomerPage,
    TrajectoryEvaluationResponse,
    TrajectorySummary,
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


class HorizonDays(IntEnum):
    DAYS_30 = 30
    DAYS_60 = 60
    DAYS_90 = 90


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


@router.get("/research/summary", response_model=FinalResearchSummary)
def research_summary() -> dict[str, Any]:
    try:
        return research_service.get_research_summary()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail="The final research summary is unavailable or out of date.",
        ) from error


@router.get(
    "/revenue-exposure/summary",
    response_model=RevenueExposureSummary,
)
def revenue_exposure_summary(
    horizon_days: HorizonDays = Query(default=HorizonDays.DAYS_30),
) -> dict[str, Any]:
    return revenue_service.get_revenue_summary(int(horizon_days))


@router.get(
    "/revenue-exposure/customers",
    response_model=RevenueCustomerPage,
)
def revenue_exposure_customers(
    horizon_days: HorizonDays = Query(default=HorizonDays.DAYS_30),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    ranking_strategy: str = Query(default="nonreturn_spending_proxy"),
    hist_segment: str | None = None,
    history_group: str | None = None,
    history_sufficiency: str | None = Query(
        default=None, pattern="^(sufficient|limited|insufficient)$"
    ),
    require_sufficient_behavior_history: bool = False,
    behavior_filter: str = Query(
        default="none",
        pattern="^(none|declining_purchase_rate|declining_revenue_rate)$",
    ),
    search: str | None = Query(default=None, max_length=32, pattern="^[0-9]*$"),
    sort_by: Literal[
        "priority_rank",
        "customer_id",
        "recency_days",
        "purchase_probability",
        "conditional_expected_spending_gbp",
        "personalized_expected_revenue_gbp",
        "nonreturn_weighted_conditional_spending_proxy_gbp",
        "historical_gross_spending_gbp",
    ] = "priority_rank",
    sort_descending: bool = False,
) -> dict[str, Any]:
    filters = EligibilityFilters(
        hist_segment=hist_segment,
        history_group=history_group,
        history_sufficiency=history_sufficiency,
        require_sufficient_behavior_history=require_sufficient_behavior_history,
        behavior_filter=behavior_filter,
    )
    try:
        return revenue_service.get_revenue_customers(
            int(horizon_days),
            page=page,
            page_size=page_size,
            ranking_strategy=ranking_strategy,
            filters=filters.model_dump(),
            search=search,
            sort_by=sort_by,
            sort_descending=sort_descending,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get(
    "/revenue-exposure/scatter",
    response_model=RevenueScatterResponse,
)
def revenue_exposure_scatter(
    horizon_days: HorizonDays = Query(default=HorizonDays.DAYS_30),
    limit: int = Query(default=1000, ge=1, le=3373),
    hist_segment: str | None = None,
    history_sufficiency: str | None = Query(
        default=None, pattern="^(sufficient|limited|insufficient)$"
    ),
) -> dict[str, Any]:
    return revenue_service.get_revenue_scatter(
        int(horizon_days),
        limit=limit,
        hist_segment=hist_segment,
        history_sufficiency=history_sufficiency,
    )


@router.get(
    "/revenue-exposure/concentration",
    response_model=RevenueConcentrationResponse,
)
def revenue_exposure_concentration(
    horizon_days: HorizonDays = Query(default=HorizonDays.DAYS_30),
) -> dict[str, Any]:
    return revenue_service.get_revenue_concentration(int(horizon_days))


@router.get(
    "/revenue-exposure/evaluation",
    response_model=RevenueExposureEvaluation,
)
def revenue_exposure_evaluation() -> dict[str, Any]:
    try:
        return revenue_service.get_revenue_evaluation()
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get(
    "/customers/{customer_id}/revenue-exposure",
    response_model=RevenueCustomerDetail,
)
def revenue_exposure_customer(
    customer_id: int = PathParameter(gt=0),
    horizon_days: HorizonDays = Query(default=HorizonDays.DAYS_30),
) -> dict[str, Any]:
    try:
        return revenue_service.get_revenue_customer(customer_id, int(horizon_days))
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff forecast cohort.",
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/retention/scenarios", response_model=RetentionScenarioResponse)
def retention_scenario(
    request: RetentionScenarioRequest,
) -> dict[str, Any]:
    try:
        return revenue_service.run_retention_scenario(
            request.model_dump(
                exclude={"ranking_strategy", "eligibility_filters"}
            ),
            ranking_strategy=request.ranking_strategy,
            eligibility_filters=request.eligibility_filters.model_dump(),
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post(
    "/retention/compare-strategies",
    response_model=RetentionStrategyComparisonResponse,
)
def retention_strategy_comparison(
    request: RetentionStrategyComparisonRequest,
) -> dict[str, Any]:
    try:
        return revenue_service.compare_retention_strategies(
            request.scenario.model_dump(),
            request.ranking_strategies,
            request.eligibility_filters.model_dump(),
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


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


@router.get("/behavior/summary", response_model=BehaviorSummary)
def behavior_summary() -> dict[str, Any]:
    return service.get_behavior_summary()


@router.get("/behavior/customers", response_model=BehaviorCustomerPage)
def behavior_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    search: str | None = None,
    hist_segment: str | None = None,
    history_group: str | None = None,
    history_sufficiency: str | None = Query(
        default=None, pattern="^(sufficient|limited|insufficient)$"
    ),
    sort_by: str = Query(
        default="current_elapsed_gap_days",
        pattern="^(current_elapsed_gap_days|gap_deviation_score|purchase_rate_ratio|revenue_rate_ratio|personalized_delay_ratio|recency)$",
    ),
    sort_direction: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> dict[str, Any]:
    try:
        return service.get_behavior_customers(
            page=page,
            page_size=page_size,
            search=search,
            hist_segment=hist_segment,
            history_group=history_group,
            history_sufficiency=history_sufficiency,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/behavior/evaluation", response_model=BehaviorEvaluation)
def behavior_evaluation() -> dict[str, Any]:
    try:
        return service.get_behavior_evaluation()
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail="Behavior evaluation is not available.") from error
    except ValueError as error:
        raise HTTPException(status_code=500, detail="Saved behavior evaluation is invalid.") from error


@router.get(
    "/customers/{customer_id}/behavior",
    response_model=BehaviorCustomerDetail,
)
def customer_behavior(
    customer_id: int = PathParameter(gt=0),
) -> dict[str, Any]:
    try:
        return service.get_customer_behavior(customer_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff behavior cohort.",
        ) from error


@router.get(
    "/customers/{customer_id}/behavior/trajectory",
    response_model=BehaviorTrajectoryResponse,
)
def customer_behavior_trajectory(
    customer_id: int = PathParameter(gt=0),
) -> dict[str, Any]:
    try:
        return service.get_customer_behavior_trajectory(customer_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff behavior cohort.",
        ) from error


@router.get(
    "/trajectories/summary",
    response_model=TrajectorySummary,
)
def trajectory_summary() -> dict[str, Any]:
    try:
        return trajectory_service.get_trajectory_summary()
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="Trajectory source data is not available.",
        ) from error


@router.get(
    "/trajectories/clusters",
    response_model=TrajectoryClustersResponse,
)
def trajectory_clusters() -> dict[str, Any]:
    try:
        return trajectory_service.get_trajectory_clusters()
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="Trajectory source data is not available.",
        ) from error


@router.get(
    "/trajectories/customers",
    response_model=TrajectoryCustomerPage,
)
def trajectory_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    search: str | None = Query(default=None, max_length=16, pattern="^[0-9]*$"),
    history_sufficiency: str | None = Query(
        default=None,
        pattern="^(sufficient_for_functional_analysis|sufficient_for_summary_trajectory|limited_history|insufficient_history)$",
    ),
    hist_segment: str | None = Query(default=None, max_length=80),
    cluster_id: int | None = Query(default=None, ge=0, le=5),
) -> dict[str, Any]:
    try:
        return trajectory_service.get_trajectory_customers(
            page=page,
            page_size=page_size,
            search=search,
            history_sufficiency=history_sufficiency,
            hist_segment=hist_segment,
            cluster_id=cluster_id,
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="Trajectory source data is not available.",
        ) from error


@router.get(
    "/trajectories/evaluation",
    response_model=TrajectoryEvaluationResponse,
)
def trajectory_evaluation() -> dict[str, Any]:
    try:
        return trajectory_service.get_trajectory_evaluation()
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="Trajectory evaluation is not available.",
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail="Saved trajectory evaluation is invalid.",
        ) from error


@router.get(
    "/customers/{customer_id}/trajectory",
    response_model=CustomerTrajectoryResponse,
)
def customer_trajectory(
    customer_id: int = PathParameter(gt=0),
) -> dict[str, Any]:
    try:
        return trajectory_service.get_customer_trajectory(customer_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the trajectory cutoff cohort.",
        ) from error
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="Trajectory source data is not available.",
        ) from error


@router.get(
    "/customers/{customer_id}/trajectory/explanation",
    response_model=CustomerTrajectoryExplanation,
)
def customer_trajectory_explanation(
    customer_id: int = PathParameter(gt=0),
) -> dict[str, Any]:
    try:
        return trajectory_service.get_customer_trajectory_explanation(customer_id)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the trajectory cutoff cohort.",
        ) from error
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail="Trajectory source data is not available.",
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


@router.get("/reliability/summary", response_model=ReliabilitySummary)
def reliability_summary() -> dict[str, Any]:
    try:
        return service.get_reliability_summary()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=503, detail="Prediction reliability artifacts are unavailable."
        ) from error


@router.get("/reliability/calibration", response_model=ReliabilityCalibration)
def reliability_calibration() -> dict[str, Any]:
    try:
        return service.get_reliability_calibration()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=503, detail="Prediction reliability artifacts are unavailable."
        ) from error


@router.get("/reliability/subgroups", response_model=ReliabilitySubgroups)
def reliability_subgroups(
    horizon_days: HorizonDays | None = None,
) -> dict[str, Any]:
    try:
        return service.get_reliability_subgroups(horizon_days)
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=503, detail="Prediction reliability artifacts are unavailable."
        ) from error


@router.get("/reliability/revenue", response_model=ReliabilityRevenue)
def reliability_revenue() -> dict[str, Any]:
    try:
        return service.get_reliability_revenue()
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=503, detail="Prediction reliability artifacts are unavailable."
        ) from error


@router.get(
    "/customers/{customer_id}/explanation",
    response_model=CustomerExplanation,
)
def customer_explanation(
    customer_id: int = PathParameter(gt=0),
    horizon_days: HorizonDays = HorizonDays.DAYS_30,
) -> dict[str, Any]:
    try:
        return service.get_customer_explanation(customer_id, horizon_days)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff forecast cohort.",
        ) from error
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail="Prediction explanation artifacts or saved models are unavailable.",
        ) from error


@router.get(
    "/customers/{customer_id}/reliability",
    response_model=CustomerReliability,
)
def customer_reliability(
    customer_id: int = PathParameter(gt=0),
    horizon_days: HorizonDays = HorizonDays.DAYS_30,
) -> dict[str, Any]:
    try:
        return service.get_customer_reliability(customer_id, horizon_days)
    except KeyError as error:
        raise HTTPException(
            status_code=404,
            detail="Customer is not in the eligible pre-cutoff forecast cohort.",
        ) from error
    except (FileNotFoundError, ValueError) as error:
        raise HTTPException(
            status_code=503,
            detail="Prediction reliability artifacts or saved models are unavailable.",
        ) from error


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
