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


class RetrospectiveDescription(BaseModel):
    source_period: Period
    descriptive_segment: str
    monetary_net: float
    average_order_value: float
    at_risk_flag: bool


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
    hist_segment: str | None
    history_group: str | None
    recency: float
    frequency: float
    monetary_gross: float
    retrospective_description: RetrospectiveDescription


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
    retrospective_description: RetrospectiveDescription


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


class ReliabilityMetric(BaseModel):
    horizon_days: int
    model: str
    forecast_cutoff: date
    customer_count: int
    brier_score: float
    log_loss: float
    roc_auc: float | None
    average_precision: float | None
    average_precision_reason: str | None
    expected_calibration_error: float | None
    maximum_calibration_error: float | None
    mean_predicted_probability: float
    observed_purchase_rate: float
    signed_calibration_gap: float
    bin_edges: list[float]
    calibration_bins: list[dict[str, Any]]
    calibration_note: str
    test_outcomes_used_for_method_selection: bool


class ReliabilitySummary(BaseModel):
    metadata: dict[str, Any]
    test_customer_count: int
    purchase_calibration: list[ReliabilityMetric]
    uncertainty_definitions: dict[str, str]
    limitations: list[str]


class ReliabilityCalibration(BaseModel):
    forecast_cutoff: date
    horizons: list[ReliabilityMetric]
    bin_sensitivity: list[dict[str, Any]]
    bin_selection: dict[str, Any]


class ReliabilitySubgroup(BaseModel):
    group_type: str
    group: str
    horizon_days: int
    customer_count: int
    mean_predicted_probability: float
    observed_purchase_rate: float
    brier_score: float
    average_precision: float | None
    calibration_gap: float
    status: str
    status_reason: str | None
    bootstrap_intervals: dict[str, Any]


class ReliabilitySubgroups(BaseModel):
    forecast_cutoff: date
    horizon_days: int | None
    minimum_group_support: int
    items: list[ReliabilitySubgroup]


class ReliabilityRevenue(BaseModel):
    forecast_cutoff: date
    metrics: list[dict[str, Any]]
    history_groups: list[dict[str, Any]]
    large_spender_sensitivity: list[dict[str, Any]]


class PurchaseFeatureEffect(BaseModel):
    feature: str
    original_value: Any
    reference_value: Any
    reference_probabilities: dict[str, float]
    probability_effects: dict[str, float]
    effect_direction: str


class IntervalFeatureContribution(BaseModel):
    transformed_feature: str
    model_feature: str
    transformed_value: float
    coefficient: float
    logit_contribution: float


class IntervalHazardExplanation(BaseModel):
    interval_days: int
    customer_id: int
    input_cutoff: date
    logit_intercept: float
    reconstructed_logit: float
    predicted_hazard: float
    reconstructed_hazard: float
    reconstruction_tolerance: dict[str, float]
    feature_contributions: list[IntervalFeatureContribution]


class SpendingLogContribution(BaseModel):
    transformed_feature: str
    model_feature: str
    transformed_value: float
    coefficient: float
    log_score_contribution: float


class SpendingReferenceSensitivity(BaseModel):
    feature: str
    reference_value: Any
    log_score_difference: float
    conditional_spending_difference: float
    effect_direction: str


class CustomerExplanation(BaseModel):
    customer_id: int
    cutoff_date: date
    model_version: str
    spending_model_version: str
    horizon_days: int
    purchase_probability: float
    reference_probability: float
    purchase_probabilities: dict[str, float]
    reference_probabilities: dict[str, float]
    model_input: dict[str, Any]
    explanation_method: str
    feature_effects: list[PurchaseFeatureEffect]
    interval_hazards: list[float]
    interval_decompositions: list[IntervalHazardExplanation]
    model_input_limitations: list[str]
    conditional_expected_spending: float
    personalized_expected_revenue: float
    spending_model_input: dict[str, Any]
    spending_log_score: float
    spending_log_score_contributions: list[SpendingLogContribution]
    spending_reference_sensitivities: list[SpendingReferenceSensitivity]
    retransformation_method: str
    limitations: list[str]


class DistributionSupportFlag(BaseModel):
    model_scope: str
    atypical_feature_count: int
    flags: list[dict[str, Any]]
    status: str
    interpretation: str


class CustomerReliability(BaseModel):
    customer_id: int
    cutoff_date: date
    horizon_days: int
    history_group: str
    evaluation_group_count: int
    group_brier_score: float | None
    group_calibration_gap: float | None
    reliability_status: str
    distribution_support_flags: list[DistributionSupportFlag]
    limitations: list[str]


class CalibrationAsset(BaseModel):
    url: str


class BehaviorHistogramBin(BaseModel):
    label: str
    lower_bound: float | None
    upper_bound: float | None
    customers: int


class BehaviorDistribution(BaseModel):
    field: str
    label: str
    available_customers: int
    median: float | None
    percentile_75: float | None
    percentile_90: float | None
    bins: list[BehaviorHistogramBin]


class BehaviorSufficiencyCount(BaseModel):
    history_sufficiency: Literal["sufficient", "limited", "insufficient"]
    customers: int


class BehaviorSummary(BaseModel):
    cutoff_date: date
    eligible_customers: int
    policy_version: str
    policy_status: str
    alert_policy_available: bool
    history_sufficiency: list[BehaviorSufficiencyCount]
    distributions: list[BehaviorDistribution]


class BehaviorCustomer(BaseModel):
    customer_id: int
    cutoff_date: date
    first_purchase_date: datetime
    last_purchase_date: datetime
    hist_segment: str | None
    history_group: str | None
    recency: float
    frequency: float
    historical_order_count: int
    completed_gap_count: int
    current_elapsed_gap_days: float
    median_completed_gap_days: float | None
    mean_completed_gap_days: float | None
    mad_completed_gap_days: float | None
    gap_deviation_score: float | None
    gap_deviation_method: str
    recent_order_count: int
    reference_order_count: int
    recent_observed_days: float
    reference_observed_days: float
    recent_order_rate: float
    reference_order_rate: float | None
    purchase_rate_ratio: float | None
    purchase_rate_change: float | None
    raw_purchase_rate_ratio: float | None
    recent_gross_revenue: float
    reference_gross_revenue: float
    recent_revenue_rate: float | None
    reference_revenue_rate: float | None
    revenue_rate_ratio: float | None
    revenue_rate_change: float | None
    recent_ewma_gap_days: float | None
    reference_ewma_gap_days: float | None
    ewma_gap_change_days: float | None
    ewma_gap_observation_count: int
    history_sufficiency: Literal["sufficient", "limited", "insufficient"]
    personalized_delay_ratio: float
    purchase_probability_30d: float
    purchase_probability_60d: float
    purchase_probability_90d: float
    available_indicator_count: int
    policy_version: str
    policy_status: str


class BehaviorCustomerDetail(BehaviorCustomer):
    alert_reasons: list[str]
    indicator_explanations: list[str]


class BehaviorCustomerPage(BaseModel):
    items: list[BehaviorCustomer]
    total: int
    page: int
    page_size: int


class BehaviorTrajectoryPoint(BaseModel):
    period_start: datetime
    period_end: datetime
    order_count: int
    gross_revenue: float
    observed_exposure_days: float
    order_rate: float
    revenue_rate: float


class BehaviorTrajectoryResponse(BaseModel):
    customer_id: int
    cutoff_date: date
    window_days: int
    policy_version: str
    items: list[BehaviorTrajectoryPoint]


class BehaviorEvaluationMetric(BaseModel):
    horizon_days: int
    model: str
    n_customers: int
    roc_auc: float | None
    average_precision: float | None
    precision_at_budget: float | None
    recall_at_budget: float | None
    brier_score: float | None
    log_loss: float | None
    alert_coverage: float | None
    false_alert_rate: float | None
    threshold: float | None
    frozen_threshold_alert_coverage: float | None
    frozen_threshold_false_alert_rate: float | None
    status: str


class BehaviorHypothesisResult(BaseModel):
    hypothesis: str
    statement: str
    status: str
    evidence_summary: str


class BehaviorBootstrapComparison(BaseModel):
    horizon_days: int
    comparison: str
    metric: str
    difference_first_minus_second: float
    confidence_interval_95_lower: float
    confidence_interval_95_upper: float
    valid_resamples: int
    requested_resamples: int
    customer_clusters: int
    resampling_unit: str


class BehaviorSelectionResult(BaseModel):
    horizon_days: int
    selected_ewma_lambda: float
    selected_regularization_c: float
    validation_average_precision: float
    validation_brier_score: float
    validation_customers: int


class BehaviorSubgroupMetric(BaseModel):
    horizon_days: int
    model: str
    group_type: str
    group: str
    n_customers: int
    nonpurchase_rate: float | None
    roc_auc: float | None
    average_precision: float | None
    status: str


class BehaviorEvaluation(BaseModel):
    evaluation_version: str
    feature_version: str
    policy_version: str
    test_cutoff_date: date
    result_status: str
    candidate_f_status: str
    selection_results: list[BehaviorSelectionResult]
    model_comparison: list[BehaviorEvaluationMetric]
    bootstrap_comparisons: list[BehaviorBootstrapComparison]
    subgroup_results: list[BehaviorSubgroupMetric]
    hypotheses: list[BehaviorHypothesisResult]
    limitations: list[str]


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
