import { useMemo, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  AlertCircle, ArrowDownToLine, ChevronLeft, ChevronRight, Clock3, History, Search,
} from 'lucide-react';
import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Scatter, ScatterChart,
  Tooltip, XAxis, YAxis,
} from 'recharts';
import {
  getGetCustomerTrajectoryExplanationQueryKey, getGetCustomerTrajectoryQueryKey,
  getGetTrajectoryClustersQueryKey, getGetTrajectoryCustomersQueryKey,
  getGetTrajectoryEvaluationQueryKey, getGetTrajectorySummaryQueryKey,
  useGetCustomerTrajectory, useGetCustomerTrajectoryExplanation, useGetTrajectoryClusters,
  useGetTrajectoryCustomers, useGetTrajectoryEvaluation, useGetTrajectorySummary,
} from '@workspace/api-client-react';
import type { GetTrajectoryCustomersParams } from '@workspace/api-client-react';

const fmt = (value?: number | null) => value == null || !Number.isFinite(value)
  ? '—'
  : new Intl.NumberFormat('en-GB', { maximumFractionDigits: 2 }).format(value);
const pct = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : `${(value * 100).toFixed(1)}%`;
const money = (value?: number | null) => value == null || !Number.isFinite(value)
  ? '—'
  : new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 2 }).format(value);
const date = (value?: string | null) => value ? new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';
const display = (value: unknown) => value == null ? '—' : typeof value === 'number' ? fmt(value) : String(value);
const humanize = (value?: string | null) => value ? value.replaceAll('_', ' ') : 'Not recorded';
const trajectoryMethodLabel = (method: string) => ({
  exposure_adjusted_30_day_rolling_trajectories: 'Exposure-adjusted 30-day trajectories',
  train_fitted_curve_shape_clustering: 'TRAIN-fitted curve-shape clusters',
  train_fitted_summary_feature_clustering: 'TRAIN-fitted summary clusters',
  train_fitted_grid_based_functional_pca: 'Grid-based functional PCA',
}[method] ?? humanize(method));
const representationLabel = (value?: string | null) => {
  if (value?.includes('standardized_curve_shape_clustering_and_grid_based_functional_pca')) {
    return 'Curve-shape clusters + functional PCA';
  }
  return humanize(value);
};
const modelLabel = (value: string) => value.replace(/^customer-trajectory-analysis-/, 'trajectory-');

type FunctionalScorePoint = {
  customer_id: number;
  [key: string]: number;
};

type FunctionalEvaluation = {
  status?: string;
  test_evaluation?: {
    component_count?: number;
    cumulative_explained_variance?: number;
    explained_variance_ratio?: number[];
    reconstruction_rmse?: number;
    mean_log_curve?: number[];
    component_shapes?: number[][];
  };
  test_score_points?: FunctionalScorePoint[];
  score_relationships_with_static_and_behavior_features?: Array<{
    functional_component: string;
    existing_feature: string;
    eligible_customers: number;
    spearman_rho: number;
    fdr_adjusted_q_value?: number;
  }>;
};

type PredictionRow = {
  model: string;
  customer_count: number;
  roc_auc?: number;
  brier_score?: number;
};

type ClusterHorizonAssociation = {
  evaluated_assigned_customers?: number;
  clusters?: Array<{
    trajectory_cluster_id: number;
    customer_count: number;
    future_purchase_rate: number;
    comparison_future_purchase_rate: number;
    difference_ci_95?: number[];
    fdr_adjusted_q_value?: number;
  }>;
};

type FeatureHorizonAssociation = {
  cohort_customers?: number;
  feature_associations?: Array<{
    feature: string;
    eligible_customers: number;
    point_biserial_correlation: number;
    bootstrap_ci_95?: number[];
    fdr_adjusted_q_value?: number;
  }>;
};

type FutureAssociationPayload = {
  cluster_associations?: { horizons?: Record<string, ClusterHorizonAssociation> };
  trajectory_feature_associations?: { horizons?: Record<string, FeatureHorizonAssociation> };
};

function Skeleton() {
  return <div className="trajectory-skeleton" aria-label="Loading trajectory data"><span /><span /><span /></div>;
}

function QueryNotice({ loading, error, retry, children }: { loading: boolean; error: boolean; retry: () => void; children: ReactNode }) {
  if (loading) return <Skeleton />;
  if (error) return <div className="trajectory-error" role="alert"><AlertCircle size={17} />Could not load saved trajectory data.<button className="button secondary" onClick={retry}>Try again</button></div>;
  return <>{children}</>;
}

function csvDownload(filename: string, headers: string[], rows: unknown[][]) {
  const quote = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const text = [headers, ...rows].map((row) => row.map(quote).join(',')).join('\n');
  const url = URL.createObjectURL(new Blob([text], { type: 'text/csv;charset=utf-8' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export default function TrajectoryPage() {
  const [searchParams] = useSearchParams();
  const [search, setSearch] = useState('');
  const [submittedSearch, setSubmittedSearch] = useState('');
  const [historyFilter, setHistoryFilter] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('');
  const [clusterFilter, setClusterFilter] = useState('');
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<number | null>(() => {
    const candidate = Number(searchParams.get('customer_id'));
    return Number.isInteger(candidate) && candidate > 0 ? candidate : null;
  });
  const [showExplanation, setShowExplanation] = useState(false);
  const params = useMemo<GetTrajectoryCustomersParams>(() => ({
    page, page_size: 12, search: submittedSearch || undefined,
    history_sufficiency: historyFilter ? historyFilter as GetTrajectoryCustomersParams['history_sufficiency'] : undefined,
    hist_segment: segmentFilter.trim() || undefined,
    cluster_id: clusterFilter === '' ? undefined : Number(clusterFilter),
  }), [page, submittedSearch, historyFilter, segmentFilter, clusterFilter]);

  const summary = useGetTrajectorySummary({ query: { queryKey: getGetTrajectorySummaryQueryKey() } });
  const clusters = useGetTrajectoryClusters({ query: { queryKey: getGetTrajectoryClustersQueryKey() } });
  const customers = useGetTrajectoryCustomers(params, { query: { queryKey: getGetTrajectoryCustomersQueryKey(params) } });
  const evaluation = useGetTrajectoryEvaluation({ query: { queryKey: getGetTrajectoryEvaluationQueryKey() } });
  const trajectory = useGetCustomerTrajectory(selectedId ?? 0, {
    query: { enabled: selectedId !== null, queryKey: getGetCustomerTrajectoryQueryKey(selectedId ?? 0) },
  });
  const explanation = useGetCustomerTrajectoryExplanation(selectedId ?? 0, {
    query: { enabled: selectedId !== null && showExplanation, queryKey: getGetCustomerTrajectoryExplanationQueryKey(selectedId ?? 0) },
  });
  const summaryData = summary.data;
  const clusterData = clusters.data;
  const customerData = customers.data;
  const detail = trajectory.data;
  const expl = explanation.data;
  const evaluationResults = evaluation.data?.results as Record<string, unknown> | undefined;
  const functional = evaluationResults?.functional_analysis as FunctionalEvaluation | undefined;
  const prediction = evaluationResults?.predictive_evaluation as {
    models?: PredictionRow[];
    functional_score_model?: { models?: PredictionRow[]; test_customer_count?: number };
  } | undefined;
  const clusterSelection = evaluationResults?.cluster_selection as {
    status?: string;
    selected_cluster_count?: number | null;
    selected_representation?: string | null;
  } | undefined;
  const clusterStatusLabel = clusterSelection?.status?.startsWith('selected_')
    ? 'Selected after TRAIN/VAL checks'
    : humanize(clusterSelection?.status);
  const futureAssociations = evaluationResults?.future_purchase_associations as FutureAssociationPayload | undefined;
  const pageCount = Math.max(1, Math.ceil((customerData?.total ?? 0) / (customerData?.page_size ?? 12)));
  const historyCounts = summaryData?.history_sufficiency_counts ?? {};
  const functionalCurveData = useMemo(() => {
    const curves = functional?.test_evaluation;
    if (!curves?.mean_log_curve?.length) return [];
    return curves.mean_log_curve.map((mean, index) => ({
      window: index + 1,
      mean,
      ...Object.fromEntries((curves.component_shapes ?? []).map((shape, component) => [
        `component_${component + 1}`,
        shape[index],
      ])),
    }));
  }, [functional]);
  const functionalScoreScatter = useMemo(
    () => (functional?.test_score_points ?? []).filter(
      (point) => Number.isFinite(point.functional_component_1)
        && Number.isFinite(point.functional_component_2),
    ),
    [functional],
  );

  const exportPage = () => {
    const rows = customerData?.items ?? [];
    if (!rows.length) return;
    csvDownload(`oelp-trajectories-page-${page}.csv`, [
      'customer_id', 'history_sufficiency', 'observed_windows', 'active_purchase_windows',
      'completed_purchase_gaps', 'trajectory_cluster_id', 'cluster_assignment_status',
      'functional_analysis_status', 'hist_segment', 'history_length_days', 'trajectory_cluster_label',
    ], rows.map((r) => [
      r.customer_id, r.history_sufficiency, r.observed_windows, r.active_purchase_windows,
      r.completed_purchase_gaps, r.trajectory_cluster_id, r.cluster_assignment_status,
      r.functional_analysis_status, r.hist_segment, r.history_length_days, r.trajectory_cluster_label,
    ]));
  };
  const submitSearch = (event: FormEvent) => {
    event.preventDefault();
    setSubmittedSearch(search.trim());
    setPage(1);
    setSelectedId(null);
    setShowExplanation(false);
  };
  const setFilter = (setter: (value: string) => void) => (value: string) => {
    setter(value);
    setPage(1);
    setSelectedId(null);
    setShowExplanation(false);
  };

  const rateChartData = useMemo(() => {
    const byIndex = new Map<number, { window: string; purchase?: number | null; revenue?: number | null }>();
    for (const point of detail?.purchase_rate_trajectory ?? []) {
      byIndex.set(point.window_index, {
        window: `${date(point.window_start)} – ${date(point.window_end)}`,
        purchase: point.purchase_rate,
      });
    }
    for (const point of detail?.revenue_rate_trajectory ?? []) {
      const row = byIndex.get(point.window_index) ?? { window: `Window ${point.window_index + 1}` };
      row.revenue = point.revenue_rate;
      byIndex.set(point.window_index, row);
    }
    return [...byIndex.entries()].sort(([a], [b]) => a - b).map(([, item]) => item);
  }, [detail]);

  return <div className="content trajectory-page">
    <header className="trajectory-intro">
      <div>
        <div className="eyebrow">Research workspace · historical only</div>
        <h1>Customer trajectory explorer</h1>
        <p>Trace observed purchasing rhythm and revenue through the saved history. Every view ends at the recorded cutoff; no future individual outcomes are shown.</p>
      </div>
      <div className="trajectory-cutoff"><History size={16} /><span>Historical cutoff</span><strong>{summaryData ? date(summaryData.cutoff_date) : 'Loading record'}</strong></div>
    </header>
    <div className="historical-banner"><History size={15} /><span><strong>Historical demonstration only.</strong> Rates describe observed windows before the cutoff. Unobserved exposure is not interpreted as a zero purchase rate.</span></div>

    <QueryNotice loading={summary.isLoading} error={summary.isError} retry={() => void summary.refetch()}>
      {summaryData && <>
        <div className="trajectory-metrics">
          <article><span>Eligible customers</span><strong>{fmt(summaryData.eligible_customers)}</strong><small>of {fmt(summaryData.total_customers)} in saved dataset</small></article>
          <article><span>Cluster assigned</span><strong>{fmt(summaryData.clustered_customer_count)}</strong><small>{fmt(summaryData.unassigned_customer_count)} unassigned</small></article>
          <article><span>Functional eligible</span><strong>{fmt(summaryData.functional_eligible_customers)}</strong><small>Based on recorded history support</small></article>
          <article><span>Model record</span><strong className="trajectory-model">{modelLabel(summaryData.model_version)}</strong><small>Cutoff {date(summaryData.cutoff_date)}</small></article>
        </div>
        <div className="trajectory-meta">
          <div><span>Selected representation</span><strong>{representationLabel(summaryData.selected_representation)}</strong></div>
          <div><span>Available trajectory methods</span><strong>{summaryData.available_trajectory_methods.length ? summaryData.available_trajectory_methods.map(trajectoryMethodLabel).join(' · ') : 'None recorded'}</strong></div>
          <div className="trajectory-counts"><span>History sufficiency</span>{Object.entries(historyCounts).map(([key, value]) => <span className="trajectory-count" key={key}>{key.replaceAll('_', ' ')} <b>{fmt(value)}</b></span>)}</div>
        </div>
      </>}
    </QueryNotice>

    <div className="trajectory-section-grid">
      <section className="panel">
        <div className="panel-head"><div><div className="panel-title">Cluster profiles</div><div className="panel-note">Saved aggregate curves; rates use separate vertical scales</div></div></div>
        <QueryNotice loading={clusters.isLoading} error={clusters.isError} retry={() => void clusters.refetch()}>
          {clusterData && (clusterData.available && clusterData.clusters.length
            ? <div className="trajectory-cluster-list">{clusterData.clusters.map((cluster) => {
              const windowIndices = [...new Set([
                ...cluster.mean_purchase_rate_curve.map((point) => point.window_index),
                ...cluster.mean_revenue_rate_curve.map((point) => point.window_index),
              ])].sort((a, b) => a - b);
              const chart = windowIndices.map((index) => ({
                window: index + 1,
                purchase: cluster.mean_purchase_rate_curve.find((point) => point.window_index === index)?.mean_rate,
                revenue: cluster.mean_revenue_rate_curve.find((point) => point.window_index === index)?.mean_rate,
              }));
              return <article className="trajectory-cluster" key={cluster.cluster_id}>
                <div className="trajectory-cluster-head"><div><span>Cluster {cluster.cluster_id}</span><h3>{cluster.cluster_label}</h3></div><div><strong>{fmt(cluster.customer_count)}</strong><small>{pct(cluster.cluster_share)} of assigned</small></div></div>
                 <div className="chart-wrap short"><ResponsiveContainer><LineChart data={chart} margin={{ top: 5, right: 12, left: 0, bottom: 0 }}><CartesianGrid stroke="#e8e4d9" vertical={false} /><XAxis dataKey="window" tick={{ fontSize: 9, fill: '#7c8980' }} axisLine={false} tickLine={false} /><YAxis yAxisId="purchase" tick={{ fontSize: 9, fill: '#315a4c' }} axisLine={false} tickLine={false} width={34} /><YAxis yAxisId="revenue" orientation="right" tick={{ fontSize: 9, fill: '#c47b58' }} axisLine={false} tickLine={false} width={34} /><Tooltip /><Legend /><Line yAxisId="purchase" type="monotone" dataKey="purchase" name="Mean purchase rate" stroke="#315a4c" strokeWidth={2} dot={false} connectNulls={false} /><Line yAxisId="revenue" type="monotone" dataKey="revenue" name="Mean revenue rate" stroke="#c47b58" strokeWidth={2} dot={false} connectNulls={false} /></LineChart></ResponsiveContainer></div>
                <div className="trajectory-cluster-stats">{Object.entries(cluster.observed_purchasing_statistics).map(([key, value]) => <span key={key}>{key.replaceAll('_', ' ')} <b>{fmt(value)}</b></span>)}</div>
                <div className="trajectory-segments"><span>Historical segment distribution</span>{Object.entries(cluster.historical_segment_distribution).map(([key, value]) => <span key={key}>{key}: {fmt(value)}</span>)}</div>
              </article>;
            })}</div>
            : <div className="trajectory-empty" data-testid="state-clusters-unavailable"><strong>{clusterData.available ? 'No cluster profiles returned' : 'Cluster profiles unavailable'}</strong><span>{clusterData.available ? 'The saved response contains no cluster profile records.' : 'The saved response does not mark trajectory clusters as available. No cluster fit is inferred here.'}</span></div>)}
        </QueryNotice>
        {clusterData?.limitations.length ? <ul className="trajectory-limits">{clusterData.limitations.map((item, i) => <li key={`${i}-${item}`}>{item}</li>)}</ul> : null}
      </section>
      <section className="panel">
        <div className="panel-head"><div><div className="panel-title">Evaluation & method notes</div><div className="panel-note">Interpretation is bounded by the saved evaluation record</div></div></div>
        <QueryNotice loading={evaluation.isLoading} error={evaluation.isError} retry={() => void evaluation.refetch()}>
          {evaluation.data && <>
            <div className="trajectory-eval-status"><span>Status</span><strong>{evaluation.data.status}</strong><span>Model {evaluation.data.model_version}</span></div>
            <div className="trajectory-results">
              <h3>Cluster selection</h3>
              <div><span>Status</span><strong>{clusterStatusLabel}</strong></div>
              <div><span>Selected clusters</span><strong>{display(clusterSelection?.selected_cluster_count)}</strong></div>
              <div><span>Representation</span><strong>{clusterSelection?.selected_representation ?? 'Not recorded'}</strong></div>
            </div>
            <div className="trajectory-results">
              <h3>30-day TEST benchmark · summary-eligible cohort</h3>
              {prediction?.models?.map((row) => <div key={row.model}>
                <span>{row.model} · {fmt(row.customer_count)} customers</span>
                <strong>AUC {fmt(row.roc_auc)} · Brier {fmt(row.brier_score)}</strong>
              </div>)}
            </div>
            {prediction?.functional_score_model?.models?.length ? <div className="trajectory-results">
              <h3>Functional-score benchmark · {fmt(prediction.functional_score_model.test_customer_count)} customers</h3>
              {prediction.functional_score_model.models.map((row) => <div key={row.model}>
                <span>{row.model} · {fmt(row.customer_count)} customers</span>
                <strong>AUC {fmt(row.roc_auc)} · Brier {fmt(row.brier_score)}</strong>
              </div>)}
            </div> : null}
            <h3 className="trajectory-subheading">Limitations</h3>
            {evaluation.data.limitations.length ? <ul className="trajectory-limits">{evaluation.data.limitations.map((item, i) => <li key={`${i}-${item}`}>{item}</li>)}</ul> : <p className="tiny">No limitation text was supplied in the evaluation response.</p>}
          </>}
        </QueryNotice>
        {summaryData?.limitations.length ? <><h3 className="trajectory-subheading">Summary limitations</h3><ul className="trajectory-limits">{summaryData.limitations.map((item, i) => <li key={`${i}-${item}`}>{item}</li>)}</ul></> : null}
      </section>
    </div>

    <section className="panel trajectory-functional-panel">
      <div className="panel-head"><div><div className="panel-title">Functional curve representation</div><div className="panel-note">TRAIN-fitted grid-based PCA approximation · historical curves only</div></div></div>
      {functional?.test_evaluation?.component_count ? <>
        <div className="trajectory-functional-metrics">
          <div><span>Supported TEST curves</span><strong>{fmt(functional.test_evaluation.component_count ? functional.test_score_points?.length : 0)}</strong></div>
          <div><span>Components</span><strong>{fmt(functional.test_evaluation.component_count)}</strong></div>
          <div><span>Variance summarized</span><strong>{pct(functional.test_evaluation.cumulative_explained_variance)}</strong></div>
          <div><span>Reconstruction RMSE</span><strong>{fmt(functional.test_evaluation.reconstruction_rmse)}</strong></div>
        </div>
        <p className="trajectory-functional-note">The left chart shows mean log purchase rate; the right chart shows normalized principal-component directions. Components describe recorded associations, not future direction or causal mechanisms.</p>
        <div className="trajectory-functional-grid">
          <article><h3>Mean curve and component shapes</h3>
            <div className="chart-wrap trajectory-functional-chart"><ResponsiveContainer><LineChart data={functionalCurveData} margin={{ top: 8, right: 10, left: 0, bottom: 0 }}><CartesianGrid stroke="#e8e4d9" vertical={false} /><XAxis dataKey="window" tick={{ fontSize: 9, fill: '#7c8980' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 9, fill: '#7c8980' }} axisLine={false} tickLine={false} width={42} /><Tooltip /><Legend /><Line type="monotone" dataKey="mean" name="Mean log rate" stroke="#315a4c" strokeWidth={2.2} dot={{ r: 2 }} />{(functional.test_evaluation.component_shapes ?? []).map((_, index) => <Line key={index} type="monotone" dataKey={`component_${index + 1}`} name={`PC ${index + 1}`} stroke={['#c47b58', '#7488b8', '#94759d'][index % 3]} strokeWidth={1.7} dot={false} />)}</LineChart></ResponsiveContainer></div>
          </article>
          <article><h3>Customer positions · PC1 vs PC2</h3>
            {functionalScoreScatter.length > 0 ? <div className="chart-wrap trajectory-functional-chart"><ResponsiveContainer><ScatterChart margin={{ top: 8, right: 14, left: 4, bottom: 6 }}><CartesianGrid stroke="#e8e4d9" /><XAxis type="number" dataKey="functional_component_1" name="PC 1" tick={{ fontSize: 9, fill: '#7c8980' }} axisLine={false} tickLine={false} /><YAxis type="number" dataKey="functional_component_2" name="PC 2" tick={{ fontSize: 9, fill: '#7c8980' }} axisLine={false} tickLine={false} width={36} /><Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={(value, name) => [fmt(Number(value)), String(name)]} /><Scatter name="Supported customers" data={functionalScoreScatter} fill="#315a4c" fillOpacity={0.5} /></ScatterChart></ResponsiveContainer></div> : <div className="trajectory-empty">No two-component score scatter is available for this fit.</div>}
          </article>
        </div>
        <div className="trajectory-functional-variance">{(functional.test_evaluation.explained_variance_ratio ?? []).map((value, index) => <span key={index}>PC {index + 1} explained <b>{pct(value)}</b></span>)}</div>
        {functional.score_relationships_with_static_and_behavior_features?.length ? <div className="trajectory-functional-relationships"><h3>Functional scores and existing features</h3><div className="table-scroll"><table className="trajectory-table"><thead><tr><th>Component</th><th>Historical feature</th><th>Customers</th><th>Spearman ρ</th><th>BH-adjusted q</th></tr></thead><tbody>{functional.score_relationships_with_static_and_behavior_features.map((row) => <tr key={`${row.functional_component}-${row.existing_feature}`}><td>{row.functional_component.replaceAll('_', ' ')}</td><td>{row.existing_feature.replaceAll('_', ' ')}</td><td className="number">{fmt(row.eligible_customers)}</td><td className="number">{fmt(row.spearman_rho)}</td><td className="number">{fmt(row.fdr_adjusted_q_value)}</td></tr>)}</tbody></table></div></div> : null}
      </> : <div className="trajectory-empty">Functional PCA was not fitted because the saved data did not meet its documented history-support requirements.</div>}
    </section>

    <section className="panel trajectory-associations-panel">
      <div className="panel-head"><div><div className="panel-title">Retrospective purchase associations</div><div className="panel-note">Aggregate 30-, 60- and 90-day TEST outcomes · exploratory, not causal or permanent churn labels</div></div></div>
      <h3>Frozen shape groups</h3>
      <div className="table-scroll"><table className="trajectory-table"><thead><tr><th>Horizon</th><th>Group</th><th>Customers</th><th>Group purchase rate</th><th>Other groups</th><th>Difference 95% interval</th><th>BH q</th></tr></thead><tbody>
        {Object.entries(futureAssociations?.cluster_associations?.horizons ?? {}).flatMap(([horizon, result]) => (result.clusters ?? []).map((row) => <tr key={`${horizon}-${row.trajectory_cluster_id}`}>
          <td>{horizon} days</td><td>{row.trajectory_cluster_id}</td><td className="number">{fmt(row.customer_count)}</td><td className="number">{pct(row.future_purchase_rate)}</td><td className="number">{pct(row.comparison_future_purchase_rate)}</td><td className="number">{row.difference_ci_95?.length === 2 ? `${pct(row.difference_ci_95[0])} to ${pct(row.difference_ci_95[1])}` : '—'}</td><td className="number">{fmt(row.fdr_adjusted_q_value)}</td>
        </tr>))}
      </tbody></table></div>
      <h3 className="trajectory-association-subheading">Trajectory features across all TEST customers</h3>
      <div className="table-scroll"><table className="trajectory-table"><thead><tr><th>Horizon</th><th>Feature</th><th>Customers</th><th>Point-biserial association</th><th>Bootstrap 95% interval</th><th>BH q</th></tr></thead><tbody>
        {Object.entries(futureAssociations?.trajectory_feature_associations?.horizons ?? {}).flatMap(([horizon, result]) => (result.feature_associations ?? []).map((row) => <tr key={`${horizon}-${row.feature}`}>
          <td>{horizon} days</td><td>{row.feature.replaceAll('_', ' ')}</td><td className="number">{fmt(row.eligible_customers)}</td><td className="number">{fmt(row.point_biserial_correlation)}</td><td className="number">{row.bootstrap_ci_95?.length === 2 ? `${fmt(row.bootstrap_ci_95[0])} to ${fmt(row.bootstrap_ci_95[1])}` : '—'}</td><td className="number">{fmt(row.fdr_adjusted_q_value)}</td>
        </tr>))}
      </tbody></table></div>
      {!futureAssociations?.cluster_associations?.horizons && !futureAssociations?.trajectory_feature_associations?.horizons
        ? <div className="trajectory-empty">No matured TEST association results were saved.</div>
        : <p className="trajectory-association-note">Intervals describe sampling uncertainty among assigned or otherwise eligible historical customers. They do not correct for cluster-selection or model-vintage bias, and are not individual predictions.</p>}
    </section>

    <section className="panel trajectory-customer-panel">
      <div className="panel-head"><div><div className="panel-title">Historical customer records</div><div className="panel-note">Search, filter and inspect the saved cohort; export includes only the visible page</div></div>
        <button className="button secondary" disabled={!customerData?.items.length} onClick={exportPage} data-testid="button-export-trajectory-csv"><ArrowDownToLine />Export visible rows</button>
      </div>
      <div className="trajectory-filters">
        <form className="trajectory-search" onSubmit={submitSearch}><label htmlFor="trajectory-search">Customer ID</label><div><Search size={15} /><input id="trajectory-search" value={search} inputMode="numeric" onChange={(e) => setSearch(e.target.value)} placeholder="Search saved IDs" data-testid="input-trajectory-search" /><button className="button" type="submit">Search</button></div></form>
        <label>History support<select value={historyFilter} onChange={(e) => setFilter(setHistoryFilter)(e.target.value)} data-testid="select-trajectory-sufficiency"><option value="">All history levels</option><option value="sufficient_for_functional_analysis">Sufficient for functional analysis</option><option value="sufficient_for_summary_trajectory">Sufficient for summary trajectory</option><option value="limited_history">Limited history</option><option value="insufficient_history">Insufficient history</option></select></label>
        <label>Historical segment<input value={segmentFilter} onChange={(e) => setFilter(setSegmentFilter)(e.target.value)} placeholder="Any segment" data-testid="input-trajectory-segment" /></label>
        <label>Trajectory cluster<select value={clusterFilter} onChange={(e) => setFilter(setClusterFilter)(e.target.value)} data-testid="select-trajectory-cluster"><option value="">All assignments</option>{clusterData?.available && clusterData.clusters.map((item) => <option key={item.cluster_id} value={item.cluster_id}>{item.cluster_label}</option>)}</select></label>
      </div>
      <QueryNotice loading={customers.isLoading} error={customers.isError} retry={() => void customers.refetch()}>
        {customerData && (customerData.items.length
          ? <>
            <p className="trajectory-result-count">{fmt(customerData.total)} matching records · model {customerData.model_version} · cutoff {date(customerData.cutoff_date)}</p>
            <div className="table-scroll"><table className="trajectory-table"><thead><tr><th>Customer</th><th>History support</th><th>Windows observed</th><th>Purchase-active windows</th><th>Completed gaps</th><th>Trajectory cluster</th><th>Functional analysis</th><th>History length</th><th></th></tr></thead><tbody>{customerData.items.map((item) => <tr className={selectedId === item.customer_id ? 'selected' : ''} key={item.customer_id}>
              <td className="number">{item.customer_id}</td><td><span className={`badge${item.history_sufficiency.includes('insufficient') ? ' warn' : ''}`}>{item.history_sufficiency.replaceAll('_', ' ')}</span></td><td className="number">{fmt(item.observed_windows)}</td><td className="number">{fmt(item.active_purchase_windows)}</td><td className="number">{fmt(item.completed_purchase_gaps)}</td><td>{item.trajectory_cluster_label ?? item.cluster_assignment_status.replaceAll('_', ' ')}</td><td>{item.functional_analysis_status.replaceAll('_', ' ')}</td><td className="number">{fmt(item.history_length_days)}d</td><td><button className="button secondary" onClick={() => { setSelectedId(item.customer_id); setShowExplanation(false); }} data-testid={`button-open-trajectory-${item.customer_id}`}>Inspect</button></td>
            </tr>)}</tbody></table></div>
            <div className="trajectory-pagination"><span>Page {customerData.page} of {pageCount}</span><div><button aria-label="Previous customer page" className="button secondary" disabled={page <= 1 || customers.isFetching} onClick={() => setPage((n) => Math.max(1, n - 1))}><ChevronLeft />Previous</button><button aria-label="Next customer page" className="button secondary" disabled={page >= pageCount || customers.isFetching} onClick={() => setPage((n) => n + 1)}>Next<ChevronRight /></button></div></div>
          </>
          : <div className="trajectory-empty">No customer records match these filters. Adjust the search or filters to broaden the historical cohort.</div>)}
      </QueryNotice>
    </section>

    {selectedId !== null && <section className="panel trajectory-detail" data-testid="panel-customer-trajectory">
      <div className="panel-head"><div><div className="panel-title">Customer {selectedId} · observed trajectory</div><div className="panel-note">Purchase and revenue rates use recorded exposure windows up to the cutoff</div></div></div>
      <QueryNotice loading={trajectory.isLoading} error={trajectory.isError} retry={() => void trajectory.refetch()}>
        {detail && <>
          <div className="trajectory-detail-summary">
            <div><span>History sufficiency</span><strong>{detail.history_sufficiency.replaceAll('_', ' ')}</strong></div>
            <div><span>Cluster assignment</span><strong>{detail.trajectory_cluster_label ?? detail.cluster_assignment_status.replaceAll('_', ' ')}</strong></div>
            <div><span>Functional analysis</span><strong>{detail.functional_analysis_status.replaceAll('_', ' ')}</strong></div>
            <div><span>Cutoff / model</span><strong>{date(detail.cutoff_date)} · {detail.model_version}</strong></div>
          </div>
          {(detail.history_sufficiency.includes('insufficient') || detail.history_sufficiency.includes('limited') || /insufficient|unsupported|not_eligible|ineligible/i.test(detail.functional_analysis_status)) && <div className="trajectory-support-warning" role="status"><Clock3 size={16} /><span>Recorded history does not support every trajectory method for this customer. Available observed windows and support details remain visible without extrapolation.</span></div>}
          <div className="trajectory-detail-layout">
            <div><h3>Observed rate by history window</h3>{rateChartData.length
              ? <div className="chart-wrap trajectory-detail-chart"><ResponsiveContainer><LineChart data={rateChartData} margin={{ top: 8, right: 14, left: 0, bottom: 20 }}><CartesianGrid stroke="#e8e4d9" vertical={false} /><XAxis dataKey="window" angle={-18} textAnchor="end" height={48} tick={{ fontSize: 8, fill: '#7c8980' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 9, fill: '#7c8980' }} axisLine={false} tickLine={false} width={36} /><Tooltip /><Legend /><Line type="monotone" dataKey="purchase" name="Purchase rate" stroke="#315a4c" strokeWidth={2} dot={{ r: 2 }} connectNulls={false} /><Line type="monotone" dataKey="revenue" name="Revenue rate" stroke="#c47b58" strokeWidth={2} dot={{ r: 2 }} connectNulls={false} /></LineChart></ResponsiveContainer></div>
              : <div className="trajectory-empty">No supported rate windows were returned for this customer.</div>}
              <div className="table-scroll"><table className="trajectory-table"><thead><tr><th>Observed window</th><th>Exposure days</th><th>Purchases</th><th>Gross revenue</th><th>Purchase rate</th><th>Revenue rate</th><th>Observation status</th></tr></thead><tbody>{detail.purchase_rate_trajectory.map((point) => <tr key={point.window_index}><td>{date(point.window_start)} – {date(point.window_end)}</td><td className="number">{fmt(point.observed_exposure_days)}</td><td className="number">{fmt(point.purchase_count)}</td><td className="number">{money(point.gross_revenue)}</td><td className="number">{fmt(point.purchase_rate)}</td><td className="number">{fmt(point.revenue_rate)}</td><td>{point.window_observation_status.replaceAll('_', ' ')}</td></tr>)}</tbody></table></div>
            </div>
            <aside className="trajectory-side-detail">
              <div className="trajectory-side-card"><h3>History support details</h3>{Object.entries(detail.history_support_details).length ? Object.entries(detail.history_support_details).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{display(value)}</strong></div>) : <p className="tiny">No support detail fields recorded.</p>}</div>
              <div className="trajectory-side-card"><h3>Functional component scores</h3>{detail.functional_analysis_status.toLowerCase().includes('unsupported') || detail.functional_analysis_status.toLowerCase().includes('insufficient')
                ? <p className="trajectory-support-muted">Not available for this history support status.</p>
                : Object.entries(detail.functional_component_scores).filter(([, value]) => value != null).length
                  ? Object.entries(detail.functional_component_scores).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{fmt(value)}</strong></div>)
                  : <p className="trajectory-support-muted">No component scores are present in the response.</p>}</div>
              <button className="button secondary" onClick={() => setShowExplanation(true)} data-testid="button-load-trajectory-explanation">Load interpretation</button>
              {showExplanation && <QueryNotice loading={explanation.isLoading} error={explanation.isError} retry={() => void explanation.refetch()}>{expl && <div className="trajectory-side-card"><h3>Saved interpretation</h3><p>{expl.interpretation}</p><div><span>Functional analysis</span><strong>{expl.functional_analysis_status}</strong></div><div><span>Cluster assignment</span><strong>{expl.cluster_assignment_status}</strong></div>{Object.entries(expl.supported_features).map(([key, value]) => <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{fmt(value)}</strong></div>)}{expl.limitations.length > 0 && <ul className="trajectory-limits">{expl.limitations.map((item, i) => <li key={`${i}-${item}`}>{item}</li>)}</ul>}</div>}</QueryNotice>}
            </aside>
          </div>
          {detail.limitations.length > 0 && <div className="trajectory-detail-limitations"><strong>Customer trajectory limitations</strong><ul className="trajectory-limits">{detail.limitations.map((item, i) => <li key={`${i}-${item}`}>{item}</li>)}</ul></div>}
        </>}
      </QueryNotice>
    </section>}
  </div>;
}
