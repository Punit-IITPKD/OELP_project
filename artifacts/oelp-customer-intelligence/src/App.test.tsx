import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import App from './App';

const mocks = vi.hoisted(() => {
  const state = (data: unknown) => ({
    data,
    isLoading: false,
    isError: false,
    isSuccess: true,
    isFetching: false,
    refetch: vi.fn(),
  });

  const customer = {
    customer_id: 12345,
    hist_segment: 'Lapsed / At-Risk',
    history_group: 'Five or more purchases',
    recency: 14,
    frequency: 4,
    monetary_gross: 280,
    retrospective_description: {
      source_period: { start_date: '2009-12-01', end_date: '2010-12-09' },
      descriptive_segment: 'Loyal',
      monetary_net: 270,
      average_order_value: 70,
      at_risk_flag: true,
    },
  };
  const profile = {
    ...customer,
    cutoff_date: '2010-09-10',
    first_purchase_date: '2009-01-01T00:00:00',
    last_purchase_date: '2010-08-27T00:00:00',
    n_historical_gaps: 3,
    regularized_expected_gap_days: 24,
    delay_ratio: 1.1,
    global_purchase_probability_30d: 0.2,
    global_purchase_probability_60d: 0.4,
    global_purchase_probability_90d: 0.6,
    segment_purchase_probability_30d: 0.3,
    segment_purchase_probability_60d: 0.5,
    segment_purchase_probability_90d: 0.7,
    purchase_probability_30d: 0.35,
    purchase_probability_60d: 0.55,
    purchase_probability_90d: 0.75,
    personalized_expected_revenue_30d: 35,
    personalized_expected_revenue_60d: 55,
    personalized_expected_revenue_90d: 75,
    cumulative_curve: [{ day: 90, probability: 0.75 }],
  };
  const overview = {
    period: { start_date: '2010-01-01', end_date: '2010-09-10' },
    historical: {
      customers: 12,
      orders: 21,
      revenue: 1400,
      average_order_value: 66.67,
    },
    monthly_trend: [{ month: '2010-01-01', revenue: 200, orders: 4 }],
    descriptive_segments: [
      {
        segment: 'Loyal',
        customers: 6,
        gross_spend: 800,
        customer_share: 0.5,
        revenue_share: 0.57,
        median_recency: 10,
        median_frequency: 4,
        median_gross_spend: 120,
      },
    ],
    forecast: {
      cutoff_date: '2010-09-10',
      hist_segment: 'All eligible customers',
      eligible_customers: 3373,
      expected_returners_30d: 900,
      expected_returners_60d: 1300,
      expected_returners_90d: 1700,
      expected_revenue_30d: 100000,
      expected_revenue_60d: 150000,
      expected_revenue_90d: 200000,
    },
  };
  const segments = {
    descriptive_segments: overview.descriptive_segments,
    historical_segments: [
      { segment: 'Lapsed / At-Risk', customers: 2000 },
      { segment: 'Steady', customers: 1373 },
    ],
  };
  const forecastSummary = {
    cutoff_date: '2010-09-10',
    hist_segment: null,
    history_group: null,
    eligible_customers: 3373,
    expected_returners_30d: 900,
    expected_returners_60d: 1300,
    expected_returners_90d: 1700,
    horizons: [
      {
        days: 30,
        global_probability: 0.2,
        segment_probability: 0.3,
        personalized_probability: 0.35,
        historical_rate_expected_revenue: 30000,
        segment_expected_revenue: 32000,
        personalized_expected_revenue: 35000,
      },
      {
        days: 60,
        global_probability: 0.4,
        segment_probability: 0.5,
        personalized_probability: 0.55,
        historical_rate_expected_revenue: 40000,
        segment_expected_revenue: 50000,
        personalized_expected_revenue: 55000,
      },
      {
        days: 90,
        global_probability: 0.6,
        segment_probability: 0.7,
        personalized_probability: 0.75,
        historical_rate_expected_revenue: 60000,
        segment_expected_revenue: 70000,
        personalized_expected_revenue: 75000,
      },
    ],
    cumulative_curve: [{ day: 90, probability: 0.75 }],
  };
  const performance = {
    cutoff_date: '2010-09-10',
    test_customers: 3373,
    purchase_metrics: [],
    purchase_history_metrics: [
      {
        history_group: 'Exactly one purchase',
        horizon_days: 30,
        n_customers: 12,
        actual_purchase_rate: 0.25,
        mean_predicted_probability: 0.3,
        brier_score: 0.2,
        roc_auc: 0.6,
      },
    ],
    revenue_metrics: [],
    revenue_group_metrics: [],
    calibration_image_url: '/api/model-performance/assets/purchase_clock_test_calibration.png',
    calibration_90d_image_url: '/api/model-performance/assets/purchase_clock_test_calibration_90d.png',
  };
  const uploadPreview = {
    file_name: 'retail.csv',
    row_count: 2,
    columns: [
      'Invoice',
      'StockCode',
      'Description',
      'Quantity',
      'InvoiceDate',
      'Price',
      'Customer ID',
      'Country',
    ],
    preview_rows: [],
  };
  const uploadAnalysis = {
    file_name: 'retail.csv',
    summary: {
      input_rows: 2,
      cleaned_rows: 2,
      excluded_rows: 0,
      customer_count: 1,
      order_count: 2,
      positive_order_count: 2,
      positive_gross_revenue: 35,
      cancellation_rows: 0,
      duplicate_rows: 0,
      reference_date: '2010-02-01',
      duplicate_rows_removed: 0,
      missing_customer_rows_removed: 0,
      retained_cancellation_rows: 0,
      retained_zero_price_rows: 0,
    },
    missing_values: [],
    order_frequency: [{ label: '2', customers: 1 }],
    revenue_trend: [{ period: '2010-01-01', revenue: 35, orders: 2 }],
    trend_period: 'Weekly',
    trend_message: '',
    rfm_distributions: [
      {
        field: 'Recency',
        label: 'Recency (days)',
        bins: [{ lower: 10, upper: 20, customers: 1 }],
      },
    ],
    customer_features_preview: [{ CustomerID: 12345, Frequency: 2 }],
  };
  const behaviorCustomer = {
    customer_id: 12345, cutoff_date: '2010-09-10', first_purchase_date: '2009-01-01', last_purchase_date: '2010-08-27',
    hist_segment: 'Lapsed / At-Risk', history_group: 'Five or more purchases', recency: 14, frequency: 4, historical_order_count: 4,
    completed_gap_count: 3, current_elapsed_gap_days: 14, median_completed_gap_days: 24, mean_completed_gap_days: 25,
    mad_completed_gap_days: 4, gap_deviation_score: 0.8, gap_deviation_method: 'robust_mad', recent_order_count: 2,
    reference_order_count: 2, recent_observed_days: 60, reference_observed_days: 120, recent_order_rate: 0.03,
    reference_order_rate: 0.02, purchase_rate_ratio: 1.5, purchase_rate_change: 0.01, raw_purchase_rate_ratio: 1.4,
    recent_gross_revenue: 140, reference_gross_revenue: 140, recent_revenue_rate: 2.3, reference_revenue_rate: 1.2,
    revenue_rate_ratio: 1.9, revenue_rate_change: 1.1, recent_ewma_gap_days: 22, reference_ewma_gap_days: 25,
    ewma_gap_change_days: -3, ewma_gap_observation_count: 3, history_sufficiency: 'sufficient', personalized_delay_ratio: 0.8,
    purchase_probability_30d: 0.35, purchase_probability_60d: 0.55, purchase_probability_90d: 0.75,
    available_indicator_count: 12, policy_version: 'notebook08-v1', policy_status: 'research_only',
  };
  const behaviorSummary = {
    cutoff_date: '2010-09-10', eligible_customers: 3373, policy_version: 'notebook08-v1',
    policy_status: 'research_only', alert_policy_available: false,
    history_sufficiency: [{ history_sufficiency: 'sufficient', customers: 1800 }, { history_sufficiency: 'limited', customers: 1000 }, { history_sufficiency: 'insufficient', customers: 573 }],
    distributions: [{ field: 'gap_deviation_score', label: 'Gap deviation score', available_customers: 2100, median: 0.2, percentile_75: 0.8, percentile_90: 1.6, bins: [{ label: '0–1', lower_bound: 0, upper_bound: 1, customers: 1400 }, { label: '1+', lower_bound: 1, upper_bound: null, customers: 700 }] }],
  };
  const behaviorEvaluation = {
    evaluation_version: 'eval-v1', feature_version: 'features-v1', policy_version: 'policy-v1',
    test_cutoff_date: '2010-09-10', result_status: 'research_only', candidate_f_status: 'not_feasible',
    selection_results: [{ horizon_days: 30, selected_ewma_lambda: 0.6, selected_regularization_c: 1, validation_average_precision: 0.3, validation_brier_score: 0.2, validation_customers: 120 }],
    model_comparison: [{ horizon_days: 30, model: 'Candidate F', n_customers: 120, roc_auc: 0.61, average_precision: 0.22, precision_at_budget: 0.31, recall_at_budget: 0.18, brier_score: 0.19, log_loss: 0.57, alert_coverage: null, false_alert_rate: null, threshold: null, frozen_threshold_alert_coverage: null, frozen_threshold_false_alert_rate: null, status: 'exploratory' }],
    bootstrap_comparisons: [{ horizon_days: 30, comparison: 'Candidate F vs baseline', metric: 'ROC AUC', difference_first_minus_second: 0.04, confidence_interval_95_lower: -0.02, confidence_interval_95_upper: 0.1, valid_resamples: 900, requested_resamples: 1000, customer_clusters: 120, resampling_unit: 'Customer ID; paired across both score series' }],
    subgroup_results: [{ horizon_days: 30, model: 'Candidate F', group_type: 'history_sufficiency', group: 'sufficient', n_customers: 100, nonpurchase_rate: 0.5, roc_auc: 0.61, average_precision: 0.22, status: 'evaluated' }],
    hypotheses: [{ hypothesis: 'H1', statement: 'Recent purchase rhythm adds evidence.', status: 'inconclusive', evidence_summary: 'Interval includes no difference.' }],
    limitations: ['Historical single-cutoff evaluation; external validation is required.'],
  };
  const behaviorTrajectory = {
    customer_id: 12345, cutoff_date: '2010-09-10', window_days: 180, policy_version: 'notebook08-v1',
    items: [{ period_start: '2010-06-01', period_end: '2010-06-30', order_count: 1, gross_revenue: 70, observed_exposure_days: 30, order_rate: 0.033, revenue_rate: 2.33 }],
  };
  const reliabilitySummary = {
    metadata: { forecast_cutoff: '2010-09-10', evaluation_set: 'TEST' },
    test_customer_count: 3373,
    purchase_calibration: [{
      horizon_days: 30, model: 'Saved model', forecast_cutoff: '2010-09-10', customer_count: 3373,
      brier_score: 0.19, log_loss: 0.58, roc_auc: 0.64, average_precision: 0.31,
      average_precision_reason: null, expected_calibration_error: 0.04, maximum_calibration_error: 0.1,
      mean_predicted_probability: 0.28, observed_purchase_rate: 0.26, signed_calibration_gap: 0.02,
      bin_edges: [0, 1], calibration_bins: [], calibration_note: 'Calibration summary',
      test_outcomes_used_for_method_selection: false,
    }],
    uncertainty_definitions: { bootstrap: 'Customer-cluster resampling' },
    limitations: ['Single historical cutoff.'],
  };
  const customerExplanation = {
    customer_id: 12345, cutoff_date: '2010-09-10', model_version: 'saved-v1', spending_model_version: 'spend-v1',
    horizon_days: 30, purchase_probability: 0.35, reference_probability: 0.3,
    purchase_probabilities: { personalized: 0.35 }, reference_probabilities: { train_reference: 0.3 },
    model_input: { recency: 14, frequency: 4 }, explanation_method: 'reference substitution',
    feature_effects: [{ feature: 'recency', original_value: 14, reference_value: 40, reference_probabilities: { personalized: 0.3 }, probability_effects: { personalized: -0.05 }, effect_direction: 'lower' }],
    interval_hazards: [], interval_decompositions: [], model_input_limitations: ['Historical inputs only.'],
    conditional_expected_spending: 100, personalized_expected_revenue: 35, spending_model_input: {},
    spending_log_score: -1.1, spending_log_score_contributions: [], spending_reference_sensitivities: [],
    retransformation_method: 'smearing', limitations: ['Research use only.'],
  };
  const customerReliability = {
    customer_id: 12345, cutoff_date: '2010-09-10', horizon_days: 30,
    history_group: 'Five or more purchases', evaluation_group_count: 120,
    group_brier_score: 0.2, group_calibration_gap: 0.03, reliability_status: 'evaluated',
    distribution_support_flags: [{ model_scope: 'purchase', atypical_feature_count: 1, flags: [], status: 'some_support', interpretation: 'One atypical input.' }],
    limitations: ['Group summary only.'],
  };
  const reliabilityCalibration = { forecast_cutoff: '2010-09-10', horizons: [{
    ...reliabilitySummary.purchase_calibration[0], calibration_bins: [{ bin: 1, predicted_mean: 0.2, observed_mean: 0.18, count: 400 }],
  }], bin_sensitivity: [], bin_selection: {} };
  const reliabilitySubgroups = { forecast_cutoff: '2010-09-10', horizon_days: 30, minimum_group_support: 50, items: [] };
  const reliabilityRevenue = { forecast_cutoff: '2010-09-10', metrics: [], history_groups: [], large_spender_sensitivity: [] };
  const revenueItem = {
    customer_id: 12345, cutoff_date: '2010-09-10', horizon_days: 30, currency_code: 'GBP',
    hist_segment: 'Lapsed / At-Risk', history_group: 'Five or more purchases', recency_days: 14,
    purchase_frequency: 4, historical_gross_spending_gbp: 280, purchase_probability: 0.35,
    conditional_expected_spending_gbp: 100, personalized_expected_revenue_gbp: 35,
    historical_rate_expected_revenue_gbp: 31, segment_expected_revenue_gbp: 39,
    nonreturn_probability: 0.65, nonreturn_weighted_conditional_spending_proxy_gbp: 65,
    opportunity_proxy_method: 'nonreturn_weighted_conditional_spending', estimated_revenue_exposure_gbp: null,
    exposure_status: 'not_estimable', history_sufficiency: 'sufficient', purchase_rate_ratio: 1.1,
    revenue_rate_ratio: 1.2, gap_deviation_score: 0.4, policy_status: 'research_only',
    available_indicator_count: 4, reliability_status: 'group_evaluated', reliability_evidence_count: 120,
    reliability_group_brier_score: 0.2, reliability_group_calibration_gap: 0.03,
    reliability_evidence_cutoff: '2010-09-10', reliability_is_individual_guarantee: false,
     selection_eligible: true,
    priority_rank: 1, priority_score: 65, priority_score_unit: 'GBP', pareto_front: 1,
  };
  const revenueSummary = {
    cutoff_date: '2010-09-10', horizon_days: 30, eligible_customers: 3373, currency_code: 'GBP',
    personalized_expected_revenue_total_gbp: 100000, historical_rate_forecast_total_gbp: 94000,
    segment_forecast_total_gbp: 104000, historical_minus_personalized_forecast_difference_gbp: -6000,
    segment_minus_personalized_forecast_difference_gbp: 4000, estimated_revenue_exposure_total_gbp: null,
    exposure_coverage: 0.42, exposure_status: 'partial', exposure_method: null,
    opportunity_proxy_total_gbp: 150000, opportunity_proxy_method: 'nonreturn_weighted_conditional_spending',
    opportunity_proxy_interpretation: 'Noncausal prioritisation proxy.', forecast_disagreement: {},
     reliability_evidence_cutoff: '2010-09-10', reliability_group_coverage: 2698,
    history_sufficiency_counts: { sufficient: 1800, limited: 1000, insufficient: 573 },
  };
  const revenueCustomers = { horizon_days: 30, ranking_strategy: 'nonreturn_spending_proxy', items: [revenueItem], total: 1, page: 1, page_size: 12, exposure_status: 'partial' };
  const revenueScatter = { horizon_days: 30, x_axis: 'nonreturn_probability', y_axis: 'conditional_expected_spending_gbp', color_by: 'hist_segment', points: [{ ...revenueItem, exposure_status: 'partial' }], returned_points: 1, eligible_customers: 3373, point_selection: 'sample', interpretation: 'Historical proxy only.' };
  const revenueConcentration = { horizon_days: 30, eligible_customers: 3373, items: [{ metric: 'personalized_expected_revenue', top_customer_share: 0.04, selected_customers: 100, portfolio_total_gbp: 100000, selected_total_gbp: 18000, portfolio_share: 0.18, status: 'available' }], interpretation: 'Concentration is descriptive.' };
  const revenueEvaluation = {
    metadata: {}, financial_definitions: { exposure: 'not estimable where coverage is incomplete' },
    portfolio_by_horizon: {}, forecast_disagreements: {}, revenue_model_test_diagnostics: [],
    revenue_model_history_group_diagnostics: [], concentration: [], ranking_method_comparisons: {},
    validation_selected_strategy_evaluation: {}, ranking_selection_and_test_evaluation: { selected_strategy: 'nonreturn_spending_proxy' },
    validation_cutoffs: {}, hypotheses: {}, limitations: ['Single historical cutoff; no causal estimate.'], timings: {},
  };
  const revenueScenarioResponse = {
    assumptions: { campaign_budget_gbp: 500, contact_cost_gbp: 1.25, assumed_response_probability: 0.18 },
    selected_customer_count: 4, campaign_cost_gbp: 5, budget_remaining_gbp: 495,
    budget_utilization: 0.01, hypothetical_incremental_revenue_gbp: 120,
    hypothetical_incremental_contribution_gbp: null, causal_estimate: false,
    selected_customers: [{
      customer_id: 12345, hist_segment: 'Lapsed / At-Risk', purchase_probability: 0.35,
      conditional_expected_spending_gbp: 100, hypothetical_incremental_revenue_gbp: 2.8,
    }], limitations: ['Hypothetical scenario only.'],
  };
  const trajectorySummary = {
    cutoff_date: '2010-09-10', summary_trajectory_eligible_customers: 3,
    shape_cluster_eligible_customers: 2, total_customers: 12,
    history_sufficiency_counts: { sufficient_for_summary_trajectory: 2, limited_history: 1 },
    clustered_customer_count: 0, unassigned_customer_count: 3, functional_eligible_customers: 1,
    available_trajectory_methods: ['summary_rate_curves'], selected_representation: 'windowed rates',
    model_version: 'trajectory-v1', limitations: ['Historical single-cutoff record.'],
  };
  const trajectoryClusters = { cutoff_date: '2010-09-10', available: false, assignment_coverage: 0, clusters: [], limitations: ['No cluster model is available.'] };
  const trajectoryCustomer = {
    customer_id: 12345, history_sufficiency: 'sufficient_for_summary_trajectory', observed_windows: 4,
    summary_trajectory_eligible: true, shape_cluster_eligible: false,
    shape_cluster_eligibility_status: 'insufficient_observed_windows', functional_eligible: false,
    active_purchase_windows: 2, completed_purchase_gaps: 3, trajectory_cluster_id: null,
    cluster_assignment_status: 'unassigned', functional_analysis_status: 'insufficient_history',
    hist_segment: 'Lapsed / At-Risk', history_length_days: 210, trajectory_cluster_label: null,
  };
  const trajectoryCustomers = { cutoff_date: '2010-09-10', items: [trajectoryCustomer], total: 1, page: 1, page_size: 12, model_version: 'trajectory-v1' };
  const customerTrajectory = {
    customer_id: 12345, cutoff_date: '2010-09-10', history_sufficiency: 'sufficient_for_summary_trajectory',
    summary_trajectory_eligible: true, shape_cluster_eligible: false,
    shape_cluster_eligibility_status: 'insufficient_observed_windows', functional_eligible: false,
    history_support_details: { observed_windows: 4, history_length_days: 210 },
    purchase_rate_trajectory: [{
      window_index: 0, window_start: '2010-03-01', window_end: '2010-03-31', observed_exposure_days: 31,
      purchase_count: 1, gross_revenue: 70, purchase_rate: 0.032, revenue_rate: 2.25,
      window_has_purchase: true, window_observation_status: 'observed',
    }],
    revenue_rate_trajectory: [{
      window_index: 0, window_start: '2010-03-01', window_end: '2010-03-31', observed_exposure_days: 31,
      purchase_count: 1, gross_revenue: 70, purchase_rate: 0.032, revenue_rate: 2.25,
      window_has_purchase: true, window_observation_status: 'observed',
    }],
    trajectory_cluster_id: null, trajectory_cluster_label: null, cluster_assignment_status: 'unassigned',
    functional_component_scores: {}, functional_analysis_status: 'insufficient_history',
    model_version: 'trajectory-v1', limitations: ['Insufficient history for functional analysis.'],
  };
  const trajectoryExplanation = {
    customer_id: 12345, cutoff_date: '2010-09-10', history_sufficiency: 'sufficient_for_summary_trajectory',
    summary_trajectory_eligible: true, shape_cluster_eligible: false,
    shape_cluster_eligibility_status: 'insufficient_observed_windows', functional_eligible: false,
    supported_features: { active_purchase_windows: 2 }, cluster_assignment_status: 'unassigned',
    functional_analysis_status: 'insufficient_history', interpretation: 'Only a short summary trajectory is supported.',
    limitations: ['No functional analysis is reported.'],
  };
  const trajectoryEvaluation = {
    status: 'completed_with_method_specific_availability', model_version: 'trajectory-v1',
    results: {
      cluster_selection: { status: 'shape_model_selected', selected_cluster_count: 2, selected_representation: 'standardized_curve_shape' },
      functional_analysis: {
        status: 'grid_based_pca_fitted_on_train',
        test_evaluation: {
          evaluation_role: 'TEST', component_count: 2,
          train_cumulative_explained_variance: 0.94,
          train_explained_variance_ratio: [0.8, 0.14], test_reconstruction_rmse: 0.02,
          mean_log_curve: [0.1, 0.2], component_shapes: [[0.4, 0.1], [-0.2, 0.3]],
        },
        test_score_points: [{ customer_id: 12345, functional_component_1: 0.5, functional_component_2: -0.2 }],
        score_relationships_with_static_and_behavior_features: [{
          functional_component: 'functional_component_1', existing_feature: 'Recency',
          eligible_customers: 1, spearman_rho: 0.4,
        }],
      },
      predictive_evaluation: {
        models: [{ model: 'trajectory summary', customer_count: 3, roc_auc: 0.67, brier_score: 0.22 }],
        functional_score_model: {
          models: [{ model: 'functional component scores', customer_count: 1, roc_auc: 0.7, brier_score: 0.2 }],
          test_customer_count: 1,
        },
      },
      future_purchase_associations: {
        cluster_associations: {
          horizons: {
            30: { clusters: [{
              trajectory_cluster_id: 1, customer_count: 2, future_purchase_rate: 0.5,
              comparison_future_purchase_rate: 0.3, difference_ci_95: [0.05, 0.1],
              fdr_adjusted_q_value: 0.02,
            }] },
          },
        },
        trajectory_feature_associations: {
          horizons: {
            30: { feature_associations: [{
              feature: 'active_purchase_windows', eligible_customers: 3,
              point_biserial_correlation: 0.4, bootstrap_ci_95: [0.1, 0.6],
              fdr_adjusted_q_value: 0.03,
            }] },
          },
        },
      },
    },
    limitations: ['No future result is an individual guarantee.'],
  };
  const scenarioMutate = vi.fn();
  const comparisonMutate = vi.fn();

  return {
    state,
    customer,
    profile,
    overview,
    segments,
    forecastSummary,
    performance,
    uploadPreview,
    uploadAnalysis,
    behaviorCustomer,
    behaviorSummary,
    behaviorEvaluation,
    behaviorTrajectory,
    reliabilitySummary,
    customerExplanation,
    customerReliability,
    reliabilityCalibration,
    reliabilitySubgroups,
    reliabilityRevenue,
    revenueItem,
    revenueSummary,
    revenueCustomers,
    revenueScatter,
    revenueConcentration,
    revenueEvaluation,
    revenueScenarioResponse,
    trajectorySummary,
    trajectoryClusters,
    trajectoryCustomers,
    customerTrajectory,
    trajectoryExplanation,
    trajectoryEvaluation,
    scenarioMutate,
    comparisonMutate,
    useGetRevenueExposureSummary: vi.fn(() => state(revenueSummary)),
    useGetRevenueExposureCustomers: vi.fn(() => state(revenueCustomers)),
    useGetRevenueExposureScatter: vi.fn(() => state(revenueScatter)),
    useGetRevenueExposureConcentration: vi.fn(() => state(revenueConcentration)),
    useGetRevenueExposureEvaluation: vi.fn(() => state(revenueEvaluation)),
    useGetRevenueExposureCustomer: vi.fn(() => state({ ...revenueItem, limitations: ['Group-level reliability is not an individual guarantee.'] })),
    useGetTrajectorySummary: vi.fn(() => state(trajectorySummary)),
    useGetTrajectoryClusters: vi.fn(() => state(trajectoryClusters)),
    useGetTrajectoryCustomers: vi.fn((_params?: unknown) => state(trajectoryCustomers)),
    useGetTrajectoryEvaluation: vi.fn(() => state(trajectoryEvaluation)),
    useGetCustomerTrajectory: vi.fn(() => state(customerTrajectory)),
    useGetCustomerTrajectoryExplanation: vi.fn(() => state(trajectoryExplanation)),
    useGetResearchSummary: vi.fn(() => state({
      notebook_registry: [
        {
          notebook_id: '01', title: 'Purchase clock', objective: 'Estimate return probabilities.',
          method: 'Saved model evaluation', dataset: 'UCI Online Retail II, Year 1',
          evaluation_horizons_days: [30], population: 'Historical TEST', evaluation_population: 'Historical TEST',
          source_version: 'purchase-clock-v1', source_artifacts: ['notebooks/01_purchase_clock.ipynb'],
          source_fields: ['test_metrics'], source_artifact: 'data/metrics/notebook_evaluation_summary.json',
          source_field: 'purchase_clock.test_metrics', major_findings: ['Personalized evidence is shown.'],
          reproducibility_command: 'python -m jupyter execute notebooks/06.ipynb',
          reproducibility_reference: 'docs/FINAL_REPRODUCIBILITY_GUIDE.md',
          horizons_days: [30], evaluation_population_counts: {}, historical_cutoff: {},
          limitations: ['Historical only.'],
        },
        {
          notebook_id: '11', title: 'Trajectory research', objective: 'Describe historical purchase curves.',
          method: 'Train-fitted summary', dataset: 'UCI Online Retail II, Year 1',
          evaluation_horizons_days: [], population: 'Method-eligible TEST', evaluation_population: 'Method-eligible TEST',
          source_version: 'trajectory-v1', source_artifacts: ['notebooks/11_customer_trajectory.ipynb'],
          source_fields: ['predictive_evaluation'], source_artifact: 'data/metrics/trajectory_analysis_evaluation.json',
          source_field: 'predictive_evaluation', major_findings: ['Trajectory evidence is limited.'],
          reproducibility_command: 'python -m jupyter execute notebooks/11.ipynb',
          reproducibility_reference: 'docs/FINAL_REPRODUCIBILITY_GUIDE.md',
          horizons_days: [30, 60, 90], evaluation_population_counts: {}, historical_cutoff: {},
          limitations: ['No causal claim.'],
        },
      ],
      research_hypotheses: [
        {
          id: 'H1', notebook_id: '01', statement: 'The saved clock has useful discrimination.',
          evidence_status: 'supported', evidence_summary: 'Saved TEST evaluation.', raw_status: 'supported',
          reference_baseline: null, selection_protocol: 'Validation-selected.',
          test_protocol: 'Locked historical TEST.', evaluation_horizons_days: [30],
          cohort_size: 1306, primary_metric: 'average_precision_difference',
          observed_result: 'Saved TEST evaluation.',
          uncertainty_intervals: [{ horizon_days: 30, estimate: 0.01, lower: 0.001, upper: 0.019, level: 0.95 }],
          limitations: ['Historical only.'], source_artifact: 'data/metrics/summary.json', source_field: 'hypothesis_status',
        },
        {
          id: 'H11', notebook_id: '11', statement: 'Trajectory features add incremental value.',
          evidence_status: 'inconclusive', evidence_summary: 'Paired interval includes zero.', raw_status: 'inconclusive',
          reference_baseline: 'Saved Purchase Clock', selection_protocol: 'Selection on validation.',
          test_protocol: 'Locked TEST paired evaluation.', evaluation_horizons_days: [30],
          cohort_size: 1306, primary_metric: 'paired_brier_difference',
          observed_result: 'Paired interval includes zero.', uncertainty_intervals: [],
          limitations: ['Not conditional incremental value.'], source_artifact: 'data/metrics/trajectory.json',
          source_field: 'incremental_value_status',
        },
      ],
      source_manifest: [{ path: 'data/metrics/purchase_clock_test_metrics.json', sha256: '0123456789abcdef0123456789abcdef' }],
      hypothesis_status_counts: { supported: 1, inconclusive: 1 },
      research_scope: {
        dataset: 'UCI Online Retail',
        observed_start: '2009-12-01',
        observed_end: '2011-12-09',
        official_test_cutoff: '2011-11-30',
        test_customer_count: 1306,
        forecast_horizons_days: [30, 60, 90],
      },
      coverage_summary: { trajectory_summary_eligible_test: 1194, trajectory_method_eligibility: { TEST: 659 }, trajectory: { official_test_customers: 1306 } },
      purchase_clock_evaluation: { test_metrics: [] },
      spending_forecast_evaluation: { test_metrics: [] },
      behavior_evaluation: { policy_status: 'research_only', candidate_f_status: 'Candidate threshold is not a validated policy.' },
      reliability_evaluation: { purchase_calibration: [] },
      revenue_exposure_evaluation: { scenario_sensitivity: { interpretation: 'Hypothetical assumptions only.' } },
      trajectory_evaluation: {
        cluster_selection: { status: 'descriptive_only', selection_rule: 'Held-out fit was not used for selection.' },
        functional_analysis: { status: 'evaluated', method: 'TRAIN-fitted representation', test_evaluation: { evaluated_curves: 659 } },
      },
      additional_research_questions: { incremental_predictive_value: { evidence_status: 'inconclusive', interpretation: 'Incremental value remains uncertain.' } },
      financial_definitions: {
        reference_exposure_status: 'not_estimable',
        reference_exposure_reason: 'No supported reference-based exposure value is saved.',
        expected_revenue: 'Purchase probability multiplied by conditional expected spending.',
        opportunity_proxy: 'Nonreturn-weighted conditional spending; not recoverable revenue.',
      },
      limitations: ['Saved historical aggregate evaluation only.'],
    })),
    usePostRetentionScenario: vi.fn(() => ({ isPending: false, isSuccess: false, isError: false, data: undefined as typeof revenueScenarioResponse | undefined, mutate: scenarioMutate, reset: vi.fn() })),
    usePostRetentionStrategyComparison: vi.fn(() => ({ isPending: false, isSuccess: false, isError: false, data: undefined, mutate: comparisonMutate, reset: vi.fn() })),
    useHealthCheck: vi.fn(() => state({ status: 'ok' })),
    useGetApiHealth: vi.fn(() => state({ status: 'ok' })),
    useGetOverview: vi.fn(() => state(overview)),
    useGetSegments: vi.fn(() => state(segments)),
    useGetCustomers: vi.fn((_params?: unknown) =>
      state({ items: [customer], total: 1, page: 1, page_size: 25 }),
    ),
    useGetCustomer: vi.fn(() => state(profile)),
    useGetCustomerHistory: vi.fn(() =>
      state([
        {
          invoice: '90001',
          purchase_date: '2010-08-01T00:00:00',
          gross_revenue: 70,
        },
      ]),
    ),
    useGetBehaviorSummary: vi.fn(() => state(behaviorSummary)),
    useGetBehaviorCustomers: vi.fn((_params?: unknown, _options?: unknown) => state({ items: [behaviorCustomer], total: 1, page: 1, page_size: 10 })),
    useGetBehaviorEvaluation: vi.fn(() => state(behaviorEvaluation)),
    useGetCustomerBehavior: vi.fn(() => state({ ...behaviorCustomer, alert_reasons: [], indicator_explanations: ['The recent order rate is above the reference window.'] })),
    useGetCustomerBehaviorTrajectory: vi.fn(() => state(behaviorTrajectory)),
    useGetCustomerForecast: vi.fn(() => state(profile)),
    useGetForecastSummary: vi.fn(() => state(forecastSummary)),
    useGetModelPerformance: vi.fn(() => state(performance)),
    useGetReliabilitySummary: vi.fn(() => state(reliabilitySummary)),
    useGetReliabilityCalibration: vi.fn(() => state(reliabilityCalibration)),
    useGetReliabilitySubgroups: vi.fn(() => state(reliabilitySubgroups)),
    useGetReliabilityRevenue: vi.fn(() => state(reliabilityRevenue)),
    useGetCustomerExplanation: vi.fn(() => state(customerExplanation)),
    useGetCustomerReliability: vi.fn(() => state(customerReliability)),
    useGetCalibrationImage: vi.fn(() =>
      state({ url: performance.calibration_image_url }),
    ),
    useGetCalibration90dImage: vi.fn(() =>
      state({ url: performance.calibration_90d_image_url }),
    ),
    usePreviewUpload: vi.fn((options?: { mutation?: { onSuccess?: (data: unknown) => void } }) => ({
      isPending: false,
      isError: false,
      mutate: vi.fn(() => options?.mutation?.onSuccess?.(uploadPreview)),
    })),
    useAnalyzeUpload: vi.fn((options?: { mutation?: { onSuccess?: (data: unknown) => void } }) => ({
      isPending: false,
      isError: false,
      mutate: vi.fn(() => options?.mutation?.onSuccess?.(uploadAnalysis)),
    })),
    useExportUpload: vi.fn(() => ({ isPending: false, mutate: vi.fn() })),
    getGetApiHealthQueryKey: vi.fn(() => ['health']),
    getHealthCheckQueryKey: vi.fn(() => ['healthz']),
    getGetCalibration90dImageQueryKey: vi.fn(() => ['calibration-90d']),
    getGetCalibrationImageQueryKey: vi.fn(() => ['calibration']),
    getGetCustomerForecastQueryKey: vi.fn(() => ['customer-forecast']),
    getGetCustomerHistoryQueryKey: vi.fn(() => ['customer-history']),
    getGetBehaviorSummaryQueryKey: vi.fn(() => ['behavior-summary']),
    getGetBehaviorCustomersQueryKey: vi.fn((params?: unknown) => ['behavior-customers', params]),
    getGetBehaviorEvaluationQueryKey: vi.fn(() => ['behavior-evaluation']),
    getGetCustomerBehaviorQueryKey: vi.fn((id?: number) => ['customer-behavior', id]),
    getGetCustomerBehaviorTrajectoryQueryKey: vi.fn((id?: number) => ['customer-behavior-trajectory', id]),
    getGetCustomerQueryKey: vi.fn(() => ['customer']),
    getGetCustomersQueryKey: vi.fn(() => ['customers']),
    getGetForecastSummaryQueryKey: vi.fn(() => ['forecast-summary']),
    getGetModelPerformanceQueryKey: vi.fn(() => ['model-performance']),
    getGetReliabilitySummaryQueryKey: vi.fn(() => ['reliability-summary']),
    getGetReliabilityCalibrationQueryKey: vi.fn(() => ['reliability-calibration']),
    getGetReliabilitySubgroupsQueryKey: vi.fn((params?: unknown) => ['reliability-subgroups', params]),
    getGetReliabilityRevenueQueryKey: vi.fn(() => ['reliability-revenue']),
    getGetCustomerExplanationQueryKey: vi.fn((id?: number, params?: unknown) => ['customer-explanation', id, params]),
    getGetCustomerReliabilityQueryKey: vi.fn((id?: number, params?: unknown) => ['customer-reliability', id, params]),
    getGetOverviewQueryKey: vi.fn(() => ['overview']),
    getGetSegmentsQueryKey: vi.fn(() => ['segments']),
    getGetRevenueExposureSummaryQueryKey: vi.fn((params?: unknown) => ['revenue-summary', params]),
    getGetRevenueExposureCustomersQueryKey: vi.fn((params?: unknown) => ['revenue-customers', params]),
    getGetRevenueExposureScatterQueryKey: vi.fn((params?: unknown) => ['revenue-scatter', params]),
    getGetRevenueExposureConcentrationQueryKey: vi.fn((params?: unknown) => ['revenue-concentration', params]),
    getGetRevenueExposureEvaluationQueryKey: vi.fn(() => ['revenue-evaluation']),
    getGetRevenueExposureCustomerQueryKey: vi.fn((id?: number, params?: unknown) => ['revenue-customer', id, params]),
    getGetTrajectorySummaryQueryKey: vi.fn(() => ['trajectory-summary']),
    getGetTrajectoryClustersQueryKey: vi.fn(() => ['trajectory-clusters']),
    getGetTrajectoryCustomersQueryKey: vi.fn((params?: unknown) => ['trajectory-customers', params]),
    getGetTrajectoryEvaluationQueryKey: vi.fn(() => ['trajectory-evaluation']),
    getGetCustomerTrajectoryQueryKey: vi.fn((id?: number) => ['customer-trajectory', id]),
    getGetCustomerTrajectoryExplanationQueryKey: vi.fn((id?: number) => ['customer-trajectory-explanation', id]),
  };
});

vi.mock('@workspace/api-client-react', () => mocks);

async function renderAt(path: string) {
  const headings: Record<string, string> = {
    '/': 'Business overview',
    '/research': 'Research overview',
    '/segments': 'Segments',
    '/intelligence': 'Customer intelligence',
    '/behavior': 'Behavior indicators',
    '/forecasting': 'Forecast workspace',
    '/upload': 'Upload analysis',
    '/model-performance': 'Model performance',
    '/revenue-exposure': 'Revenue exposure & retention planning',
    '/trajectories': 'Customer trajectory explorer',
  };
  window.history.replaceState({}, '', path);
  const result = render(<App />);
  await screen.findByRole('heading', { name: headings[path] }, { timeout: 5000 });
  return result;
}

describe('OELP customer intelligence pages', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/');
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it.each([
    ['/', 'Business overview'],
    ['/segments', 'Segments'],
    ['/intelligence', 'Customer intelligence'],
    ['/research', 'Research overview'],
    ['/behavior', 'Behavior indicators'],
    ['/forecasting', 'Forecast workspace'],
    ['/upload', 'Upload analysis'],
    ['/model-performance', 'Model performance'],
    ['/revenue-exposure', 'Revenue exposure & retention planning'],
    ['/trajectories', 'Customer trajectory explorer'],
  ])('renders %s with live-data page heading', async (path, heading) => {
    await renderAt(path);
    expect(screen.getByRole('heading', { name: heading })).toBeInTheDocument();
    if (path === '/upload') {
      expect(screen.getByText(/Descriptive only/i)).toBeInTheDocument();
    } else if (path === '/research') {
      expect(screen.getByText(/Historical research only/i)).toBeInTheDocument();
    } else if (path === '/revenue-exposure') {
      expect(screen.getByTestId('disclosure-noncausal')).toHaveTextContent(/noncausal/i);
    } else {
      expect(screen.getByText(/Historical demonstration only/i)).toBeInTheDocument();
    }
  });

  it('renders and filters the evidence-linked research synthesis', async () => {
    const user = userEvent.setup();
    await renderAt('/research');

    expect(screen.getByText('The saved clock has useful discrimination.')).toBeInTheDocument();
    expect(screen.getByText('Trajectory features add incremental value.')).toBeInTheDocument();
    expect(screen.getByText('Reference-based exposure')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Final evaluation' })).toHaveAttribute(
      'href',
      'https://github.com/Punit-IITPKD/OELP_project/blob/main/docs/FINAL_RESEARCH_EVALUATION.md',
    );

    await user.selectOptions(screen.getByLabelText('Filter evidence'), 'inconclusive');
    expect(screen.getByText('Trajectory features add incremental value.')).toBeInTheDocument();
    expect(screen.queryByText('The saved clock has useful discrimination.')).not.toBeInTheDocument();

    await user.type(screen.getByLabelText('Find a notebook'), 'Trajectory research');
    expect(screen.getByRole('heading', { name: 'Trajectory research' })).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Purchase clock' })).not.toBeInTheDocument();
  });

  it('uses durable main-branch references for production research sources', async () => {
    await renderAt('/research');

    const repoBlobPrefix = 'https://github.com/Punit-IITPKD/OELP_project/blob/main/';
    const researchLinks = screen.getAllByRole('link')
      .map((link) => link.getAttribute('href') ?? '')
      .filter((href) => href.includes('/blob/'));

    expect(researchLinks.length).toBeGreaterThan(0);
    expect(researchLinks.every((href) => href.startsWith(repoBlobPrefix))).toBe(true);
    expect(researchLinks.some((href) => href.endsWith('/notebooks/11_customer_trajectory.ipynb'))).toBe(true);
    expect(researchLinks.some((href) => href.endsWith('/docs/CUSTOMER_TRAJECTORY_ANALYSIS.md'))).toBe(true);
    expect(researchLinks.some((href) => href.endsWith('/docs/FINAL_RESEARCH_EVALUATION.md'))).toBe(true);
    expect(researchLinks.some((href) => href.endsWith('/docs/FINAL_REPRODUCIBILITY_GUIDE.md'))).toBe(true);
    expect(researchLinks.some((href) => href.endsWith('/data/metrics/purchase_clock_test_metrics.json'))).toBe(true);
    expect(researchLinks.some((href) => href.includes('feat/phase7-final-research-integration'))).toBe(false);
  });

  it('searches, filters, inspects and exports historical trajectory records', async () => {
    const user = userEvent.setup();
    const createObjectUrl = vi.fn(() => 'blob:trajectory');
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: createObjectUrl });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    await renderAt('/trajectories');

    expect(screen.getByTestId('state-clusters-unavailable')).toHaveTextContent(/No cluster fit is inferred/i);
    expect(screen.getByText('Summary trajectory eligible')).toBeInTheDocument();
    expect(screen.getByText('Shape-cluster eligible')).toBeInTheDocument();
    expect(screen.getByText('Cluster assignments')).toBeInTheDocument();
    expect(screen.getAllByText('FDA eligible')).toHaveLength(2);
    expect(screen.getByText('TRAIN explained variance summarized')).toBeInTheDocument();
    expect(screen.getByText('TEST reconstruction RMSE')).toBeInTheDocument();
    expect(mocks.useGetTrajectorySummary).toHaveBeenCalledWith(expect.objectContaining({
      query: expect.objectContaining({ queryKey: ['trajectory-summary'] }),
    }));
    await user.type(screen.getByTestId('input-trajectory-search'), '12345');
    await user.click(screen.getByRole('button', { name: 'Search' }));
    expect(mocks.useGetTrajectoryCustomers).toHaveBeenLastCalledWith(expect.objectContaining({
      search: '12345', page: 1, page_size: 12,
    }), expect.objectContaining({ query: expect.objectContaining({ queryKey: expect.any(Array) }) }));

    await user.selectOptions(screen.getByTestId('select-trajectory-sufficiency'), 'limited_history');
    expect(mocks.useGetTrajectoryCustomers).toHaveBeenLastCalledWith(expect.objectContaining({
      search: '12345', history_sufficiency: 'limited_history',
    }), expect.objectContaining({ query: expect.objectContaining({ queryKey: expect.any(Array) }) }));
    await user.click(screen.getByTestId('button-open-trajectory-12345'));
    expect(await screen.findByTestId('panel-customer-trajectory')).toHaveTextContent('Observed rate by history window');
    expect(screen.getByTestId('panel-customer-trajectory')).toHaveTextContent(/Insufficient history for functional analysis/i);
    expect(screen.getByTestId('panel-customer-trajectory')).toHaveTextContent('Shape-cluster eligibility');
    expect(mocks.useGetCustomerTrajectory).toHaveBeenLastCalledWith(12345, expect.objectContaining({
      query: expect.objectContaining({ enabled: true, queryKey: ['customer-trajectory', 12345] }),
    }));
    await user.click(screen.getByTestId('button-load-trajectory-explanation'));
    expect(await screen.findByText(/Only a short summary trajectory is supported/i)).toBeInTheDocument();
    expect(mocks.useGetCustomerTrajectoryExplanation).toHaveBeenLastCalledWith(12345, expect.objectContaining({
      query: expect.objectContaining({ enabled: true, queryKey: ['customer-trajectory-explanation', 12345] }),
    }));
    await user.click(screen.getByTestId('button-export-trajectory-csv'));
    expect(createObjectUrl).toHaveBeenCalledOnce();
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
  });

  it('renders functional curve summaries and same-cohort prediction results', async () => {
    await renderAt('/trajectories');
    expect(screen.getByText('Functional curve representation')).toBeInTheDocument();
    expect(screen.getByText('PC1 vs PC2', { exact: false })).toBeInTheDocument();
    expect(screen.getByText(/trajectory summary · 3 customers/i)).toBeInTheDocument();
    expect(screen.getByText(/functional component scores · 1 customers/i)).toBeInTheDocument();
    expect(screen.getByText(/Functional scores and existing features/i)).toBeInTheDocument();
    expect(screen.getByText('Retrospective purchase associations')).toBeInTheDocument();
    expect(screen.getByText('active purchase windows')).toBeInTheDocument();
    expect(screen.getAllByText('30 days')).toHaveLength(2);
  });

  it('links a customer intelligence profile into its historical trajectory', async () => {
    const user = userEvent.setup();
    await renderAt('/intelligence');
    await user.type(screen.getByTestId('input-customer-id'), '12345');
    await user.click(screen.getByTestId('button-search-customer'));
    await user.click(await screen.findByTestId('button-open-customer-12345'));
    const link = await screen.findByTestId('link-customer-trajectory');
    expect(link).toHaveAttribute('href', '/trajectories?customer_id=12345');
    await user.click(link);
    expect(await screen.findByTestId('panel-customer-trajectory')).toHaveTextContent('Customer 12345');
    expect(mocks.useGetCustomerTrajectory).toHaveBeenLastCalledWith(12345, expect.objectContaining({
      query: expect.objectContaining({ enabled: true, queryKey: ['customer-trajectory', 12345] }),
    }));
  });

  it('offers reachable navigation and queries revenue data with API filters and complete query keys', async () => {
    const user = userEvent.setup();
    await renderAt('/');
    await user.click(screen.getByTestId('link-revenue-exposure'));
    expect(await screen.findByRole('heading', { name: 'Revenue exposure & retention planning' })).toBeInTheDocument();
    expect(screen.getByText('Not estimable', { selector: '.exposure-metric strong' })).toBeInTheDocument();
    expect(screen.getByTestId('disclosure-noncausal')).toHaveTextContent(/noncausal/i);
    expect(mocks.useGetRevenueExposureSummary).toHaveBeenCalledWith({ horizon_days: 30 }, expect.objectContaining({
      query: expect.objectContaining({ queryKey: ['revenue-summary', { horizon_days: 30 }] }),
    }));
    expect(mocks.useGetRevenueExposureCustomers).toHaveBeenCalledWith(expect.objectContaining({
      horizon_days: 30, page: 1, page_size: 12, ranking_strategy: 'nonreturn_spending_proxy',
    }), expect.objectContaining({ query: expect.objectContaining({ queryKey: expect.any(Array) }) }));
    expect(mocks.useGetRevenueExposureScatter).toHaveBeenCalledWith({ horizon_days: 30, limit: 300 }, expect.objectContaining({
      query: expect.objectContaining({ queryKey: ['revenue-scatter', { horizon_days: 30, limit: 300 }] }),
    }));
    expect(mocks.useGetRevenueExposureConcentration).toHaveBeenCalledWith({ horizon_days: 30 }, expect.objectContaining({
      query: expect.objectContaining({ queryKey: ['revenue-concentration', { horizon_days: 30 }] }),
    }));
    expect(mocks.useGetRevenueExposureEvaluation).toHaveBeenCalledWith(expect.objectContaining({
      query: expect.objectContaining({ queryKey: ['revenue-evaluation'] }),
    }));
    await user.click(screen.getByTestId('button-exposure-detail-12345'));
    expect(screen.getByTestId('panel-exposure-detail')).toHaveTextContent('Eligible under active filters');
    expect(mocks.useGetRevenueExposureCustomer).toHaveBeenLastCalledWith(12345, { horizon_days: 30 }, expect.objectContaining({
      query: expect.objectContaining({ enabled: true, queryKey: ['revenue-customer', 12345, { horizon_days: 30 }] }),
    }));
  });

  it('passes horizon, ranking and eligibility filters to the customer ranking API', async () => {
    const user = userEvent.setup();
    await renderAt('/revenue-exposure');
    await user.selectOptions(screen.getByTestId('select-exposure-horizon'), '90');
    await user.selectOptions(screen.getByTestId('select-exposure-ranking'), 'pareto_risk_value');
    await user.selectOptions(screen.getByTestId('select-exposure-sufficiency'), 'sufficient');
    await user.selectOptions(screen.getByTestId('select-exposure-history-group'), 'Five or more purchases');
    await user.type(screen.getByTestId('input-exposure-segment'), 'Lapsed');
    await user.selectOptions(screen.getByTestId('select-exposure-behavior'), 'declining_purchase_rate');
    await user.click(screen.getByTestId('check-exposure-sufficient-behavior'));
    expect(mocks.useGetRevenueExposureCustomers).toHaveBeenLastCalledWith(expect.objectContaining({
      horizon_days: 90, page: 1, ranking_strategy: 'pareto_risk_value',
      history_sufficiency: 'sufficient', history_group: 'Five or more purchases',
      hist_segment: 'Lapsed', behavior_filter: 'declining_purchase_rate',
      require_sufficient_behavior_history: true,
    }), expect.objectContaining({ query: expect.objectContaining({ queryKey: expect.any(Array) }) }));
    await user.type(screen.getByTestId('input-exposure-search'), '12345');
    await user.selectOptions(screen.getByTestId('select-exposure-sort'), 'purchase_probability');
    await user.click(screen.getByTestId('button-exposure-sort-direction'));
    expect(mocks.useGetRevenueExposureCustomers).toHaveBeenLastCalledWith(expect.objectContaining({
      search: '12345', sort_by: 'purchase_probability', sort_descending: true,
    }), expect.objectContaining({ query: expect.objectContaining({ queryKey: expect.any(Array) }) }));
  });

  it('exports the visible ranked customer page as CSV', async () => {
    const user = userEvent.setup();
    const createObjectUrl = vi.fn((_blob: Blob) => 'blob:revenue');
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: createObjectUrl });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    await renderAt('/revenue-exposure');
    await user.click(screen.getByTestId('button-export-exposure-csv'));
    expect(createObjectUrl).toHaveBeenCalledOnce();
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
  });

  it('submits hypothetical scenario assumptions and strategy-comparison request without causal claims', async () => {
    const user = userEvent.setup();
    await renderAt('/revenue-exposure');
    await user.type(screen.getByTestId('input-scenario-budget'), '750');
    await user.type(screen.getByTestId('input-scenario-contact-cost'), '1.25');
    await user.type(screen.getByTestId('input-scenario-maximum-contacts'), '400');
    await user.type(screen.getByTestId('input-scenario-response'), '0.18');
    await user.type(screen.getByTestId('input-scenario-uplift'), '0.08');
    await user.type(screen.getByTestId('input-scenario-margin'), '0.35');
    await user.click(screen.getByTestId('button-submit-scenario'));
    expect(mocks.scenarioMutate).toHaveBeenCalledWith({ data: expect.objectContaining({
      horizon_days: 30, campaign_budget_gbp: 750, contact_cost_gbp: 1.25,
      maximum_contacts: 400, assumed_response_probability: 0.18,
      assumed_purchase_uplift_if_responded: 0.08, assumed_gross_margin_rate: 0.35,
      ranking_strategy: 'nonreturn_spending_proxy',
    }) });
    await user.click(screen.getByTestId('check-scenario-compare'));
    await user.click(screen.getByTestId('button-submit-scenario'));
    expect(mocks.comparisonMutate).toHaveBeenCalledWith({ data: expect.objectContaining({
      scenario: expect.objectContaining({ campaign_budget_gbp: 750, horizon_days: 30 }),
      ranking_strategies: expect.arrayContaining(['historical_gross_spending', 'pareto_risk_value']),
    }) });
    expect(screen.getByTestId('disclosure-scenario-noncausal')).toHaveTextContent(/not causal retention lift/i);
  });

  it('shows the returned contact list and the exact assumptions behind a scenario', async () => {
    const user = userEvent.setup();
    mocks.usePostRetentionScenario.mockImplementation(() => ({
      isPending: false,
      isSuccess: true,
      isError: false,
      data: mocks.revenueScenarioResponse,
      mutate: mocks.scenarioMutate,
      reset: vi.fn(),
    }));
    await renderAt('/revenue-exposure');
    expect(screen.getByTestId('table-scenario-contacts')).toBeInTheDocument();
    expect(screen.getByTestId('row-scenario-contact-12345')).toHaveTextContent('£3');
    await user.click(screen.getByText('Assumptions used'));
    expect(screen.getByText('campaign budget gbp')).toBeInTheDocument();
    expect(screen.getByText('500')).toBeInTheDocument();
  });

  it('integrates the same cutoff customer profile with the revenue planner', async () => {
    const user = userEvent.setup();
    await renderAt('/intelligence');
    await user.type(screen.getByTestId('input-customer-id'), '12345');
    await user.click(screen.getByTestId('button-search-customer'));
    await user.click(await screen.findByTestId('button-open-customer-12345'));
    expect(await screen.findByTestId('section-customer-revenue-exposure')).toBeInTheDocument();
    await user.selectOptions(screen.getByTestId('select-customer-revenue-horizon'), '90');
    const plannerLink = screen.getByTestId('link-customer-revenue-planner');
    expect(plannerLink).toHaveAttribute('href', '/revenue-exposure?customer_id=12345&horizon_days=90');
    await user.click(plannerLink);
    expect(await screen.findByTestId('select-exposure-horizon')).toHaveValue('90');
    expect(screen.getByTestId('input-exposure-search')).toHaveValue('12345');
  });

  it('shows a paginated segment customer table and exports its visible page', async () => {
    await renderAt('/segments');
    expect(screen.getByText('Customer records')).toBeInTheDocument();
    expect(screen.getByText('12345')).toBeInTheDocument();
    expect(screen.getByText('Full-period retrospective RFM')).toBeInTheDocument();
    expect(screen.getByTestId('button-export-segment-customers')).toBeEnabled();
  });

  it('navigates to the behavior workspace from primary navigation and renders real query data', async () => {
    const user = userEvent.setup();
    await renderAt('/');
    await user.click(screen.getByTestId('link-behavior'));
    expect(await screen.findByRole('heading', { name: 'Behavior indicators' })).toBeInTheDocument();
    expect(screen.getByText('3,373')).toBeInTheDocument();
    expect(screen.getAllByText('Candidate F').length).toBeGreaterThan(0);
    expect(mocks.useGetBehaviorSummary).toHaveBeenCalled();
    expect(mocks.useGetBehaviorEvaluation).toHaveBeenCalled();
  });

  it('sends behavior cohort filters and sort options to the API and exports visible rows', async () => {
    const user = userEvent.setup();
    const createObjectUrl = vi.fn((_blob: Blob) => 'blob:behavior');
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: createObjectUrl });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    await renderAt('/behavior');
    await user.type(screen.getByTestId('input-behavior-search'), '12345');
    await user.type(screen.getByTestId('input-behavior-segment'), 'Lapsed');
    await user.type(screen.getByTestId('input-behavior-history-group'), 'Five or more');
    await user.selectOptions(screen.getByTestId('select-behavior-sufficiency'), 'sufficient');
    await user.selectOptions(screen.getByTestId('select-behavior-sort'), 'gap_deviation_score');
    const call = mocks.useGetBehaviorCustomers.mock.calls.at(-1);
    expect(call?.[0]).toMatchObject({ search: '12345', hist_segment: 'Lapsed', history_group: 'Five or more', history_sufficiency: 'sufficient', sort_by: 'gap_deviation_score' });
    await user.click(screen.getByTestId('button-export-behavior-csv'));
    expect(createObjectUrl).toHaveBeenCalledTimes(1);
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
    expect(await (createObjectUrl.mock.calls[0][0] as Blob).text()).toContain('current_elapsed_gap_days');
  });

  it('sends historical cohort and purchase-history filters to the customer API', async () => {
    const user = userEvent.setup();
    await renderAt('/segments');
    await user.selectOptions(
      screen.getByTestId('select-historical-cohort'),
      'Lapsed / At-Risk',
    );
    await user.selectOptions(
      screen.getByTestId('select-history-group'),
      'Five or more purchases',
    );
    const lastCall = mocks.useGetCustomers.mock.calls.at(-1);
    expect(lastCall?.[0]).toMatchObject({
      hist_segment: 'Lapsed / At-Risk',
      history_group: 'Five or more purchases',
    });
  });

  it('renders saved purchase-history group labels in model diagnostics', async () => {
    await renderAt('/model-performance');
    expect(screen.getByText('Exactly one purchase')).toBeInTheDocument();
    expect(screen.queryByText('NaN')).not.toBeInTheDocument();
  });

  it('loads customer explanation only on request and discloses noncausal sensitivities', async () => {
    const user = userEvent.setup();
    await renderAt('/intelligence');
    await user.type(screen.getByTestId('input-customer-id'), '12345');
    await user.click(screen.getByTestId('button-search-customer'));
    await user.click(await screen.findByTestId('button-open-customer-12345'));
    expect(await screen.findByTestId('button-load-customer-explanation')).toBeInTheDocument();
    expect(mocks.useGetCustomerExplanation).toHaveBeenLastCalledWith(12345, { horizon_days: 30 }, expect.objectContaining({
      query: expect.objectContaining({ enabled: false, queryKey: ['customer-explanation', 12345, { horizon_days: 30 }] }),
    }));
    await user.click(screen.getByTestId('button-load-customer-explanation'));
    expect(await screen.findByText('Feature substitutions')).toBeInTheDocument();
    expect(screen.getAllByText(/noncausal model-input sensitivities/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/35\.0% purchase probability/)).toBeInTheDocument();
    expect(mocks.useGetCustomerExplanation).toHaveBeenLastCalledWith(12345, { horizon_days: 30 }, expect.objectContaining({
      query: expect.objectContaining({ enabled: true }),
    }));
  });

  it('shows TEST sample and cutoff disclosures in calibration reliability tab', async () => {
    const user = userEvent.setup();
    await renderAt('/model-performance');
    await user.click(screen.getByTestId('tab-performance-calibration'));
    expect(await screen.findByText(/3,373 TEST customers/i)).toBeInTheDocument();
    expect(screen.getByText(/Calibration describes aggregate historical behavior/i)).toBeInTheDocument();
    expect(screen.getByText(/Calibration summary/)).toBeInTheDocument();
    expect(mocks.useGetReliabilitySummary).toHaveBeenLastCalledWith(expect.objectContaining({
      query: expect.objectContaining({ enabled: true }),
    }));
    await user.click(screen.getByTestId('tab-performance-subgroups'));
    expect(await screen.findByText(/No supported subgroup rows were returned/i)).toBeInTheDocument();
  });

  it('labels full-period profile values as retrospective rather than forecast inputs', async () => {
    const user = userEvent.setup();
    await renderAt('/intelligence');
    await user.type(screen.getByTestId('input-customer-id'), '12345');
    await user.click(screen.getByTestId('button-search-customer'));
    await user.click(await screen.findByTestId('button-open-customer-12345'));
    expect(
      await screen.findByText('Retrospective full-period description'),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/may include data after the forecast cutoff and are not model inputs/i),
    ).toBeInTheDocument();
    expect(screen.getByText('Personalized expected gap')).toBeInTheDocument();
    expect(screen.getByTestId('section-behavior-history')).toBeInTheDocument();
    expect(screen.getByTestId('copy-no-alert-policy')).toHaveTextContent(/not churn alerts or live recommendations/i);
    expect(mocks.useGetCustomerBehavior).toHaveBeenCalledWith(12345, expect.objectContaining({
      query: expect.objectContaining({ enabled: true, queryKey: ['customer-behavior', 12345] }),
    }));
  });

  it('exports a selected customer forecast from saved API values', async () => {
    const user = userEvent.setup();
    const createObjectUrl = vi.fn((_blob: Blob) => 'blob:test');
    Object.defineProperty(URL, 'createObjectURL', {
      configurable: true,
      value: createObjectUrl,
    });
    Object.defineProperty(URL, 'revokeObjectURL', {
      configurable: true,
      value: vi.fn(),
    });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});

    await renderAt('/intelligence');
    await user.type(screen.getByTestId('input-customer-id'), '12345');
    await user.click(screen.getByTestId('button-search-customer'));
    await user.click(await screen.findByTestId('button-open-customer-12345'));
    const exportButton = await screen.findByTestId(
      'button-export-customer-forecast',
    );
    await user.click(exportButton);

    expect(createObjectUrl).toHaveBeenCalledTimes(1);
    const blob = createObjectUrl.mock.calls[0][0] as Blob;
    expect(await blob.text()).toContain('0.35');
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled();
  });

  it('filters visible forecast models and updates the comparison table', async () => {
    const user = userEvent.setup();
    await renderAt('/forecasting');

    const globalModel = screen.getByTestId('input-model-global');
    expect(globalModel).toBeChecked();
    await user.click(globalModel);
    expect(globalModel).not.toBeChecked();
    expect(screen.queryByRole('columnheader', { name: 'Global probability' }))
      .not.toBeInTheDocument();
    expect(
      screen.getByRole('columnheader', { name: 'Personalized probability' }),
    ).toBeInTheDocument();
  });

  it('previews and analyzes an upload without invoking forecast endpoints', async () => {
    const user = userEvent.setup();
    await renderAt('/upload');
    const file = new File(
      ['Invoice,StockCode,Description,Quantity,InvoiceDate,Price,Customer ID,Country'],
      'retail.csv',
      { type: 'text/csv' },
    );
    await user.upload(screen.getByTestId('input-upload-file'), file);
    expect(await screen.findByText(/2 rows · 8 columns/)).toBeInTheDocument();
    await user.click(screen.getByTestId('button-analyze-upload'));
    expect(await screen.findByText('Cleaned rows')).toBeInTheDocument();
    expect(screen.getByText('Recency (days)')).toBeInTheDocument();
    expect(mocks.useAnalyzeUpload).toHaveBeenCalled();
    expect(mocks.useGetCustomerForecast).not.toHaveBeenCalled();
  });
});
