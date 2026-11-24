import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { AlertTriangle, ArrowUpRight, Crosshair, Gauge, Layers3, ShieldCheck, Users, Wallet } from 'lucide-react';
import { CartesianGrid, Legend, Line, LineChart, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis, ResponsiveContainer } from 'recharts';
import {
  getGetRevenueExposureConcentrationQueryKey, getGetRevenueExposureCustomersQueryKey,
  getGetRevenueExposureCustomerQueryKey, getGetRevenueExposureEvaluationQueryKey,
  getGetRevenueExposureScatterQueryKey, getGetRevenueExposureSummaryQueryKey,
  useGetRevenueExposureConcentration, useGetRevenueExposureCustomers,
  useGetRevenueExposureCustomer, useGetRevenueExposureEvaluation, useGetRevenueExposureScatter,
  useGetRevenueExposureSummary, usePostRetentionScenario, usePostRetentionStrategyComparison,
} from '@workspace/api-client-react';
import type { RetentionScenarioInput, RetentionScenarioRequest, RetentionScenarioRequestRankingStrategy } from '@workspace/api-client-react';

type Horizon = 30 | 60 | 90;
const strategies: RetentionScenarioRequestRankingStrategy[] = ['historical_gross_spending', 'recency_only', 'nonreturn_probability', 'conditional_expected_spending', 'nonreturn_spending_proxy', 'pareto_risk_value'];
const scatterPalette = ['#ca795c', '#527963', '#b39a54', '#7a8fac', '#9c7180', '#788e79', '#ab7b4f'];
const strategyLabels: Record<string, string> = {
  historical_gross_spending: 'Historical gross spend', recency_only: 'Recency', nonreturn_probability: 'Nonreturn probability',
  conditional_expected_spending: 'Conditional spend', nonreturn_spending_proxy: 'Nonreturn × spend proxy', pareto_risk_value: 'Pareto risk/value',
};
const fmtMoney = (value?: number | null) => value == null || !Number.isFinite(value) ? 'Not estimable' : new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(value);
const fmtNumber = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 }).format(value);
const fmtPct = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : `${(value * 100).toFixed(1)}%`;
const safeDate = (value?: string | null) => value ? new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';
const isRecord = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);

function Metric({ label, value, caption, icon: Icon }: { label: string; value: string; caption: string; icon: typeof Wallet }) {
  return <article className="exposure-metric" data-testid={`metric-${label.toLowerCase().replaceAll(' ', '-')}`}><div className="exposure-metric-top"><span>{label}</span><Icon size={16} /></div><strong>{value}</strong><small>{caption}</small></article>;
}
function RecordGrid({ data }: { data: unknown }) {
  if (!isRecord(data) || Object.keys(data).length === 0) return <div className="exposure-empty">No saved evaluation evidence was returned.</div>;
  return <dl className="exposure-records">{Object.entries(data).map(([key, value]) => <div key={key}><dt>{key.replaceAll('_', ' ')}</dt><dd>{isRecord(value) ? JSON.stringify(value) : Array.isArray(value) ? value.join(', ') : String(value ?? '—')}</dd></div>)}</dl>;
}
function ScenarioContacts({ items }: { items: Array<Record<string, unknown>> }) {
  if (!items.length) return <div className="exposure-empty">No customers fit the submitted budget and filters.</div>;
  return <div className="table-scroll"><table data-testid="table-scenario-contacts"><thead><tr><th>Customer</th><th>Segment</th><th>Purchase probability</th><th>Conditional spending</th><th>Hypothetical incremental revenue</th></tr></thead><tbody>{items.slice(0, 10).map((item, index) => <tr key={String(item.customer_id ?? index)} data-testid={`row-scenario-contact-${String(item.customer_id ?? index)}`}><td className="number">{String(item.customer_id ?? '—')}</td><td>{String(item.hist_segment ?? '—')}</td><td className="number">{fmtPct(typeof item.purchase_probability === 'number' ? item.purchase_probability : null)}</td><td className="number">{fmtMoney(typeof item.conditional_expected_spending_gbp === 'number' ? item.conditional_expected_spending_gbp : null)}</td><td className="number">{fmtMoney(typeof item.hypothetical_incremental_revenue_gbp === 'number' ? item.hypothetical_incremental_revenue_gbp : null)}</td></tr>)}</tbody></table>{items.length > 10 && <p className="exposure-chart-note">Showing the first 10 of {items.length} selected customers.</p>}</div>;
}

export default function RevenueExposurePage() {
  const initialQuery = new URLSearchParams(window.location.search);
  const initialHorizon = Number(initialQuery.get('horizon_days'));
  const [horizon, setHorizon] = useState<Horizon>(initialHorizon === 60 || initialHorizon === 90 ? initialHorizon : 30);
  const [ranking, setRanking] = useState<RetentionScenarioRequestRankingStrategy>('nonreturn_spending_proxy');
  const [historySufficiency, setHistorySufficiency] = useState('');
  const [historyGroup, setHistoryGroup] = useState('');
  const [segment, setSegment] = useState('');
  const [search, setSearch] = useState(initialQuery.get('customer_id') ?? '');
  const [sortBy, setSortBy] = useState('priority_rank');
  const [sortDescending, setSortDescending] = useState(false);
  const [behaviorFilter, setBehaviorFilter] = useState('none');
  const [requireHistory, setRequireHistory] = useState(false);
  const [page, setPage] = useState(1);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [budget, setBudget] = useState('');
  const [contactCost, setContactCost] = useState('');
  const [maximumContacts, setMaximumContacts] = useState('');
  const [responseProbability, setResponseProbability] = useState('');
  const [purchaseUplift, setPurchaseUplift] = useState('');
  const [margin, setMargin] = useState('');
  const [comparison, setComparison] = useState(false);
  const [resultMode, setResultMode] = useState<'scenario' | 'comparison'>('scenario');
  const [formError, setFormError] = useState('');
  const summaryParams = useMemo(() => ({ horizon_days: horizon }), [horizon]);
  const customerParams = useMemo(() => ({
    horizon_days: horizon, page, page_size: 12, ranking_strategy: ranking,
    search: search || undefined, sort_by: sortBy as 'priority_rank' | 'customer_id' | 'recency_days' | 'purchase_probability' | 'conditional_expected_spending_gbp' | 'personalized_expected_revenue_gbp' | 'nonreturn_weighted_conditional_spending_proxy_gbp' | 'historical_gross_spending_gbp',
    sort_descending: sortDescending,
    hist_segment: segment || undefined, history_group: historyGroup || undefined,
    history_sufficiency: historySufficiency ? historySufficiency as 'sufficient' | 'limited' | 'insufficient' : undefined,
    require_sufficient_behavior_history: requireHistory || undefined,
    behavior_filter: behaviorFilter as 'none' | 'declining_purchase_rate' | 'declining_revenue_rate',
  }), [horizon, page, ranking, search, sortBy, sortDescending, segment, historyGroup, historySufficiency, requireHistory, behaviorFilter]);
  const summary = useGetRevenueExposureSummary(summaryParams, { query: { queryKey: getGetRevenueExposureSummaryQueryKey(summaryParams) } });
  const customers = useGetRevenueExposureCustomers(customerParams, { query: { queryKey: getGetRevenueExposureCustomersQueryKey(customerParams) } });
  const scatterParams = useMemo(() => ({
    horizon_days: horizon, limit: 300, hist_segment: segment || undefined,
    history_sufficiency: historySufficiency ? historySufficiency as 'sufficient' | 'limited' | 'insufficient' : undefined,
  }), [horizon, segment, historySufficiency]);
  const scatter = useGetRevenueExposureScatter(scatterParams, { query: { queryKey: getGetRevenueExposureScatterQueryKey(scatterParams) } });
  const concentrationParams = useMemo(() => ({ horizon_days: horizon }), [horizon]);
  const concentration = useGetRevenueExposureConcentration(concentrationParams, { query: { queryKey: getGetRevenueExposureConcentrationQueryKey(concentrationParams) } });
  const evaluation = useGetRevenueExposureEvaluation({ query: { queryKey: getGetRevenueExposureEvaluationQueryKey() } });
  const detailParams = useMemo(() => ({ horizon_days: horizon }), [horizon]);
  const detail = useGetRevenueExposureCustomer(selectedId ?? 0, detailParams, { query: { queryKey: getGetRevenueExposureCustomerQueryKey(selectedId ?? 0, detailParams), enabled: selectedId !== null } });
  const scenarioMutation = usePostRetentionScenario();
  const comparisonMutation = usePostRetentionStrategyComparison();
  const s = summary.data;
  const pageData = customers.data;
  const selected = detail.data;
  const selectedCandidate = pageData?.items.find((candidate) => candidate.customer_id === selectedId);
  const scatterGroups = useMemo(() => {
    const points = scatter.data?.points ?? [];
    const segments = [...new Set(points.map((point) => point.hist_segment ?? 'Unassigned'))];
    return segments.map((label, index) => ({
      label,
      color: scatterPalette[index % scatterPalette.length],
      points: points.filter((point) => (point.hist_segment ?? 'Unassigned') === label),
    }));
  }, [scatter.data?.points]);
  const sensitivitySeries = useMemo(() => {
    const source = evaluation.data?.scenario_sensitivity;
    const rows = isRecord(source) && Array.isArray(source.scenario_results)
      ? source.scenario_results.filter(isRecord)
      : [];
    const matching = rows.filter((row) =>
      Number(row.horizon_days) === horizon &&
      row.ranking_strategy === ranking
    );
    const nearest = (values: number[], target: number) =>
      values.reduce((best, value) => Math.abs(value - target) < Math.abs(best - target) ? value : best, values[0] ?? target);
    const targetBudget = Number.isFinite(Number(budget)) && budget.trim() ? Number(budget) : 500;
    const targetCost = Number.isFinite(Number(contactCost)) && contactCost.trim() ? Number(contactCost) : 3;
    const budgetOptions = [...new Set(matching.map((row) => Number(row.campaign_budget_gbp)).filter(Number.isFinite))];
    const costOptions = [...new Set(matching.map((row) => Number(row.contact_cost_gbp)).filter(Number.isFinite))];
    const chosenBudget = nearest(budgetOptions, targetBudget);
    const chosenCost = nearest(costOptions, targetCost);
    const filtered = matching.filter((row) =>
      Number(row.campaign_budget_gbp) === chosenBudget &&
      Number(row.contact_cost_gbp) === chosenCost
    );
    const byResponse = new Map<number, Record<string, number>>();
    for (const row of filtered) {
      const response = Number(row.assumed_response_probability);
      const uplift = Math.round(Number(row.assumed_purchase_uplift_if_responded) * 100);
      const revenue = Number(row.hypothetical_incremental_revenue_gbp);
      if (!Number.isFinite(response) || !Number.isFinite(uplift) || !Number.isFinite(revenue)) continue;
      const point = byResponse.get(response) ?? { response_probability_percent: response * 100 };
      point[`uplift_${uplift}`] = revenue;
      byResponse.set(response, point);
    }
    return {
      rows: [...byResponse.values()].sort((a, b) => a.response_probability_percent - b.response_probability_percent),
      budget: chosenBudget,
      contactCost: chosenCost,
      uplifts: [...new Set(filtered.map((row) => Math.round(Number(row.assumed_purchase_uplift_if_responded) * 100)))].sort((a, b) => a - b),
    };
  }, [evaluation.data?.scenario_sensitivity, horizon, ranking, budget, contactCost]);
  const scenarioInput: RetentionScenarioInput = {
    horizon_days: horizon, campaign_budget_gbp: Number(budget), contact_cost_gbp: Number(contactCost),
    maximum_contacts: Number(maximumContacts), assumed_response_probability: Number(responseProbability),
    assumed_purchase_uplift_if_responded: Number(purchaseUplift),
    ...(margin.trim() ? { assumed_gross_margin_rate: Number(margin) } : {}),
  };
  const eligibilityFilters = {
    ...(segment ? { hist_segment: segment } : {}), ...(historyGroup ? { history_group: historyGroup } : {}),
    ...(historySufficiency ? { history_sufficiency: historySufficiency as 'sufficient' | 'limited' | 'insufficient' } : {}),
    ...(requireHistory ? { require_sufficient_behavior_history: true } : {}),
    ...(behaviorFilter !== 'none' ? { behavior_filter: behaviorFilter as 'declining_purchase_rate' | 'declining_revenue_rate' } : {}),
  };
  const submitScenario = (event: FormEvent) => {
    event.preventDefault();
    setFormError('');
    if ([budget, contactCost, maximumContacts, responseProbability, purchaseUplift].some((value) => value.trim() === '') || !Number.isFinite(scenarioInput.campaign_budget_gbp) || scenarioInput.campaign_budget_gbp < 0 || scenarioInput.contact_cost_gbp <= 0 || !Number.isFinite(scenarioInput.maximum_contacts) || scenarioInput.maximum_contacts < 0 || [scenarioInput.assumed_response_probability, scenarioInput.assumed_purchase_uplift_if_responded, scenarioInput.assumed_gross_margin_rate].some((v) => v != null && (!Number.isFinite(v) || v < 0 || v > 1))) {
      setFormError('Enter the budget, contact cost, contact limit and assumptions. Use non-negative budget and contacts, positive contact cost, and probabilities between 0 and 1.');
      return;
    }
    setResultMode(comparison ? 'comparison' : 'scenario');
    if (comparison) comparisonMutation.mutate({ data: { scenario: scenarioInput, ranking_strategies: strategies, eligibility_filters: eligibilityFilters } });
    else {
      const request: RetentionScenarioRequest = { ...scenarioInput, ranking_strategy: ranking, eligibility_filters: eligibilityFilters };
      scenarioMutation.mutate({ data: request });
    }
  };
  const exportRankingCsv = () => {
    if (!pageData?.items.length) return;
    const columns = [
      'customer_id', 'hist_segment', 'history_group', 'history_sufficiency',
      'purchase_probability', 'conditional_expected_spending_gbp',
      'personalized_expected_revenue_gbp',
      'nonreturn_weighted_conditional_spending_proxy_gbp',
      'estimated_revenue_exposure_gbp', 'reliability_status',
      'selection_eligible', 'priority_rank', 'priority_score',
    ] as const;
    const escape = (value: unknown) => `"${String(value ?? '').replaceAll('"', '""')}"`;
    const csv = `${columns.map(escape).join(',')}\n${pageData.items.map((item) => columns.map((column) => escape(item[column])).join(',')).join('\n')}\n`;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    link.download = `revenue-priority-${horizon}d-page-${page}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };
  const mutationError = scenarioMutation.isError || comparisonMutation.isError;
  const scenarioResult = scenarioMutation.data;
  const comparisonResult = comparisonMutation.data;
  const activeMutation = comparison ? comparisonMutation : scenarioMutation;
  const totalPages = pageData ? Math.max(1, Math.ceil(pageData.total / pageData.page_size)) : 1;

  return <main className="content revenue-page">
    <div className="exposure-heading">
      <div><div className="eyebrow">Historical portfolio research · OELP</div><h1>Revenue exposure &amp; retention planning</h1><p>Separate saved-model forecasts, observable risk evidence, and hypothetical contact planning. Every figure is anchored to a recorded historical cutoff.</p></div>
      <label className="exposure-horizon"><span>Forecast horizon</span><select value={horizon} onChange={(e) => { setHorizon(Number(e.target.value) as Horizon); setPage(1); setSelectedId(null); }} data-testid="select-exposure-horizon"><option value={30}>30 days</option><option value={60}>60 days</option><option value={90}>90 days</option></select></label>
    </div>
    <div className="exposure-disclosure" data-testid="disclosure-noncausal"><AlertTriangle size={18}/><div><strong>Historical, noncausal planning only.</strong> Nonreturn is an observed historical proxy—not proof of churn, preventable loss, or causal retention lift. Scenario outputs are hypothetical, not estimable treatment effects or recommendations.</div></div>
    {summary.isLoading ? <div className="exposure-skeleton"><i/><i/><i/><i/></div> : summary.isError ? <div className="error-box" role="alert">Revenue summary unavailable. <button className="button secondary" onClick={() => void summary.refetch()}>Retry</button></div> : s && <>
      <div className="exposure-kpis">
        <Metric label="Personalized forecast" value={fmtMoney(s.personalized_expected_revenue_total_gbp)} caption={`${fmtNumber(s.eligible_customers)} eligible · cutoff ${safeDate(s.cutoff_date)}`} icon={Wallet}/>
        <Metric label="Forecast disagreement" value={fmtMoney(s.historical_minus_personalized_forecast_difference_gbp)} caption={`Historical-rate difference · segment ${fmtMoney(s.segment_minus_personalized_forecast_difference_gbp)}`} icon={Layers3}/>
        <Metric label="Estimated exposure" value={fmtMoney(s.estimated_revenue_exposure_total_gbp)} caption={`${fmtPct(s.exposure_coverage)} coverage · ${s.exposure_status}`} icon={Crosshair}/>
        <Metric label="Nonreturn proxy" value={fmtMoney(s.opportunity_proxy_total_gbp)} caption="A prioritisation proxy, not recoverable revenue" icon={Gauge}/>
      </div>
      <section className="exposure-forecast-compare" data-testid="section-forecast-comparison"><div className="exposure-forecast-title"><div><strong>Three saved revenue views</strong><span>Same eligible cohort · {horizon}-day horizon</span></div><span>Cutoff {safeDate(s.cutoff_date)}</span></div>{([
        ['Personalized', s.personalized_expected_revenue_total_gbp, '#315a4c'],
        ['Historical rate', s.historical_rate_forecast_total_gbp, '#c47b5c'],
        ['Historical segment', s.segment_forecast_total_gbp, '#c9a459'],
      ] as [string, number, string][]).map(([label, value, color]) => {
        const max = Math.max(s.personalized_expected_revenue_total_gbp, s.historical_rate_forecast_total_gbp, s.segment_forecast_total_gbp, 1);
        return <div className="exposure-forecast-row" key={label}><span>{label}</span><div className="exposure-forecast-track"><i style={{ width: `${Math.max(2, value / max * 100)}%`, background: color }}/></div><strong>{fmtMoney(value)}</strong></div>;
      })}</section>
     <div className="exposure-evidence-line" data-testid="text-exposure-evidence"><span>Reliability evidence cutoff <b>{safeDate(s.reliability_evidence_cutoff)}</b></span><span>Customers with group evidence <b>{fmtNumber(s.reliability_group_coverage)}</b></span><span>Exposure method <b>{s.exposure_method ?? 'Not estimable'}</b></span></div>
    </>}
    <div className="exposure-grid">
       <section className="panel exposure-panel"><div className="panel-head"><div><div className="panel-title">Risk versus value</div><div className="panel-note">X: nonreturn probability · Y: conditional expected spending · color: historical segment</div></div><span className="exposure-tag">Saved outputs</span></div>
         {scatter.isLoading ? <div className="exposure-chart-skeleton"/> : scatter.isError ? <div className="empty-box">Scatter evidence unavailable.</div> : scatter.data?.points.length ? <div className="chart-wrap"><ResponsiveContainer><ScatterChart margin={{ top: 10, right: 16, bottom: 8, left: 12 }}><CartesianGrid stroke="#e7e3d8" strokeDasharray="3 4"/><XAxis type="number" dataKey="nonreturn_probability" name="Nonreturn probability" domain={[0, 1]} tickFormatter={(v) => fmtPct(Number(v))} tick={{ fontSize: 9, fill: '#75847b' }} axisLine={false} tickLine={false}/><YAxis type="number" dataKey="conditional_expected_spending_gbp" name="Conditional expected spending" tickFormatter={(v) => `£${v}`} tick={{ fontSize: 9, fill: '#75847b' }} axisLine={false} tickLine={false} width={50}/><ZAxis type="number" dataKey="historical_gross_spending_gbp" name="Historical gross spending" range={[32, 180]}/><Tooltip cursor={{ strokeDasharray: '3 3' }} content={({ active, payload }) => { const point = payload?.[0]?.payload as Record<string, unknown> | undefined; if (!active || !point) return null; return <div className="exposure-tooltip"><strong>Customer {String(point.customer_id ?? '—')}</strong><span>Purchase probability {fmtPct(typeof point.purchase_probability === 'number' ? point.purchase_probability : null)}</span><span>Conditional spend {fmtMoney(typeof point.conditional_expected_spending_gbp === 'number' ? point.conditional_expected_spending_gbp : null)}</span><span>Expected revenue {fmtMoney(typeof point.personalized_expected_revenue_gbp === 'number' ? point.personalized_expected_revenue_gbp : null)}</span><span>History {String(point.history_group ?? '—')}</span><span>Reliability {String(point.reliability_status ?? '—')}</span></div>; }}/><Legend verticalAlign="bottom" height={26} wrapperStyle={{ fontSize: 9 }}/>{scatterGroups.map((group) => <Scatter key={group.label} name={group.label} data={group.points} fill={group.color} fillOpacity={0.62} stroke={group.color} strokeWidth={0.5}/>)}</ScatterChart></ResponsiveContainer></div> : <div className="exposure-empty">No scatter points returned for this horizon.</div>}
        {scatter.data && <p className="exposure-chart-note">{scatter.data.interpretation}</p>}
      </section>
      <section className="panel exposure-panel"><div className="panel-head"><div><div className="panel-title">Concentration &amp; coverage</div><div className="panel-note">Portfolio share and evidence availability from API response</div></div><ShieldCheck size={17} color="#557866"/></div>
        {concentration.isLoading ? <div className="exposure-chart-skeleton"/> : concentration.isError ? <div className="exposure-empty">Concentration data unavailable.</div> : concentration.data?.items.length ? <div className="table-scroll"><table><thead><tr><th>Metric</th><th>Top share</th><th>Selected</th><th>Portfolio share</th><th>Status</th></tr></thead><tbody>{concentration.data.items.map((item, i) => <tr key={`${item.metric}-${i}`}><td>{item.metric.replaceAll('_', ' ')}</td><td className="number">{fmtPct(item.top_customer_share)}</td><td className="number">{fmtNumber(item.selected_customers)}</td><td className="number">{fmtPct(item.portfolio_share)}</td><td><span className="badge neutral">{item.status}</span></td></tr>)}</tbody></table></div> : <div className="exposure-empty">No concentration rows returned.</div>}
        {concentration.data && <p className="exposure-chart-note">{concentration.data.interpretation}</p>}
      </section>
    </div>
    <section className="panel exposure-panel exposure-customer-panel">
      <div className="panel-head"><div><div className="panel-title">Eligible customer ranking</div><div className="panel-note">API-ranked customer evidence. Missing exposure is shown as not estimable, never zero.</div></div><div className="exposure-header-actions"><span className="exposure-count"><Users size={14}/>{pageData ? `${fmtNumber(pageData.total)} records` : 'Loading records'}</span><button className="button secondary" onClick={exportRankingCsv} disabled={!pageData?.items.length} data-testid="button-export-exposure-csv">Export visible rows CSV</button></div></div>
      <div className="exposure-filters">
        <label><span>Ranking strategy</span><select value={ranking} onChange={(e) => { setRanking(e.target.value as RetentionScenarioRequestRankingStrategy); setPage(1); }} data-testid="select-exposure-ranking">{strategies.map((v) => <option key={v} value={v}>{strategyLabels[v]}</option>)}</select></label>
        <label><span>Search customer ID</span><input value={search} onChange={(e) => { setSearch(e.target.value.replace(/\D/g, '').slice(0, 32)); setPage(1); }} placeholder="All customers" inputMode="numeric" data-testid="input-exposure-search"/></label>
        <label><span>Sort table by</span><select value={sortBy} onChange={(e) => { setSortBy(e.target.value); setPage(1); }} data-testid="select-exposure-sort"><option value="priority_rank">Ranking priority</option><option value="customer_id">Customer ID</option><option value="purchase_probability">Purchase probability</option><option value="conditional_expected_spending_gbp">Conditional spending</option><option value="personalized_expected_revenue_gbp">Expected revenue</option><option value="nonreturn_weighted_conditional_spending_proxy_gbp">Nonreturn proxy</option><option value="historical_gross_spending_gbp">Historical gross spending</option><option value="recency_days">Recency</option></select></label>
        <button className="button secondary exposure-sort-toggle" onClick={() => { setSortDescending((value) => !value); setPage(1); }} data-testid="button-exposure-sort-direction">{sortDescending ? 'Descending' : 'Ascending'}</button>
        <label><span>History sufficiency</span><select value={historySufficiency} onChange={(e) => { setHistorySufficiency(e.target.value); setPage(1); }} data-testid="select-exposure-sufficiency"><option value="">All evidence levels</option><option value="sufficient">Sufficient</option><option value="limited">Limited</option><option value="insufficient">Insufficient</option></select></label>
        <label><span>History group</span><select value={historyGroup} onChange={(e) => { setHistoryGroup(e.target.value); setPage(1); }} data-testid="select-exposure-history-group"><option value="">All groups</option><option>Exactly one purchase</option><option>Two to four purchases</option><option>Five or more purchases</option></select></label>
        <label><span>Historical segment</span><input value={segment} onChange={(e) => { setSegment(e.target.value); setPage(1); }} placeholder="Any segment" data-testid="input-exposure-segment"/></label>
        <label><span>Behavior signal</span><select value={behaviorFilter} onChange={(e) => { setBehaviorFilter(e.target.value); setPage(1); }} data-testid="select-exposure-behavior"><option value="none">No decline filter</option><option value="declining_purchase_rate">Declining purchase rate</option><option value="declining_revenue_rate">Declining revenue rate</option></select></label>
        <label className="exposure-check"><input type="checkbox" checked={requireHistory} onChange={(e) => setRequireHistory(e.target.checked)} data-testid="check-exposure-sufficient-behavior"/>Require sufficient behavior history</label>
      </div>
      {customers.isLoading ? <div className="exposure-table-skeleton"/> : customers.isError ? <div className="error-box">Customer ranking unavailable. <button className="button secondary" onClick={() => void customers.refetch()}>Retry</button></div> : pageData?.items.length ? <>
         <div className="table-scroll"><table data-testid="table-exposure-customers"><thead><tr><th>Rank</th><th>Customer</th><th>History</th><th>Recency</th><th>Purchase</th><th>Nonreturn proxy</th><th>Personalized</th><th>Exposure</th><th>Reliability evidence</th><th>Eligibility</th><th></th></tr></thead><tbody>{pageData.items.map((c, i) => <tr key={c.customer_id} data-testid={`row-exposure-customer-${c.customer_id}`} className={selectedId === c.customer_id ? 'exposure-selected' : ''}><td className="number">{c.priority_rank ?? (page - 1) * pageData.page_size + i + 1}</td><td className="number">{c.customer_id}</td><td>{c.history_sufficiency ?? '—'}<small className="exposure-cell-sub">{c.history_group ?? c.hist_segment ?? '—'}</small></td><td className="number">{fmtNumber(c.recency_days)}d</td><td className="number">{fmtPct(c.purchase_probability)}</td><td className="number">{fmtMoney(c.nonreturn_weighted_conditional_spending_proxy_gbp)}</td><td className="number">{fmtMoney(c.personalized_expected_revenue_gbp)}</td><td className="number">{fmtMoney(c.estimated_revenue_exposure_gbp)}</td><td><span className={`badge ${c.reliability_status === 'evaluated' ? '' : 'warn'}`}>{c.reliability_status}</span><small className="exposure-cell-sub">{fmtNumber(c.reliability_evidence_count)} grouped records</small></td><td><span className={`badge ${c.selection_eligible ? '' : 'warn'}`}>{c.selection_eligible ? 'Eligible' : 'Filtered out'}</span></td><td><button className="button secondary exposure-open" onClick={() => setSelectedId(c.customer_id)} data-testid={`button-exposure-detail-${c.customer_id}`}>Inspect</button></td></tr>)}</tbody></table></div>
        <div className="exposure-pagination"><span>Page {page} of {totalPages} · API strategy: {strategyLabels[pageData.ranking_strategy] ?? pageData.ranking_strategy}</span><div><button className="button secondary" disabled={page <= 1 || customers.isFetching} onClick={() => setPage(page - 1)} data-testid="button-exposure-previous">Previous</button><button className="button secondary" disabled={page >= totalPages || customers.isFetching} onClick={() => setPage(page + 1)} data-testid="button-exposure-next">Next</button></div></div>
      </> : <div className="exposure-empty">No eligible customers match these evidence filters.</div>}
       {selectedId !== null && <div className="exposure-detail" data-testid="panel-exposure-detail"><div className="panel-head"><div><div className="panel-title">Customer {selectedId} · {horizon}-day detail</div><div className="panel-note">Historical cutoff detail, model disagreement, reliability group context, and returned limitations</div></div><button className="button ghost" onClick={() => setSelectedId(null)} data-testid="button-close-exposure-detail">Close</button></div>{detail.isLoading ? <div className="exposure-chart-skeleton"/> : detail.isError ? <div className="error-box">Customer detail unavailable. <button className="button secondary" onClick={() => void detail.refetch()}>Retry</button></div> : selected ? <><div className="exposure-detail-grid"><span>Cutoff <b>{safeDate(selected.cutoff_date)}</b></span><span>Group <b>{selected.history_group ?? '—'}</b></span><span>Personalized revenue <b>{fmtMoney(selected.personalized_expected_revenue_gbp)}</b></span><span>Historical-rate forecast <b>{fmtMoney(selected.historical_rate_expected_revenue_gbp)}</b></span><span>Segment-aware forecast <b>{fmtMoney(selected.segment_expected_revenue_gbp)}</b></span><span>Nonreturn probability <b>{fmtPct(selected.nonreturn_probability)}</b></span><span>Exposure <b>{fmtMoney(selected.estimated_revenue_exposure_gbp)}</b></span><span>Reliability group Brier <b>{fmtNumber(selected.reliability_group_brier_score)}</b></span><span>Calibration gap <b>{fmtPct(selected.reliability_group_calibration_gap)}</b></span><span>Evidence count <b>{fmtNumber(selected.reliability_evidence_count)}</b></span><span>Scenario eligibility <b>{selectedCandidate?.selection_eligible ? 'Eligible under active filters' : 'Recheck against active filters'}</b></span></div><ul className="exposure-limitations">{selected.limitations.map((text, i) => <li key={i}>{text}</li>)}</ul><p className="exposure-causal-note">Group reliability is not an individual guarantee. Nonreturn-weighted spend is a proxy, not an estimate of preventable loss.</p></> : <div className="exposure-empty">No detail record returned.</div>}</div>}
    </section>
     <section className="exposure-planner">
      <div className="exposure-planner-intro"><div className="eyebrow">Hypothetical outreach design</div><h2>Set a contact envelope</h2><p>Change assumptions, submit one scenario, or compare the same budget across supported API ranking strategies. No contact is sent.</p><div className="exposure-planner-note" data-testid="disclosure-scenario-noncausal">Scenario values are assumptions supplied by the analyst. Historical nonpurchase is not causal retention lift.</div></div>
      <div className="panel exposure-form-panel">
        <form onSubmit={submitScenario} className="exposure-form">
          <label><span>Campaign budget · GBP</span><input type="number" min="0" step="0.01" value={budget} onChange={(e) => setBudget(e.target.value)} data-testid="input-scenario-budget"/></label>
          <label><span>Cost per contact · GBP</span><input type="number" min="0.01" step="0.01" value={contactCost} onChange={(e) => setContactCost(e.target.value)} data-testid="input-scenario-contact-cost"/></label>
          <label><span>Maximum contacts</span><input type="number" min="0" step="1" value={maximumContacts} onChange={(e) => setMaximumContacts(e.target.value)} data-testid="input-scenario-maximum-contacts"/></label>
          <label><span>Assumed response probability</span><input type="number" min="0" max="1" step="0.01" value={responseProbability} onChange={(e) => setResponseProbability(e.target.value)} data-testid="input-scenario-response"/></label>
          <label><span>Purchase uplift if responded</span><input type="number" min="0" max="1" step="0.01" value={purchaseUplift} onChange={(e) => setPurchaseUplift(e.target.value)} data-testid="input-scenario-uplift"/></label>
          <label><span>Assumed gross margin · optional</span><input type="number" min="0" max="1" step="0.01" value={margin} onChange={(e) => setMargin(e.target.value)} data-testid="input-scenario-margin"/></label>
          <label className="exposure-scenario-ranking"><span>Rank eligible customers by</span><select value={ranking} onChange={(e) => setRanking(e.target.value as RetentionScenarioRequestRankingStrategy)} data-testid="select-scenario-ranking">{strategies.map((v) => <option key={v} value={v}>{strategyLabels[v]}</option>)}</select></label>
          <label className="exposure-compare-toggle"><input type="checkbox" checked={comparison} onChange={(e) => setComparison(e.target.checked)} data-testid="check-scenario-compare"/>Compare all six strategies</label>
          {formError && <div className="exposure-form-error" role="alert">{formError}</div>}
          <button type="submit" className="button exposure-submit" disabled={activeMutation.isPending} data-testid="button-submit-scenario">{activeMutation.isPending ? 'Calculating scenario…' : comparison ? 'Compare strategies' : 'Run hypothetical scenario'}<ArrowUpRight size={14}/></button>
        </form>
         {(scenarioMutation.isSuccess || comparisonMutation.isSuccess || mutationError) && <div className="exposure-result" data-testid="result-scenario">
           {mutationError ? <div className="error-box">Scenario could not be calculated. <button className="button secondary" onClick={() => resultMode === 'comparison' ? comparisonMutation.reset() : scenarioMutation.reset()}>Dismiss</button></div> : resultMode === 'scenario' && scenarioResult ? <><div className="exposure-result-head"><div><span>Hypothetical incremental revenue</span><strong>{fmtMoney(scenarioResult.hypothetical_incremental_revenue_gbp)}</strong></div><span className="badge warn">Noncausal</span></div><div className="exposure-result-stats"><span>{fmtNumber(scenarioResult.selected_customer_count)} selected</span><span>Campaign cost {fmtMoney(scenarioResult.campaign_cost_gbp)}</span><span>Remaining {fmtMoney(scenarioResult.budget_remaining_gbp)}</span><span>Utilization {fmtPct(scenarioResult.budget_utilization)}</span><span>Contribution {fmtMoney(scenarioResult.hypothetical_incremental_contribution_gbp)}</span></div><details className="exposure-assumptions"><summary>Assumptions used</summary><RecordGrid data={scenarioResult.assumptions}/></details><details className="exposure-assumptions"><summary>Break-even analysis</summary><RecordGrid data={scenarioResult.break_even_information}/></details><ScenarioContacts items={scenarioResult.selected_customers}/><p>{scenarioResult.limitations.join(' ')}</p></> : resultMode === 'comparison' && comparisonResult ? <><div className="panel-title">Strategy comparison · same assumptions</div><details className="exposure-assumptions"><summary>Shared assumptions</summary><RecordGrid data={comparisonResult.scenario_assumptions}/></details><div className="table-scroll"><table data-testid="table-strategy-comparison"><thead><tr><th>Ranking strategy</th><th>Selected</th><th>Cost</th><th>Utilization</th><th>Hypothetical revenue</th><th>Contribution</th><th>Break-even status</th></tr></thead><tbody>{comparisonResult.strategy_results.map((r) => <tr key={r.ranking_strategy}><td>{strategyLabels[r.ranking_strategy] ?? r.ranking_strategy}</td><td className="number">{fmtNumber(r.selected_customer_count)}<small className="exposure-cell-sub">IDs: {r.selected_customers.slice(0, 5).map((customer) => String(customer.customer_id ?? '—')).join(', ')}</small></td><td className="number">{fmtMoney(r.campaign_cost_gbp)}</td><td className="number">{fmtPct(r.budget_utilization)}</td><td className="number">{fmtMoney(r.hypothetical_incremental_revenue_gbp)}</td><td className="number">{fmtMoney(r.hypothetical_incremental_contribution_gbp)}</td><td>{String(r.break_even_information.status ?? 'Not estimable')}</td></tr>)}</tbody></table></div><p>{comparisonResult.interpretation}</p><p className="exposure-causal-note">All rows are hypothetical and noncausal; they do not estimate treatment effects.</p></> : null}
        </div>}
      </div>
    </section>
    <section className="panel exposure-panel exposure-sensitivity" data-testid="section-scenario-sensitivity"><div className="panel-head"><div><div className="panel-title">Illustrative scenario sensitivity</div><div className="panel-note">Saved grid · nearest budget {fmtMoney(sensitivitySeries.budget)} · contact cost {fmtMoney(sensitivitySeries.contactCost)} · {horizon} days · {strategyLabels[ranking]}</div></div><span className="badge warn">Assumptions, not estimates</span></div>
      {sensitivitySeries.rows.length ? <div className="chart-wrap"><ResponsiveContainer><LineChart data={sensitivitySeries.rows} margin={{ top: 8, right: 15, bottom: 6, left: 10 }}><CartesianGrid stroke="#e7e3d8" strokeDasharray="3 4"/><XAxis dataKey="response_probability_percent" name="Assumed response probability" tickFormatter={(value) => `${value}%`} tick={{ fontSize: 9, fill: '#75847b' }} axisLine={false} tickLine={false}/><YAxis tickFormatter={(value) => `£${Number(value).toLocaleString('en-GB')}`} tick={{ fontSize: 9, fill: '#75847b' }} axisLine={false} tickLine={false} width={68}/><Tooltip formatter={(value) => [fmtMoney(Number(value)), 'Hypothetical revenue']} labelFormatter={(value) => `Assumed response ${value}%`}/><Legend verticalAlign="bottom" height={26} wrapperStyle={{ fontSize: 9 }}/>{sensitivitySeries.uplifts.map((uplift, index) => <Line key={uplift} type="monotone" dataKey={`uplift_${uplift}`} name={`${uplift}% uplift if responded`} stroke={scatterPalette[index % scatterPalette.length]} strokeWidth={2} dot={{ r: 3 }}/>)}</LineChart></ResponsiveContainer></div> : <div className="exposure-empty">Saved scenario sensitivity results are unavailable for this selection.</div>}
      <p className="exposure-chart-note">The chart reports hypothetical gross revenue from the precomputed grid. It does not show observed campaign outcomes or causal lift.</p>
    </section>
    <section className="panel exposure-evaluation"><div className="panel-head"><div><div className="panel-title">Reliability &amp; method record</div><div className="panel-note">Saved evaluation evidence and declared limitations</div></div><ShieldCheck size={17} color="#557866"/></div>
      {evaluation.isLoading ? <div className="exposure-table-skeleton"/> : evaluation.isError ? <div className="exposure-empty">Evaluation record unavailable.</div> : evaluation.data ? <><div className="exposure-eval-grid"><div><h3>Financial definitions</h3><RecordGrid data={evaluation.data.financial_definitions}/></div><div><h3>Ranking selection &amp; validation record</h3><RecordGrid data={evaluation.data.ranking_selection_and_test_evaluation}/></div></div><div className="exposure-limitations"><strong>Evaluation limitations</strong><ul>{evaluation.data.limitations.map((item, i) => <li key={i}>{item}</li>)}</ul></div></> : <div className="exposure-empty">No evaluation record returned.</div>}
    </section>
  </main>;
}
