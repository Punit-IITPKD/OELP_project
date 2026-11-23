import { useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { getGetBehaviorSummaryQueryKey, getGetBehaviorCustomersQueryKey, getGetBehaviorEvaluationQueryKey, getGetCustomerBehaviorQueryKey, getGetCustomerBehaviorTrajectoryQueryKey, useGetBehaviorSummary, useGetBehaviorCustomers, useGetBehaviorEvaluation, useGetCustomerBehavior, useGetCustomerBehaviorTrajectory } from '@workspace/api-client-react';
import type { BehaviorCustomerDetail, GetBehaviorCustomersHistorySufficiency, GetBehaviorCustomersSortBy } from '@workspace/api-client-react';
import { Activity, AlertCircle, ArrowDownToLine, History, Search, Users } from 'lucide-react';
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const num = (v?: number | null) => v == null || !Number.isFinite(v) ? '—' : new Intl.NumberFormat('en-GB', { maximumFractionDigits: 2 }).format(v);
const money = (v?: number | null) => v == null || !Number.isFinite(v) ? '—' : new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(v);
const pct = (v?: number | null) => v == null || !Number.isFinite(v) ? '—' : `${(v * 100).toFixed(1)}%`;
const date = (v?: string) => v ? new Date(v).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';

function Panel({ title, note, children, extra }: { title: string; note?: string; children: ReactNode; extra?: ReactNode }) {
  return <section className="panel"><div className="panel-head"><div><div className="panel-title">{title}</div>{note && <div className="panel-note">{note}</div>}</div>{extra}</div>{children}</section>;
}
function State({ query, empty, children }: { query: { isLoading: boolean; isError: boolean; refetch: () => unknown }; empty?: boolean; children: ReactNode }) {
  if (query.isLoading) return <div className="grid"><div className="skeleton" /><div className="skeleton" /></div>;
  if (query.isError) return <div className="error-box"><AlertCircle size={15} /> Data could not be loaded. <button className="button secondary" onClick={() => void query.refetch()}>Try again</button></div>;
  if (empty) return <div className="empty-box">No saved historical data is available for this view.</div>;
  return <>{children}</>;
}
function Metric({ title, value, foot }: { title: string; value: string; foot: string }) {
  return <div className="panel"><div className="metric-label">{title}<Activity size={15} color="#83978b" /></div><div className="metric-value number">{value}</div><div className="metric-accent" /><div className="metric-foot">{foot}</div></div>;
}

export default function BehaviorPage() {
  const summary = useGetBehaviorSummary({ query: { queryKey: getGetBehaviorSummaryQueryKey() } });
  const [search, setSearch] = useState('');
  const [segment, setSegment] = useState('');
  const [historyGroup, setHistoryGroup] = useState('');
  const [sufficiency, setSufficiency] = useState<GetBehaviorCustomersHistorySufficiency | ''>('');
  const [sort, setSort] = useState<GetBehaviorCustomersSortBy>('current_elapsed_gap_days');
  const [direction, setDirection] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number | null>(null);
  const params = useMemo(() => ({ page, page_size: 10, search: search.trim() || undefined, hist_segment: segment || undefined, history_group: historyGroup || undefined, history_sufficiency: sufficiency || undefined, sort_by: sort, sort_direction: direction }), [page, search, segment, historyGroup, sufficiency, sort, direction]);
  const customers = useGetBehaviorCustomers(params, { query: { queryKey: getGetBehaviorCustomersQueryKey(params) } });
  const evaluation = useGetBehaviorEvaluation({ query: { queryKey: getGetBehaviorEvaluationQueryKey() } });
  const detail = useGetCustomerBehavior(selected ?? 0, { query: { enabled: Boolean(selected), queryKey: getGetCustomerBehaviorQueryKey(selected ?? 0) } });
  const trajectory = useGetCustomerBehaviorTrajectory(selected ?? 0, { query: { enabled: Boolean(selected), queryKey: getGetCustomerBehaviorTrajectoryQueryKey(selected ?? 0) } });
  const d = detail.data as BehaviorCustomerDetail | undefined;
  const rows = customers.data?.items ?? [];
  const exportCsv = () => {
    if (!rows.length) return;
    const columns = ['customer_id', 'cutoff_date', 'hist_segment', 'history_group', 'recency', 'frequency', 'current_elapsed_gap_days', 'completed_gap_count', 'median_completed_gap_days', 'mad_completed_gap_days', 'gap_deviation_score', 'recent_order_count', 'reference_order_count', 'purchase_rate_ratio', 'recent_gross_revenue', 'reference_gross_revenue', 'revenue_rate_ratio', 'history_sufficiency', 'personalized_delay_ratio', 'purchase_probability_30d', 'purchase_probability_60d', 'purchase_probability_90d', 'available_indicator_count', 'policy_version', 'policy_status'];
    const quote = (v: unknown) => `"${String(v ?? '').replaceAll('"', '""')}"`;
    const csv = [columns.map(quote).join(','), ...rows.map((row) => columns.map((key) => quote(row[key as keyof typeof row])).join(','))].join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `oelp-behavior-page-${page}.csv`; anchor.click(); URL.revokeObjectURL(url);
  };
  const resetPage = () => setPage(1);
  return <div className="content">
    <div className="page-heading"><div><div className="eyebrow">Notebook 08 · historical behavior</div><h1>Behavior indicators</h1><p>Inspect cutoff-safe purchase patterns and the evidence behind candidate indicators. Signals remain descriptive until independently validated.</p></div></div>
    <div className="historical-banner"><History size={15} /><span><strong>Historical demonstration only.</strong> Every measure is anchored to the saved cutoff. These are continuous historical indicators—not churn alerts, live monitoring, or current-business recommendations.</span></div>
    <State query={summary} empty={!summary.data}>{summary.data && <>
      <div className="grid kpis">
        <Metric title="Eligible customers" value={num(summary.data.eligible_customers)} foot={`Cutoff ${date(summary.data.cutoff_date)}`} />
        <Metric title="History sufficient" value={num(summary.data.history_sufficiency.find((x) => x.history_sufficiency === 'sufficient')?.customers)} foot="Enough observed purchase history" />
        <Metric title="Limited history" value={num(summary.data.history_sufficiency.find((x) => x.history_sufficiency === 'limited')?.customers)} foot="Interpret indicators with care" />
        <Metric title="Policy status" value={summary.data.policy_status.replaceAll('_', ' ')} foot={`Version ${summary.data.policy_version}`} />
      </div>
      <div className="behavior-policy-note" data-testid="behavior-policy-status"><strong>Validated alert policy:</strong> {summary.data.alert_policy_available ? 'available' : 'not available'} · History sufficiency counts are classifications of observed coverage, not confidence guarantees.</div>
      <Panel title="History sufficiency" note="Counts from the saved cohort summary">
        <div className="table-scroll"><table><thead><tr><th>History level</th><th>Customers</th><th>Interpretation</th></tr></thead><tbody>{summary.data.history_sufficiency.map((level) => <tr key={level.history_sufficiency}><td><span className="badge neutral">{level.history_sufficiency}</span></td><td className="number">{num(level.customers)}</td><td>{level.history_sufficiency === 'sufficient' ? 'More observed history is available for these indicators.' : level.history_sufficiency === 'limited' ? 'Interpret comparisons cautiously.' : 'Several indicators may be unavailable.'}</td></tr>)}</tbody></table></div>
      </Panel>
      <div style={{ marginTop: 16 }} />
      <Panel title="Cohort distributions" note="Available feature coverage and percentile context from the historical cohort">
        {summary.data.distributions.length ? <div className="grid two behavior-distributions">{summary.data.distributions.map((distribution) => <div key={distribution.field} className="behavior-distribution"><div className="behavior-distribution-head"><strong>{distribution.label}</strong><span>{num(distribution.available_customers)} available</span></div><div className="behavior-percentiles"><span>Median <b>{num(distribution.median)}</b></span><span>P75 <b>{num(distribution.percentile_75)}</b></span><span>P90 <b>{num(distribution.percentile_90)}</b></span></div><div className="chart-wrap short"><ResponsiveContainer><BarChart data={distribution.bins}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="label" tick={{ fontSize: 8, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 8, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip /><Bar dataKey="customers" name="Customers" fill="#78918a" radius={[3, 3, 0, 0]}>{distribution.bins.map((bin, i) => <Cell key={`${bin.label}-${i}`} fill={['#315a4c', '#d8ad5e', '#c57d5c', '#78918a'][i % 4]} />)}</Bar></BarChart></ResponsiveContainer></div></div>)}</div> : <div className="empty-box">No feature distributions are included in this saved summary.</div>}
      </Panel>
    </>}</State>
    <div style={{ marginTop: 16 }}>
      <Panel title="Historical customer cohort" note="Search and sort are applied by the saved behavior endpoint. Export downloads the visible result page." extra={<button className="button secondary" disabled={!rows.length} onClick={exportCsv} data-testid="button-export-behavior-csv"><ArrowDownToLine />Export visible rows</button>}>
        <div className="filter-row behavior-filters">
          <div className="field"><label className="field-label" htmlFor="behavior-search">Customer ID</label><div style={{ position: 'relative' }}><Search size={14} style={{ position: 'absolute', top: 11, left: 10, color: '#85938b' }} /><input id="behavior-search" className="input" style={{ paddingLeft: 31 }} value={search} onChange={(e) => { setSearch(e.target.value); resetPage(); }} placeholder="Search customer" data-testid="input-behavior-search" /></div></div>
          <div className="field"><label className="field-label" htmlFor="behavior-segment">Historical segment</label><input id="behavior-segment" className="input" value={segment} onChange={(e) => { setSegment(e.target.value); resetPage(); }} placeholder="Any segment" data-testid="input-behavior-segment" /></div>
          <div className="field"><label className="field-label" htmlFor="behavior-group">History group</label><input id="behavior-group" className="input" value={historyGroup} onChange={(e) => { setHistoryGroup(e.target.value); resetPage(); }} placeholder="Any history group" data-testid="input-behavior-history-group" /></div>
          <div className="field"><label className="field-label" htmlFor="behavior-sufficiency">History sufficiency</label><select id="behavior-sufficiency" className="input" value={sufficiency} onChange={(e) => { setSufficiency(e.target.value as GetBehaviorCustomersHistorySufficiency | ''); resetPage(); }} data-testid="select-behavior-sufficiency"><option value="">All levels</option><option value="sufficient">Sufficient</option><option value="limited">Limited</option><option value="insufficient">Insufficient</option></select></div>
          <div className="field"><label className="field-label" htmlFor="behavior-sort">Sort by</label><select id="behavior-sort" className="input" value={sort} onChange={(e) => { setSort(e.target.value as GetBehaviorCustomersSortBy); resetPage(); }} data-testid="select-behavior-sort"><option value="current_elapsed_gap_days">Elapsed gap</option><option value="gap_deviation_score">Gap deviation</option><option value="purchase_rate_ratio">Purchase-rate ratio</option><option value="revenue_rate_ratio">Revenue-rate ratio</option><option value="personalized_delay_ratio">Personalized delay ratio</option><option value="recency">Recency</option></select></div>
          <button className="button secondary behavior-direction" onClick={() => { setDirection((v) => v === 'desc' ? 'asc' : 'desc'); resetPage(); }} data-testid="button-behavior-sort-direction">{direction === 'desc' ? 'High to low' : 'Low to high'}</button>
        </div>
        <State query={customers} empty={!rows.length}>{customers.data && <>
          <div className="table-scroll"><table><thead><tr><th>Customer</th><th>Segment / history</th><th>Elapsed gap</th><th>Completed gaps</th><th>Gap deviation</th><th>Purchase ratio</th><th>Revenue ratio</th><th>Sufficiency</th><th></th></tr></thead><tbody>{rows.map((item) => <tr key={item.customer_id} className={selected === item.customer_id ? 'behavior-selected-row' : ''} data-testid={`row-behavior-customer-${item.customer_id}`}><td className="number">{item.customer_id}<div className="tiny">{date(item.cutoff_date)}</div></td><td>{item.hist_segment ?? '—'}<div className="tiny">{item.history_group ?? '—'}</div></td><td className="number">{num(item.current_elapsed_gap_days)}d</td><td className="number">{num(item.completed_gap_count)}</td><td className="number">{num(item.gap_deviation_score)}</td><td className="number">{num(item.purchase_rate_ratio)}</td><td className="number">{num(item.revenue_rate_ratio)}</td><td><span className="badge neutral">{item.history_sufficiency}</span></td><td><button className="button secondary" onClick={() => setSelected(item.customer_id)} data-testid={`button-view-behavior-${item.customer_id}`}>Inspect</button></td></tr>)}</tbody></table></div>
          <div className="filter-row" style={{ justifyContent: 'space-between', margin: '12px 0 0' }}><span className="tiny">{num(customers.data.total)} customers · page {customers.data.page} of {Math.max(1, Math.ceil(customers.data.total / customers.data.page_size))}</span><div style={{ display: 'flex', gap: 7 }}><button className="button secondary" disabled={page <= 1 || customers.isFetching} onClick={() => setPage((v) => Math.max(1, v - 1))} data-testid="button-behavior-previous">Previous</button><button className="button secondary" disabled={page >= Math.ceil(customers.data.total / customers.data.page_size) || customers.isFetching} onClick={() => setPage((v) => v + 1)} data-testid="button-behavior-next">Next</button></div></div>
        </>}</State>
      </Panel>
    </div>
    {selected !== null && <div className="grid two" style={{ marginTop: 16 }}>
      <Panel title={`Customer ${selected} · indicator detail`} note="Feature values and explanations are historical observations, not causal conclusions.">
        {detail.isLoading ? <div className="skeleton" /> : detail.isError ? <div className="error-box">Customer detail could not be loaded. <button className="button secondary" onClick={() => void detail.refetch()}>Try again</button></div> : !d ? <div className="empty-box">No detailed indicators are available.</div> : <>
          <div className="behavior-policy-note" data-testid="copy-no-alert-policy"><strong>No validated alert policy.</strong> These are continuous historical indicators, not churn alerts or live/current recommendations.</div>
          <div className="behavior-value-grid">
            <Value label="Current elapsed gap" value={`${num(d.current_elapsed_gap_days)} days`} /><Value label="Median / MAD gap" value={`${num(d.median_completed_gap_days)} / ${num(d.mad_completed_gap_days)}`} />
            <Value label="Gap deviation · method" value={`${num(d.gap_deviation_score)} · ${d.gap_deviation_method}`} /><Value label="Orders · recent / reference" value={`${num(d.recent_order_count)} / ${num(d.reference_order_count)}`} />
            <Value label="Purchase-rate ratio · raw" value={`${num(d.purchase_rate_ratio)} · ${num(d.raw_purchase_rate_ratio)}`} /><Value label="Revenue-rate ratio" value={num(d.revenue_rate_ratio)} />
            <Value label="Recent / reference revenue" value={`${money(d.recent_gross_revenue)} / ${money(d.reference_gross_revenue)}`} /><Value label="EWMA gap change" value={`${num(d.ewma_gap_change_days)} days`} />
            <Value label="Personalized delay ratio" value={num(d.personalized_delay_ratio)} /><Value label="Available indicators" value={`${d.available_indicator_count}`} />
          </div>
          <div className="behavior-profile-probabilities"><span>Historical purchase probabilities</span><strong>30d {pct(d.purchase_probability_30d)}</strong><strong>60d {pct(d.purchase_probability_60d)}</strong><strong>90d {pct(d.purchase_probability_90d)}</strong></div>
          <p className="tiny">Policy {d.policy_version} · {d.policy_status} · cutoff {date(d.cutoff_date)} · {d.history_sufficiency} history sufficiency</p>
          {d.indicator_explanations.length > 0 && <ul className="behavior-explanations">{d.indicator_explanations.map((x, i) => <li key={`${i}-${x}`}>{x}</li>)}</ul>}
          {d.alert_reasons.length === 0 && <p className="tiny">No alert reasons are defined because a validated alert policy is not available.</p>}
        </>}
      </Panel>
      <Panel title="Purchase trajectory" note="Observed order and revenue rates across the historical window">
        {trajectory.isLoading ? <div className="skeleton" /> : trajectory.isError ? <div className="error-box">Trajectory could not be loaded. <button className="button secondary" onClick={() => void trajectory.refetch()}>Try again</button></div> : trajectory.data?.items.length ? <><div className="tiny">Window {trajectory.data.window_days} days · cutoff {date(trajectory.data.cutoff_date)}</div><div className="chart-wrap"><ResponsiveContainer><AreaChart data={trajectory.data.items}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="period_start" tick={{ fontSize: 8, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 8, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip /><Area type="monotone" dataKey="order_rate" name="Order rate" stroke="#315a4c" fill="#d8e2d8" /><Area type="monotone" dataKey="revenue_rate" name="Revenue rate" stroke="#c57d5c" fill="#f3e4d8" /></AreaChart></ResponsiveContainer></div><div className="table-scroll"><table><thead><tr><th>Period</th><th>Orders</th><th>Gross revenue</th><th>Exposure days</th></tr></thead><tbody>{trajectory.data.items.map((x) => <tr key={`${x.period_start}-${x.period_end}`}><td>{date(x.period_start)}–{date(x.period_end)}</td><td className="number">{num(x.order_count)}</td><td className="number">{money(x.gross_revenue)}</td><td className="number">{num(x.observed_exposure_days)}</td></tr>)}</tbody></table></div></> : <div className="empty-box">No historical trajectory points are available.</div>}
      </Panel>
    </div>}
    <div style={{ marginTop: 16 }}>
      <Panel title="Validation evidence" note="Actual saved model comparison results and paired-bootstrap uncertainty intervals">
        <State query={evaluation} empty={!evaluation.data}>{evaluation.data && <>
          <div className="filter-row"><span className="badge neutral">Result: {evaluation.data.result_status}</span><span className="badge neutral">Candidate F: {evaluation.data.candidate_f_status.startsWith('not_fitted') ? 'not fitted' : evaluation.data.candidate_f_status}</span><span className="tiny">Test cutoff {date(evaluation.data.test_cutoff_date)} · evaluation {evaluation.data.evaluation_version}</span></div>
          {evaluation.data.candidate_f_status.startsWith('not_fitted') && <p className="tiny">No saved Purchase Clock probability was available at the official TRAIN cutoffs, so conditional Candidate F was not fitted.</p>}
          {!!evaluation.data.selection_results.length && <details className="behavior-results-details"><summary>Validation-selected settings</summary><div className="table-scroll"><table><thead><tr><th>Horizon</th><th>EWMA λ</th><th>Regularization C</th><th>Validation AP</th><th>Validation Brier</th><th>Validation customers</th></tr></thead><tbody>{evaluation.data.selection_results.map((selection) => <tr key={selection.horizon_days}><td>{selection.horizon_days}d</td><td className="number">{num(selection.selected_ewma_lambda)}</td><td className="number">{num(selection.selected_regularization_c)}</td><td className="number">{num(selection.validation_average_precision)}</td><td className="number">{num(selection.validation_brier_score)}</td><td className="number">{num(selection.validation_customers)}</td></tr>)}</tbody></table></div></details>}
          {evaluation.data.model_comparison.length ? <div className="table-scroll"><table><thead><tr><th>Horizon</th><th>Model</th><th>Customers</th><th>ROC AUC</th><th>Avg. precision</th><th>Precision @ top 10%</th><th>Recall @ top 10%</th><th>Brier</th><th>Log loss</th><th>Top 10% coverage</th><th>Top 10% false-alert rate</th><th>VAL threshold</th><th>Frozen coverage</th><th>Frozen false-alert rate</th><th>Status</th></tr></thead><tbody>{evaluation.data.model_comparison.map((m, i) => <tr key={`${m.horizon_days}-${m.model}-${i}`}><td>{m.horizon_days}d</td><td>{m.model}</td><td className="number">{num(m.n_customers)}</td><td className="number">{num(m.roc_auc)}</td><td className="number">{num(m.average_precision)}</td><td className="number">{num(m.precision_at_budget)}</td><td className="number">{num(m.recall_at_budget)}</td><td className="number">{num(m.brier_score)}</td><td className="number">{num(m.log_loss)}</td><td className="number">{pct(m.alert_coverage)}</td><td className="number">{pct(m.false_alert_rate)}</td><td className="number">{num(m.threshold)}</td><td className="number">{pct(m.frozen_threshold_alert_coverage)}</td><td className="number">{pct(m.frozen_threshold_false_alert_rate)}</td><td><span className="badge neutral">{m.status.startsWith('not_fitted') ? 'Not fitted · vintage unavailable' : m.status}</span></td></tr>)}</tbody></table></div> : <div className="empty-box">No model comparison metrics are present.</div>}
          {evaluation.data.bootstrap_comparisons.length > 0 && <div className="table-scroll" style={{ marginTop: 12 }}><table><thead><tr><th>Horizon</th><th>Comparison</th><th>Metric</th><th>Difference</th><th>95% paired interval</th><th>Valid / requested resamples</th><th>Customer clusters</th></tr></thead><tbody>{evaluation.data.bootstrap_comparisons.map((b, i) => <tr key={`${b.horizon_days}-${b.comparison}-${i}`}><td>{b.horizon_days}d</td><td>{b.comparison}</td><td>{b.metric}</td><td className="number">{num(b.difference_first_minus_second)}</td><td className="number">[{num(b.confidence_interval_95_lower)}, {num(b.confidence_interval_95_upper)}]</td><td className="number">{b.valid_resamples} / {b.requested_resamples}</td><td className="number">{b.customer_clusters}</td></tr>)}</tbody></table></div>}
          {!!evaluation.data.subgroup_results.length && <details className="behavior-results-details"><summary>Subgroup results by history sufficiency and saved segment</summary><div className="table-scroll"><table><thead><tr><th>Horizon</th><th>Model</th><th>Grouping</th><th>Group</th><th>Customers</th><th>No-purchase rate</th><th>ROC AUC</th><th>Avg. precision</th><th>Status</th></tr></thead><tbody>{evaluation.data.subgroup_results.map((subgroup, i) => <tr key={`${subgroup.horizon_days}-${subgroup.model}-${subgroup.group_type}-${subgroup.group}-${i}`}><td>{subgroup.horizon_days}d</td><td>{subgroup.model}</td><td>{subgroup.group_type.replaceAll('_', ' ')}</td><td>{subgroup.group}</td><td className="number">{num(subgroup.n_customers)}</td><td className="number">{pct(subgroup.nonpurchase_rate)}</td><td className="number">{num(subgroup.roc_auc)}</td><td className="number">{num(subgroup.average_precision)}</td><td>{subgroup.status}</td></tr>)}</tbody></table></div></details>}
          {!!evaluation.data.hypotheses.length && <div className="grid two behavior-hypotheses">{evaluation.data.hypotheses.map((h) => <div className="behavior-hypothesis" key={h.hypothesis}><strong>{h.hypothesis} · {h.status}</strong><p>{h.statement}</p><span>{h.evidence_summary}</span></div>)}</div>}
          {!!evaluation.data.limitations.length && <div className="behavior-limitations"><strong>Limitations</strong><ul>{evaluation.data.limitations.map((x, i) => <li key={`${i}-${x}`}>{x}</li>)}</ul></div>}
        </>}</State>
      </Panel>
    </div>
  </div>;
}

function Value({ label, value }: { label: string; value: string }) {
  return <div className="behavior-value"><span>{label}</span><strong className="number">{value}</strong></div>;
}
