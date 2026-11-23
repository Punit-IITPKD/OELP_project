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
    model_comparison: [{ horizon_days: 30, model: 'Candidate F', n_customers: 120, roc_auc: 0.61, average_precision: 0.22, precision_at_budget: 0.31, recall_at_budget: 0.18, brier_score: 0.19, log_loss: 0.57, alert_coverage: null, false_alert_rate: null, threshold: null, status: 'exploratory' }],
    bootstrap_comparisons: [{ horizon_days: 30, comparison: 'Candidate F vs baseline', metric: 'ROC AUC', difference_first_minus_second: 0.04, confidence_interval_95_lower: -0.02, confidence_interval_95_upper: 0.1, valid_resamples: 900, requested_resamples: 1000, customer_clusters: 120 }],
    hypotheses: [{ hypothesis: 'H1', statement: 'Recent purchase rhythm adds evidence.', status: 'inconclusive', evidence_summary: 'Interval includes no difference.' }],
    limitations: ['Historical single-cutoff evaluation; external validation is required.'],
  };
  const behaviorTrajectory = {
    customer_id: 12345, cutoff_date: '2010-09-10', window_days: 180, policy_version: 'notebook08-v1',
    items: [{ period_start: '2010-06-01', period_end: '2010-06-30', order_count: 1, gross_revenue: 70, observed_exposure_days: 30, order_rate: 0.033, revenue_rate: 2.33 }],
  };

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
    useGetBehaviorCustomers: vi.fn(() => state({ items: [behaviorCustomer], total: 1, page: 1, page_size: 10 })),
    useGetBehaviorEvaluation: vi.fn(() => state(behaviorEvaluation)),
    useGetCustomerBehavior: vi.fn(() => state({ ...behaviorCustomer, alert_reasons: [], indicator_explanations: ['The recent order rate is above the reference window.'] })),
    useGetCustomerBehaviorTrajectory: vi.fn(() => state(behaviorTrajectory)),
    useGetCustomerForecast: vi.fn(() => state(profile)),
    useGetForecastSummary: vi.fn(() => state(forecastSummary)),
    useGetModelPerformance: vi.fn(() => state(performance)),
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
    getGetOverviewQueryKey: vi.fn(() => ['overview']),
    getGetSegmentsQueryKey: vi.fn(() => ['segments']),
  };
});

vi.mock('@workspace/api-client-react', () => mocks);

function renderAt(path: string) {
  window.history.replaceState({}, '', path);
  return render(<App />);
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
    ['/behavior', 'Behavior indicators'],
    ['/forecasting', 'Forecast workspace'],
    ['/upload', 'Upload analysis'],
    ['/model-performance', 'Model performance'],
  ])('renders %s with live-data page heading', (path, heading) => {
    renderAt(path);
    expect(screen.getByRole('heading', { name: heading })).toBeInTheDocument();
    if (path === '/upload') {
      expect(screen.getByText(/Descriptive only/i)).toBeInTheDocument();
    } else {
      expect(screen.getByText(/Historical demonstration only/i)).toBeInTheDocument();
    }
  });

  it('shows a paginated segment customer table and exports its visible page', () => {
    renderAt('/segments');
    expect(screen.getByText('Customer records')).toBeInTheDocument();
    expect(screen.getByText('12345')).toBeInTheDocument();
    expect(screen.getByText('Full-period retrospective RFM')).toBeInTheDocument();
    expect(screen.getByTestId('button-export-segment-customers')).toBeEnabled();
  });

  it('navigates to the behavior workspace from primary navigation and renders real query data', async () => {
    const user = userEvent.setup();
    renderAt('/');
    await user.click(screen.getByTestId('link-behavior'));
    expect(await screen.findByRole('heading', { name: 'Behavior indicators' })).toBeInTheDocument();
    expect(screen.getByText('3,373')).toBeInTheDocument();
    expect(screen.getByText('Candidate F')).toBeInTheDocument();
    expect(mocks.useGetBehaviorSummary).toHaveBeenCalled();
    expect(mocks.useGetBehaviorEvaluation).toHaveBeenCalled();
  });

  it('sends behavior cohort filters and sort options to the API and exports visible rows', async () => {
    const user = userEvent.setup();
    const createObjectUrl = vi.fn((_blob: Blob) => 'blob:behavior');
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: createObjectUrl });
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {});
    renderAt('/behavior');
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
    renderAt('/segments');
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

  it('renders saved purchase-history group labels in model diagnostics', () => {
    renderAt('/model-performance');
    expect(screen.getByText('Exactly one purchase')).toBeInTheDocument();
    expect(screen.queryByText('NaN')).not.toBeInTheDocument();
  });

  it('labels full-period profile values as retrospective rather than forecast inputs', async () => {
    const user = userEvent.setup();
    renderAt('/intelligence');
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

    renderAt('/intelligence');
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
    renderAt('/forecasting');

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
    renderAt('/upload');
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
