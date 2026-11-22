from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str


class ApiError(BaseModel):
    detail: str


class Period(BaseModel):
    start_date: date
    end_date: date


class MonthlyMetric(BaseModel):
    month: date
    revenue: float
    orders: int


class DescriptiveSegment(BaseModel):
    segment: str
    customers: int
    gross_spend: float
    customer_share: float
    revenue_share: float
    median_recency: float
    median_frequency: float
    median_gross_spend: float


class HistoricalSegment(BaseModel):
    segment: str
    customers: int


class OverviewHistorical(BaseModel):
    customers: int
    orders: int
    revenue: float
    average_order_value: float


class OverviewForecast(BaseModel):
    cutoff_date: date
    hist_segment: str
    eligible_customers: int
    expected_returners_30d: float
    expected_returners_60d: float
    expected_returners_90d: float
    expected_revenue_30d: float
    expected_revenue_60d: float
    expected_revenue_90d: float


class OverviewResponse(BaseModel):
    period: Period
    historical: OverviewHistorical
    monthly_trend: list[MonthlyMetric]
    descriptive_segments: list[DescriptiveSegment]
    forecast: OverviewForecast


class SegmentOverview(BaseModel):
    descriptive_segments: list[DescriptiveSegment]
    historical_segments: list[HistoricalSegment]


class CustomerListItem(BaseModel):
    customer_id: int
    descriptive_segment: str
    hist_segment: str | None
    history_group: str | None
    recency: float
    frequency: float
    monetary_gross: float
    monetary_net: float
    average_order_value: float
    at_risk_flag: bool


class CustomerPage(BaseModel):
    items: list[CustomerListItem]
    total: int
    page: int
    page_size: int


class PurchaseOrder(BaseModel):
    invoice: str
    purchase_date: datetime
    gross_revenue: float


class ProbabilityPoint(BaseModel):
    day: int
    probability: float


class CustomerForecast(BaseModel):
    customer_id: int
    cutoff_date: date
    hist_segment: str
    history_group: str
    first_purchase_date: datetime
    last_purchase_date: datetime
    recency: float
    frequency: float
    monetary_gross: float
    n_historical_gaps: int
    regularized_expected_gap_days: float
    delay_ratio: float
    global_purchase_probability_30d: float
    global_purchase_probability_60d: float
    global_purchase_probability_90d: float
    segment_purchase_probability_30d: float
    segment_purchase_probability_60d: float
    segment_purchase_probability_90d: float
    purchase_probability_30d: float
    purchase_probability_60d: float
    purchase_probability_90d: float
    personalized_expected_revenue_30d: float
    personalized_expected_revenue_60d: float
    personalized_expected_revenue_90d: float
    cumulative_curve: list[ProbabilityPoint]


class CustomerProfile(CustomerForecast):
    descriptive_segment: str
    monetary_net: float
    average_order_value: float
    at_risk_flag: bool


class ForecastHorizon(BaseModel):
    days: int
    global_probability: float
    segment_probability: float
    personalized_probability: float
    historical_rate_expected_revenue: float
    segment_expected_revenue: float
    personalized_expected_revenue: float


class ForecastSummary(BaseModel):
    cutoff_date: date
    hist_segment: str | None
    history_group: str | None
    eligible_customers: int
    expected_returners_30d: float
    expected_returners_60d: float
    expected_returners_90d: float
    horizons: list[ForecastHorizon]
    cumulative_curve: list[ProbabilityPoint]


class PurchaseMetric(BaseModel):
    model: str
    horizon_days: int
    n_customers: int
    brier_score: float
    roc_auc: float
    average_precision: float
    calibration_error: float
    log_loss: float
    mean_predicted_probability: float
    actual_purchase_rate: float


class PurchaseHistoryMetric(BaseModel):
    history_group: str
    horizon_days: int
    n_customers: int
    actual_purchase_rate: float
    mean_predicted_probability: float
    brier_score: float
    roc_auc: float


class RevenueMetric(BaseModel):
    model: str
    horizon_days: int
    n_customers: int
    split_role: str
    mae: float
    rmse: float
    mean_forecast_bias: float
    total_predicted_revenue: float
    total_actual_revenue: float
    total_revenue_bias: float
    aggregate_calibration_ratio: float


class GroupMetric(BaseModel):
    group_type: str
    group: str
    model: str
    horizon_days: int
    n_customers: int
    mae: float
    rmse: float
    mean_forecast_bias: float
    total_predicted_revenue: float
    total_actual_revenue: float
    total_revenue_bias: float
    aggregate_calibration_ratio: float


class ModelPerformance(BaseModel):
    cutoff_date: date
    test_customers: int
    purchase_metrics: list[PurchaseMetric]
    purchase_history_metrics: list[PurchaseHistoryMetric]
    revenue_metrics: list[RevenueMetric]
    revenue_group_metrics: list[GroupMetric]
    calibration_image_url: str
    calibration_90d_image_url: str


class CalibrationAsset(BaseModel):
    url: str


class UploadPreview(BaseModel):
    file_name: str
    row_count: int
    columns: list[str]
    preview_rows: list[dict[str, Any]]


class UploadSummary(BaseModel):
    input_rows: int
    cleaned_rows: int
    excluded_rows: int
    customer_count: int
    order_count: int
    positive_order_count: int
    positive_gross_revenue: float
    cancellation_rows: int
    duplicate_rows: int
    reference_date: datetime
    duplicate_rows_removed: int
    missing_customer_rows_removed: int
    retained_cancellation_rows: int
    retained_zero_price_rows: int


class MissingValue(BaseModel):
    column: str
    missing_count: int


class FrequencyBucket(BaseModel):
    label: str
    customers: int


class RevenuePoint(BaseModel):
    period: date
    revenue: float
    orders: int


class RfmBin(BaseModel):
    lower: float
    upper: float
    customers: int


class RfmDistribution(BaseModel):
    field: str
    label: str
    bins: list[RfmBin]


class UploadAnalysis(BaseModel):
    file_name: str
    summary: UploadSummary
    missing_values: list[MissingValue]
    order_frequency: list[FrequencyBucket]
    revenue_trend: list[RevenuePoint]
    trend_period: str | None
    trend_message: str | None
    rfm_distributions: list[RfmDistribution]
    customer_features_preview: list[dict[str, Any]]


UploadExportKind = Literal["cleaned_transactions", "customer_features"]
