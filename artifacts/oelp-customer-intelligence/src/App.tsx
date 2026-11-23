import { useMemo, useState } from 'react';
import type { FormEvent, ReactNode, ElementType } from 'react';
import { BrowserRouter, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  Activity, AlertCircle, ArrowDownToLine, ArrowLeftRight, BarChart3, Clock3, Database, FileSpreadsheet, Filter,
  History, LayoutDashboard, LoaderCircle, Search, ShieldCheck, ShoppingBag, Sparkles,
  Users, UploadCloud, UserRoundSearch, Wallet,
} from 'lucide-react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, ComposedChart, Legend,
  Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import {
  getGetApiHealthQueryKey, getHealthCheckQueryKey, getGetCalibration90dImageQueryKey, getGetCalibrationImageQueryKey,
  getGetCustomerForecastQueryKey, getGetCustomerHistoryQueryKey, getGetCustomerQueryKey,
  getGetCustomersQueryKey, getGetForecastSummaryQueryKey, getGetModelPerformanceQueryKey,
  getGetOverviewQueryKey, getGetSegmentsQueryKey,
  useAnalyzeUpload, useExportUpload, useGetApiHealth, useGetCalibration90dImage,
  useGetCalibrationImage, useGetCustomer, useGetCustomerForecast, useGetCustomerHistory,
  useGetCustomers, useGetForecastSummary, useGetModelPerformance, useGetOverview,
  useGetSegments, useHealthCheck, usePreviewUpload,
} from '@workspace/api-client-react';
import type { CustomerListItem, GetCustomersHistoryGroup, UploadAnalysis, UploadPreview } from '@workspace/api-client-react';
import BehaviorPage from './BehaviorPage';
import BehaviorHistory from './BehaviorHistory';
import './index.css';

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });
const money = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(value);
const number = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 }).format(value);
const percent = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : `${(value * 100).toFixed(1)}%`;
const dateShort = (value?: string | null) => value ? new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) : '—';
const COLORS = ['#315a4c', '#d8ad5e', '#c57d5c', '#78918a', '#a8ad78', '#b9757d', '#789eb0'];

function HistoricalNotice() {
  return <div className="historical-banner" data-testid="notice-historical-demonstration"><History size={15} /><span><strong>Historical demonstration only.</strong> Forecasts below reproduce saved-model outputs at the recorded historical cutoff. They are not current-business predictions, live forecasts, or recommendations.</span></div>;
}
function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{action}</div>;
}
function Panel({ title, note, children, extra }: { title: string; note?: string; children: ReactNode; extra?: ReactNode }) {
  return <section className="panel"><div className="panel-head"><div><div className="panel-title">{title}</div>{note && <div className="panel-note">{note}</div>}</div>{extra}</div>{children}</section>;
}
function Loading({ rows = 2 }: { rows?: number }) {
  return <div className="grid" aria-label="Loading data">{Array.from({ length: rows }, (_, i) => <div key={i} className="skeleton" />)}</div>;
}
function QueryState({ loading, error, empty, retry, children }: { loading: boolean; error: boolean; empty?: boolean; retry: () => void; children: ReactNode }) {
  if (loading) return <Loading />;
  if (error) return <div className="error-box"><AlertCircle size={17} style={{ verticalAlign: 'middle', marginRight: 7 }} />Data could not be loaded. <button className="button secondary" onClick={retry} style={{ marginLeft: 9 }}>Try again</button></div>;
  if (empty) return <div className="empty-box">No saved historical data is available for this view.</div>;
  return <>{children}</>;
}
function Metric({ label, value, foot, icon: Icon }: { label: string; value: string; foot: string; icon: ElementType }) {
  return <div className="panel"><div className="metric-label"><span>{label}</span><Icon size={16} color="#83978b" /></div><div className="metric-value number">{value}</div><div className="metric-accent" /><div className="metric-foot">{foot}</div></div>;
}
function AppShell() {
  const location = useLocation();
  const health = useHealthCheck({ query: { queryKey: getHealthCheckQueryKey(), refetchInterval: 60_000 } });
  const previewHealth = useGetApiHealth({ query: { queryKey: getGetApiHealthQueryKey(), refetchInterval: 60_000 } });
  const title = useMemo(() => {
    const titles: Record<string, string> = { '/': 'Business overview', '/segments': 'Customer segments', '/intelligence': 'Customer intelligence', '/behavior': 'Behavior indicators', '/forecasting': 'Forecast workspace', '/upload': 'Upload analysis', '/model-performance': 'Model performance' };
    return titles[location.pathname] ?? 'Workspace';
  }, [location.pathname]);
  const links = [
    { to: '/', label: 'Business overview', icon: LayoutDashboard },
    { to: '/segments', label: 'Segments', icon: Users },
    { to: '/intelligence', label: 'Customer intelligence', icon: UserRoundSearch },
    { to: '/behavior', label: 'Behavior indicators', icon: History },
    { to: '/forecasting', label: 'Forecasting', icon: Activity },
    { to: '/upload', label: 'Upload analysis', icon: UploadCloud },
    { to: '/model-performance', label: 'Model performance', icon: BarChart3 },
  ];
  const connected = health.isSuccess || previewHealth.isSuccess;
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">O</div><div><div className="brand-name">OELP Intelligence</div><div className="brand-sub">Customer retention</div></div></div>
      <nav aria-label="Primary navigation"><div className="nav-label">Workspace</div><div className="nav-list">{links.map(({ to, label, icon: Icon }) => <NavLink to={to} end={to === '/'} key={to} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`} data-testid={`link-${to === '/' ? 'overview' : to.slice(1)}`}><Icon /><span>{label}</span></NavLink>)}</div></nav>
      <div className="side-foot"><strong>HISTORICAL DATASET</strong><br />Saved notebook evaluations<br />No live business connection</div>
    </aside>
    <main className="main-area">
      <header className="topbar"><div className="crumb">OELP / {title}</div><div className="top-right"><div className="status-pill"><span className="status-dot" style={{ background: connected ? '#4b9c79' : '#c7a15e' }} />{connected ? 'API connected' : health.isLoading || previewHealth.isLoading ? 'Checking API' : 'API unavailable'}</div><div className="top-date">SAVED MODEL WORKSPACE</div></div></header>
      <Routes>
        <Route path="/" element={<Overview />} />
        <Route path="/segments" element={<Segments />} />
        <Route path="/intelligence" element={<Intelligence />} />
        <Route path="/behavior" element={<BehaviorPage />} />
        <Route path="/forecasting" element={<Forecasting />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/model-performance" element={<Performance />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </main>
  </div>;
}

function Overview() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const params = useMemo(() => ({ start_date: startDate || undefined, end_date: endDate || undefined }), [startDate, endDate]);
  const q = useGetOverview(params, { query: { queryKey: getGetOverviewQueryKey(params) } });
  const data = q.data;
  const segmentData = data?.descriptive_segments ?? [];
  return <div className="content">
    <PageHeading eyebrow="Historical trading record" title="Business overview" description="A descriptive view of the saved customer-retention dataset and its historical model outputs." />
    <HistoricalNotice />
    <Panel title="Historical period" note="Adjust the saved-data window for descriptive totals and monthly trends">
      <div className="filter-row" style={{ marginBottom: 0 }}>
        <div className="field" style={{ maxWidth: 220 }}><label className="field-label" htmlFor="overview-start">Start date</label><input id="overview-start" className="input" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} data-testid="input-overview-start-date" /></div>
        <div className="field" style={{ maxWidth: 220 }}><label className="field-label" htmlFor="overview-end">End date</label><input id="overview-end" className="input" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} data-testid="input-overview-end-date" /></div>
        {(startDate || endDate) && <button className="button secondary" onClick={() => { setStartDate(''); setEndDate(''); }} data-testid="button-reset-overview-dates">Reset dates</button>}
      </div>
    </Panel>
    <QueryState loading={q.isLoading} error={q.isError} empty={!data} retry={() => void q.refetch()}>
      {data && <>
        <div className="grid kpis">
          <Metric label="Customers in history" value={number(data.historical.customers)} foot={`${dateShort(data.period.start_date)} — ${dateShort(data.period.end_date)}`} icon={Users} />
          <Metric label="Historical orders" value={number(data.historical.orders)} foot="Observed transaction history" icon={ShoppingBag} />
          <Metric label="Historical revenue" value={money(data.historical.revenue)} foot={`Average order ${money(data.historical.average_order_value)}`} icon={Wallet} />
          <Metric label="Forecast-eligible cohort" value={number(data.forecast.eligible_customers)} foot={`Cutoff ${dateShort(data.forecast.cutoff_date)}`} icon={Sparkles} />
        </div>
        <div className="grid two">
          <Panel title="Revenue over time" note="Observed monthly revenue and order counts in the source period">
            {data.monthly_trend.length ? <div className="chart-wrap"><ResponsiveContainer><ComposedChart data={data.monthly_trend} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="month" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis yAxisId="left" tickFormatter={(v) => money(v)} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} width={58} /><YAxis yAxisId="right" orientation="right" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} width={38} /><Tooltip formatter={(v, name) => [name === 'Revenue' ? money(Number(v)) : number(Number(v)), name]} /><Bar yAxisId="left" dataKey="revenue" name="Revenue" fill="#315a4c" radius={[3, 3, 0, 0]} maxBarSize={23} /><Line yAxisId="right" dataKey="orders" name="Orders" stroke="#d49a65" strokeWidth={2} dot={false} /></ComposedChart></ResponsiveContainer></div> : <div className="empty-box">No monthly trend rows in the saved response.</div>}
          </Panel>
          <Panel title="Descriptive RFM mix" note="Customer share by segment; descriptive classification, not a forecast cohort">
            {segmentData.length ? <div className="chart-wrap short"><ResponsiveContainer><BarChart data={segmentData} layout="vertical" margin={{ left: 8, right: 12 }}><CartesianGrid stroke="#ebe8de" horizontal={false} /><XAxis type="number" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="segment" width={122} tick={{ fontSize: 9, fill: '#53685d' }} axisLine={false} tickLine={false} /><Tooltip formatter={(v) => number(Number(v))} /><Bar dataKey="customers" name="Customers" radius={[0, 4, 4, 0]} maxBarSize={22}>{segmentData.map((s, i) => <Cell key={s.segment} fill={COLORS[i % COLORS.length]} />)}</Bar></BarChart></ResponsiveContainer></div> : <div className="empty-box">No descriptive segments in this response.</div>}
          </Panel>
        </div>
        <div className="grid two" style={{ marginTop: 16 }}>
          <Panel title="Saved-model cohort totals" note={`Historical segment · cutoff ${dateShort(data.forecast.cutoff_date)}`}><div className="table-scroll"><table><thead><tr><th>Horizon</th><th>Expected returners</th><th>Expected revenue</th></tr></thead><tbody>{[30, 60, 90].map((d) => <tr key={d}><td>{d} days</td><td className="number">{number(data.forecast[`expected_returners_${d}d` as 'expected_returners_30d' | 'expected_returners_60d' | 'expected_returners_90d'])}</td><td className="number">{money(data.forecast[`expected_revenue_${d}d` as 'expected_revenue_30d' | 'expected_revenue_60d' | 'expected_revenue_90d'])}</td></tr>)}</tbody></table></div></Panel>
          <Panel title="Segment summary" note="Observed RFM characteristics"><div className="table-scroll"><table><thead><tr><th>Segment</th><th>Customers</th><th>Median recency</th><th>Revenue share</th></tr></thead><tbody>{segmentData.slice(0, 5).map((s) => <tr key={s.segment}><td><strong>{s.segment}</strong></td><td className="number">{number(s.customers)}</td><td className="number">{number(s.median_recency)} days</td><td className="number">{percent(s.revenue_share)}</td></tr>)}</tbody></table></div></Panel>
        </div>
      </>}
    </QueryState>
  </div>;
}

function Segments() {
  const q = useGetSegments({ query: { queryKey: getGetSegmentsQueryKey() } });
  const data = q.data;
  const [tab, setTab] = useState<'descriptive' | 'historical'>('descriptive');
  const [customerSearch, setCustomerSearch] = useState('');
  const [customerPage, setCustomerPage] = useState(1);
  const [histSegment, setHistSegment] = useState('');
  const [historyGroup, setHistoryGroup] = useState<GetCustomersHistoryGroup | ''>('');
  const customerParams = useMemo(() => ({
    page: customerPage,
    page_size: 10,
    search: customerSearch.trim() || undefined,
    hist_segment: histSegment || undefined,
    history_group: historyGroup || undefined,
  }), [customerPage, customerSearch, histSegment, historyGroup]);
  const customers = useGetCustomers(customerParams, { query: { queryKey: getGetCustomersQueryKey(customerParams) } });
  const descriptions = data?.descriptive_segments ?? [];
  const hist = data?.historical_segments ?? [];
  const exportCustomers = () => {
    const items = customers.data?.items ?? [];
    if (!items.length) return;
    const escape = (value: unknown) => `"${String(value ?? '').replaceAll('"', '""')}"`;
    const columns = [
      'customer_id',
      'retrospective_segment',
      'hist_segment',
      'history_group',
      'cutoff_recency_days',
      'cutoff_frequency',
      'cutoff_gross_spend',
      'retrospective_net_spend',
      'retrospective_average_order_value',
      'retrospective_at_risk_flag',
      'retrospective_source_start',
      'retrospective_source_end',
    ];
    const csv = [
      columns.join(','),
      ...items.map((item) => [
        item.customer_id,
        item.retrospective_description.descriptive_segment,
        item.hist_segment,
        item.history_group,
        item.recency,
        item.frequency,
        item.monetary_gross,
        item.retrospective_description.monetary_net,
        item.retrospective_description.average_order_value,
        item.retrospective_description.at_risk_flag,
        item.retrospective_description.source_period.start_date,
        item.retrospective_description.source_period.end_date,
      ].map(escape).join(',')),
    ].join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `oelp-customers-page-${customerPage}.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  };
  return <div className="content">
    <PageHeading eyebrow="Customer composition" title="Segments" description="Explore full-period retrospective RFM descriptions separately from the forecast-time cohorts and customer features." />
    <HistoricalNotice />
    <QueryState loading={q.isLoading} error={q.isError} empty={!data} retry={() => void q.refetch()}>
      {data && <>
        <div className="filter-row"><button className={`button ${tab === 'descriptive' ? '' : 'secondary'}`} onClick={() => setTab('descriptive')} data-testid="button-descriptive-segments">Full-period descriptive RFM</button><button className={`button ${tab === 'historical' ? '' : 'secondary'}`} onClick={() => setTab('historical')} data-testid="button-historical-cohorts">Historical forecast cohorts</button><span className="tiny" style={{ marginLeft: 5 }}>{tab === 'descriptive' ? 'Full-period RFM labels are retrospective and are not forecast-time inputs.' : 'These cohorts are model evaluation groupings at the historical cutoff.'}</span></div>
        {tab === 'descriptive' ? <div className="grid two">
          <Panel title="Descriptive segment distribution" note="Customer count and share from saved RFM analysis">
            {descriptions.length ? <div className="chart-wrap tall"><ResponsiveContainer><BarChart data={descriptions} layout="vertical" margin={{ left: 10, right: 20 }}><CartesianGrid stroke="#ebe8de" horizontal={false} /><XAxis type="number" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="segment" width={100} tick={{ fontSize: 10, fill: '#53685d' }} axisLine={false} tickLine={false} /><Tooltip formatter={(v, n) => [number(Number(v)), n === 'customers' ? 'Customers' : 'Gross spend']} /><Bar dataKey="customers" fill="#315a4c" radius={[0, 4, 4, 0]} maxBarSize={19} /></BarChart></ResponsiveContainer></div> : <div className="empty-box">No descriptive RFM data.</div>}
          </Panel>
          <Panel title="RFM profile" note="Median behavior by descriptive segment"><div className="table-scroll"><table><thead><tr><th>Segment</th><th>Customers</th><th>Share</th><th>Median recency</th><th>Median frequency</th><th>Median gross spend</th></tr></thead><tbody>{descriptions.map((s) => <tr key={s.segment}><td><span className="badge">{s.segment}</span></td><td className="number">{number(s.customers)}</td><td className="number">{percent(s.customer_share)}</td><td className="number">{number(s.median_recency)}d</td><td className="number">{number(s.median_frequency)}</td><td className="number">{money(s.median_gross_spend)}</td></tr>)}</tbody></table></div></Panel>
        </div> : <Panel title="Historical forecast cohorts" note="Saved cohort labels and eligible customer counts at the forecast cutoff">
          {hist.length ? <div className="table-scroll"><table><thead><tr><th>Historical cohort</th><th>Customers</th><th>Use</th></tr></thead><tbody>{hist.map((s) => <tr key={s.segment}><td><strong>{s.segment}</strong></td><td className="number">{number(s.customers)}</td><td><span className="badge neutral">Forecast evaluation group</span></td></tr>)}</tbody></table></div> : <div className="empty-box">No historical forecast cohorts are saved.</div>}
        </Panel>}
      </>}
    </QueryState>
    <div style={{ marginTop: 16 }}>
      <Panel title="Customer records" note="Recency, frequency, and gross spend use the forecast cutoff. The nested retrospective description uses the complete observed period." extra={<button className="button secondary" disabled={!customers.data?.items.length} onClick={exportCustomers} data-testid="button-export-segment-customers"><ArrowDownToLine />Export current page</button>}>
        <div className="filter-row">
          <div className="field" style={{ maxWidth: 260 }}><label className="field-label" htmlFor="segment-customer-search">Search by customer ID</label><input id="segment-customer-search" className="input" value={customerSearch} placeholder="Customer ID" onChange={(e) => { setCustomerSearch(e.target.value); setCustomerPage(1); }} data-testid="input-segment-customer-search" /></div>
          <div className="field" style={{ maxWidth: 260 }}><label className="field-label" htmlFor="segment-historical-cohort">Historical forecast cohort</label><select id="segment-historical-cohort" className="input" value={histSegment} onChange={(e) => { setHistSegment(e.target.value); setCustomerPage(1); }} data-testid="select-historical-cohort"><option value="">All cohorts</option>{hist.map((item) => <option key={item.segment} value={item.segment}>{item.segment}</option>)}</select></div>
          <div className="field" style={{ maxWidth: 260 }}><label className="field-label" htmlFor="segment-history-group">Purchase-history group</label><select id="segment-history-group" className="input" value={historyGroup} onChange={(e) => { setHistoryGroup(e.target.value as GetCustomersHistoryGroup | ''); setCustomerPage(1); }} data-testid="select-history-group"><option value="">All groups</option><option value="Exactly one purchase">Exactly one purchase</option><option value="Two to four purchases">Two to four purchases</option><option value="Five or more purchases">Five or more purchases</option></select></div>
          <span className="tiny">{customers.data ? `${number(customers.data.total)} matching records` : 'Search or filter the saved customer records'}</span>
        </div>
        <QueryState loading={customers.isLoading} error={customers.isError} empty={!customers.data?.items.length} retry={() => void customers.refetch()}>
          {customers.data && <><div className="table-scroll"><table><thead><tr><th>Customer ID</th><th>Full-period retrospective RFM</th><th>Historical cutoff cohort</th><th>Purchase-history group</th><th>Cutoff recency</th><th>Cutoff frequency</th><th>Cutoff gross spend</th><th>Retrospective net spend</th><th>Retrospective average order</th><th>Retrospective risk flag</th></tr></thead><tbody>{customers.data.items.map((customer) => <tr key={customer.customer_id}><td className="number">{customer.customer_id}</td><td>{customer.retrospective_description.descriptive_segment}</td><td>{customer.hist_segment ?? '—'}</td><td>{customer.history_group ?? '—'}</td><td className="number">{number(customer.recency)}d</td><td className="number">{number(customer.frequency)}</td><td className="number">{money(customer.monetary_gross)}</td><td className="number">{money(customer.retrospective_description.monetary_net)}</td><td className="number">{money(customer.retrospective_description.average_order_value)}</td><td><span className={`badge${customer.retrospective_description.at_risk_flag ? ' warn' : ' neutral'}`}>{customer.retrospective_description.at_risk_flag ? 'Flagged' : 'No'}</span></td></tr>)}</tbody></table></div><div className="filter-row" style={{ justifyContent: 'space-between', margin: '12px 0 0' }}><span className="tiny">Page {customers.data.page} of {Math.max(1, Math.ceil(customers.data.total / customers.data.page_size))}</span><div style={{ display: 'flex', gap: 7 }}><button className="button secondary" disabled={customerPage <= 1 || customers.isFetching} onClick={() => setCustomerPage((page) => Math.max(1, page - 1))} data-testid="button-segment-customers-previous">Previous</button><button className="button secondary" disabled={customerPage >= Math.ceil(customers.data.total / customers.data.page_size) || customers.isFetching} onClick={() => setCustomerPage((page) => page + 1)} data-testid="button-segment-customers-next">Next</button></div></div></>}
        </QueryState>
      </Panel>
    </div>
  </div>;
}

function Intelligence() {
  const [search, setSearch] = useState('');
  const [submitted, setSubmitted] = useState('');
  const [customerId, setCustomerId] = useState<number | null>(null);
  const params = useMemo(() => ({ page: 1, page_size: 8, search: submitted || undefined }), [submitted]);
  const list = useGetCustomers(params, { query: { queryKey: getGetCustomersQueryKey(params), enabled: submitted.length > 0 } });
  const profile = useGetCustomer(customerId ?? 0, { query: { queryKey: getGetCustomerQueryKey(customerId ?? 0), enabled: customerId !== null } });
  const history = useGetCustomerHistory(customerId ?? 0, { query: { queryKey: getGetCustomerHistoryQueryKey(customerId ?? 0), enabled: customerId !== null } });
  const forecast = useGetCustomerForecast(customerId ?? 0, { query: { queryKey: getGetCustomerForecastQueryKey(customerId ?? 0), enabled: customerId !== null } });
  const onSearch = (e: FormEvent) => { e.preventDefault(); setSubmitted(search.trim()); setCustomerId(null); };
  const p = profile.data;
  const exportCustomerForecast = () => {
    if (!p) return;
    const rows: [string, string | number][] = [
      ['customer_id', p.customer_id],
      ['cutoff_date', p.cutoff_date],
      ['hist_segment', p.hist_segment],
      ['history_group', p.history_group],
      ['global_purchase_probability_30d', p.global_purchase_probability_30d],
      ['segment_purchase_probability_30d', p.segment_purchase_probability_30d],
      ['personalized_purchase_probability_30d', p.purchase_probability_30d],
      ['personalized_expected_spend_30d', p.personalized_expected_revenue_30d],
      ['global_purchase_probability_60d', p.global_purchase_probability_60d],
      ['segment_purchase_probability_60d', p.segment_purchase_probability_60d],
      ['personalized_purchase_probability_60d', p.purchase_probability_60d],
      ['personalized_expected_spend_60d', p.personalized_expected_revenue_60d],
      ['global_purchase_probability_90d', p.global_purchase_probability_90d],
      ['segment_purchase_probability_90d', p.segment_purchase_probability_90d],
      ['personalized_purchase_probability_90d', p.purchase_probability_90d],
      ['personalized_expected_spend_90d', p.personalized_expected_revenue_90d],
    ];
    const escape = (value: string | number) => `"${String(value).replace(/"/g, '""')}"`;
    const csv = `${rows.map(([key]) => escape(key)).join(',')}\n${rows.map(([, value]) => escape(value)).join(',')}\n`;
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `customer-${p.customer_id}-saved-forecast.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  };
  return <div className="content">
    <PageHeading eyebrow="Individual customer history" title="Customer intelligence" description="Search eligible IDs and inspect the cutoff-time forecast separately from full-period retrospective descriptions." />
    <HistoricalNotice />
    <Panel title="Find an eligible customer" note="Search by Customer ID. Results and profiles come from the saved historical dataset.">
      <form className="filter-row" onSubmit={onSearch}><div className="field" style={{ maxWidth: 410 }}><label className="field-label" htmlFor="customer-search">Customer ID</label><div style={{ position: 'relative' }}><Search size={15} style={{ position: 'absolute', top: 11, left: 11, color: '#85938b' }} /><input className="input" id="customer-search" style={{ paddingLeft: 34 }} value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Enter a saved Customer ID" data-testid="input-customer-id" /></div></div><button className="button" type="submit" data-testid="button-search-customer"><Search />Search records</button></form>
      {submitted && !customerId && <QueryState loading={list.isLoading} error={list.isError} empty={list.data?.items.length === 0} retry={() => void list.refetch()}>{list.data && <div className="table-scroll"><table><thead><tr><th>Customer ID</th><th>Full-period retrospective RFM</th><th>Historical cutoff cohort</th><th>Cutoff frequency</th><th>Cutoff gross spend</th><th></th></tr></thead><tbody>{list.data.items.map((c: CustomerListItem) => <tr key={c.customer_id}><td className="number">{c.customer_id}</td><td><span className="badge">{c.retrospective_description.descriptive_segment}</span></td><td>{c.hist_segment ?? '—'}</td><td className="number">{number(c.frequency)}</td><td className="number">{money(c.monetary_gross)}</td><td><button className="button secondary" onClick={() => setCustomerId(c.customer_id)} data-testid={`button-open-customer-${c.customer_id}`}>Open profile</button></td></tr>)}</tbody></table></div>}</QueryState>}
    </Panel>
    {customerId !== null && <div style={{ marginTop: 16 }}>
      <QueryState loading={profile.isLoading} error={profile.isError} empty={!p} retry={() => void profile.refetch()}>
        {p && <>
          <div className="profile-hero"><div><div className="eyebrow" style={{ color: '#e8c575' }}>Saved forecast · historical demonstration</div><div className="profile-id">Customer {p.customer_id}</div><div className="profile-sub">{p.hist_segment} · cutoff {dateShort(p.cutoff_date)}</div></div><button className="button secondary" onClick={exportCustomerForecast} data-testid="button-export-customer-forecast"><ArrowDownToLine />Download saved forecast CSV</button><div className="profile-stats"><div className="profile-stat"><span>Last purchase before cutoff</span><strong>{dateShort(p.last_purchase_date)}</strong></div><div className="profile-stat"><span>Forecast history group</span><strong>{p.history_group || '—'}</strong></div></div></div>
          <div className="grid kpis">
            <Metric label="Days since purchase" value={`${number(p.recency)}d`} foot={`First purchase ${dateShort(p.first_purchase_date)}`} icon={Clock3} />
            <Metric label="Historical orders" value={number(p.frequency)} foot={`${number(p.n_historical_gaps)} observed purchase gaps`} icon={ShoppingBag} />
            <Metric label="Cutoff gross spend" value={money(p.monetary_gross)} foot={`Observed before ${dateShort(p.cutoff_date)}`} icon={Wallet} />
            <Metric label="Personalized expected gap" value={`${number(p.regularized_expected_gap_days)}d`} foot={`Delay ratio ${Number.isFinite(p.delay_ratio) ? p.delay_ratio.toFixed(2) : '—'}`} icon={ArrowLeftRight} />
          </div>
        </>}
      </QueryState>
      {p && <div className="grid equal" style={{ marginTop: 16 }}>
        <Panel title="Purchase probability" note="Personalized saved-model probabilities; historical demonstration">
          {[['30 days', p.purchase_probability_30d], ['60 days', p.purchase_probability_60d], ['90 days', p.purchase_probability_90d]].map(([label, val]) => <div className="prob-row" key={label as string}><span>{label}</span><div className="track"><div className="fill" style={{ width: `${Math.max(0, Math.min(100, Number(val) * 100))}%` }} /></div><strong className="number">{percent(Number(val))}</strong></div>)}
          <div className="tiny" style={{ marginTop: 15 }}>Global / segment / personalized are retained separately in the saved forecast record.</div>
          <div className="table-scroll" style={{ marginTop: 10 }}><table><thead><tr><th>Horizon</th><th>Global</th><th>Segment</th><th>Personalized</th><th>Expected spend</th></tr></thead><tbody>{[30, 60, 90].map((d) => <tr key={d}><td>{d}d</td><td className="number">{percent(p[`global_purchase_probability_${d}d` as 'global_purchase_probability_30d' | 'global_purchase_probability_60d' | 'global_purchase_probability_90d'])}</td><td className="number">{percent(p[`segment_purchase_probability_${d}d` as 'segment_purchase_probability_30d' | 'segment_purchase_probability_60d' | 'segment_purchase_probability_90d'])}</td><td className="number">{percent(p[`purchase_probability_${d}d` as 'purchase_probability_30d' | 'purchase_probability_60d' | 'purchase_probability_90d'])}</td><td className="number">{money(p[`personalized_expected_revenue_${d}d` as 'personalized_expected_revenue_30d' | 'personalized_expected_revenue_60d' | 'personalized_expected_revenue_90d'])}</td></tr>)}</tbody></table></div>
        </Panel>
        <Panel title="Cumulative probability curve" note="Saved customer-level curve"><QueryState loading={forecast.isLoading} error={forecast.isError} empty={!forecast.data?.cumulative_curve.length} retry={() => void forecast.refetch()}>{forecast.data && <div className="chart-wrap"><ResponsiveContainer><AreaChart data={forecast.data.cumulative_curve}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="day" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis domain={[0, 1]} tickFormatter={(v) => percent(Number(v))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(v) => percent(Number(v))} labelFormatter={(v) => `Day ${v}`} /><Area type="monotone" dataKey="probability" stroke="#315a4c" fill="#d8e2d8" strokeWidth={2} /></AreaChart></ResponsiveContainer></div>}</QueryState></Panel>
        <Panel title="Purchase history" note="Orders before the historical cutoff"><QueryState loading={history.isLoading} error={history.isError} empty={!history.data?.length} retry={() => void history.refetch()}>{history.data && <div className="table-scroll"><table><thead><tr><th>Purchase date</th><th>Invoice</th><th>Gross revenue</th></tr></thead><tbody>{history.data.map((order, i) => <tr key={`${order.invoice}-${i}`}><td>{dateShort(order.purchase_date)}</td><td className="number">{order.invoice}</td><td className="number">{money(order.gross_revenue)}</td></tr>)}</tbody></table></div>}</QueryState></Panel>
      </div>}
      {p && <div style={{ marginTop: 16 }}>
        <Panel title="Retrospective full-period description" note={`These RFM and net-spend values use all observed transactions from ${dateShort(p.retrospective_description.source_period.start_date)} through ${dateShort(p.retrospective_description.source_period.end_date)}. They may include data after the forecast cutoff and are not model inputs.`}>
          <div className="grid kpis">
            <Metric label="Retrospective RFM segment" value={p.retrospective_description.descriptive_segment} foot="Full observed transaction period" icon={Users} />
            <Metric label="Retrospective net spend" value={money(p.retrospective_description.monetary_net)} foot="Full observed transaction period" icon={Wallet} />
            <Metric label="Retrospective average order" value={money(p.retrospective_description.average_order_value)} foot="Full observed transaction period" icon={ArrowLeftRight} />
            <Metric label="Retrospective risk flag" value={p.retrospective_description.at_risk_flag ? 'Flagged' : 'Not flagged'} foot="Descriptive status, not a predicted outcome" icon={ShieldCheck} />
          </div>
        </Panel>
      </div>}
      {p && <div style={{ marginTop: 16 }}><BehaviorHistory customerId={p.customer_id} /></div>}
    </div>}
  </div>;
}

function Forecasting() {
  const [segment, setSegment] = useState('');
  const [historyGroup, setHistoryGroup] = useState('');
  const [visibleModels, setVisibleModels] = useState({ global: true, segment: true, personalized: true });
  const params = useMemo(() => ({ hist_segment: segment || undefined, history_group: historyGroup.trim() || undefined }), [segment, historyGroup]);
  const q = useGetForecastSummary(params, { query: { queryKey: getGetForecastSummaryQueryKey(params) } });
  const segments = useGetSegments({ query: { queryKey: getGetSegmentsQueryKey() } });
  const d = q.data;
  const anyModelVisible = Object.values(visibleModels).some(Boolean);
  return <div className="content">
    <PageHeading eyebrow="Saved model outputs" title="Forecast workspace" description="Compare model outputs for historical customer cohorts and validated horizons." />
    <HistoricalNotice />
    <Panel title="Cohort filters" note="Filtering applies to saved historical cohort labels; it does not change or retrain a model">
      <div className="filter-row"><div className="field" style={{ maxWidth: 300 }}><label className="field-label" htmlFor="forecast-segment">Historical cohort</label><select id="forecast-segment" className="select" value={segment} onChange={(e) => setSegment(e.target.value)} data-testid="select-historical-cohort"><option value="">All historical cohorts</option>{(segments.data?.historical_segments ?? []).map((s) => <option value={s.segment} key={s.segment}>{s.segment}</option>)}</select></div><div className="field" style={{ maxWidth: 260 }}><label className="field-label" htmlFor="forecast-history-group">History group</label><input id="forecast-history-group" className="input" value={historyGroup} onChange={(e) => setHistoryGroup(e.target.value)} placeholder="Filter by history group" data-testid="input-history-group" /></div><div className="tiny">Data cutoff: {dateShort(d?.cutoff_date)}</div></div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', borderTop: '1px solid #e5e1d6', paddingTop: 12 }}>
        <span className="field-label" style={{ margin: 0 }}>Compare models</span>
        {([
          ['global', 'Global'],
          ['segment', 'Segment'],
          ['personalized', 'Personalized'],
        ] as const).map(([key, label]) => <label key={key} className="badge" style={{ cursor: 'pointer', gap: 7 }}>
          <input type="checkbox" checked={visibleModels[key]} onChange={() => setVisibleModels((current) => ({ ...current, [key]: !current[key] }))} data-testid={`input-model-${key}`} />
          {label}
        </label>)}
      </div>
    </Panel>
    <div style={{ marginTop: 16 }}><QueryState loading={q.isLoading} error={q.isError} empty={!d} retry={() => void q.refetch()}>{d && <>
      <div className="grid kpis">
        <Metric label="Eligible customers" value={number(d.eligible_customers)} foot={`Cutoff ${dateShort(d.cutoff_date)}`} icon={Users} />
        <Metric label="Expected returners · 30d" value={number(d.expected_returners_30d)} foot="Saved-model cohort total" icon={Activity} />
        <Metric label="Expected returners · 60d" value={number(d.expected_returners_60d)} foot="Saved-model cohort total" icon={Activity} />
        <Metric label="Expected returners · 90d" value={number(d.expected_returners_90d)} foot="Saved-model cohort total" icon={Activity} />
      </div>
      <div className="grid two">
        <Panel title="Purchase probability by horizon" note={`Historical segment: ${d.hist_segment || 'All cohorts'} · cutoff ${dateShort(d.cutoff_date)}`}>
          {d.horizons.length && anyModelVisible ? <div className="chart-wrap"><ResponsiveContainer><LineChart data={d.horizons}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="days" tickFormatter={(v) => `${v}d`} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis domain={[0, 1]} tickFormatter={(v) => percent(Number(v))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(v) => percent(Number(v))} labelFormatter={(v) => `${v} day horizon`} />{visibleModels.global && <Line type="monotone" dataKey="global_probability" name="Global" stroke="#78918a" strokeWidth={2} />}{visibleModels.segment && <Line type="monotone" dataKey="segment_probability" name="Segment" stroke="#c57d5c" strokeWidth={2} />}{visibleModels.personalized && <Line type="monotone" dataKey="personalized_probability" name="Personalized" stroke="#315a4c" strokeWidth={2.5} />}<Legend /></LineChart></ResponsiveContainer></div> : <div className="empty-box">{d.horizons.length ? 'Select at least one model to display the comparison.' : 'No saved horizon comparisons.'}</div>}
        </Panel>
        <Panel title="Expected revenue comparison" note="Expected revenue across saved comparison models">
          {d.horizons.length && anyModelVisible ? <div className="chart-wrap"><ResponsiveContainer><BarChart data={d.horizons}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="days" tickFormatter={(v) => `${v}d`} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(v) => money(Number(v))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} width={58} /><Tooltip formatter={(v) => money(Number(v))} labelFormatter={(v) => `${v} day horizon`} />{visibleModels.global && <Bar dataKey="historical_rate_expected_revenue" name="Global" fill="#78918a" radius={[3, 3, 0, 0]} />}{visibleModels.segment && <Bar dataKey="segment_expected_revenue" name="Segment" fill="#d8ad5e" radius={[3, 3, 0, 0]} />}{visibleModels.personalized && <Bar dataKey="personalized_expected_revenue" name="Personalized" fill="#315a4c" radius={[3, 3, 0, 0]} />}<Legend /></BarChart></ResponsiveContainer></div> : <div className="empty-box">{d.horizons.length ? 'Select at least one model to display the comparison.' : 'No revenue comparisons saved.'}</div>}
        </Panel>
      </div>
      <div className="grid equal" style={{ marginTop: 16 }}>
        <Panel title="Cumulative returner curve" note="Saved cohort probability curve">{d.cumulative_curve.length ? <div className="chart-wrap"><ResponsiveContainer><AreaChart data={d.cumulative_curve}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="day" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis domain={[0, 1]} tickFormatter={(v) => percent(Number(v))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(v) => percent(Number(v))} /><Area type="monotone" dataKey="probability" stroke="#315a4c" fill="#d8e2d8" strokeWidth={2} /></AreaChart></ResponsiveContainer></div> : <div className="empty-box">No cumulative curve available.</div>}</Panel>
        <Panel title="Saved comparison values" note="The forecast is historical, and cohort totals are not realized outcomes"><div className="table-scroll"><table><thead><tr><th>Horizon</th>{visibleModels.global && <th>Global probability</th>}{visibleModels.segment && <th>Segment probability</th>}{visibleModels.personalized && <th>Personalized probability</th>}</tr></thead><tbody>{d.horizons.map((h) => <tr key={h.days}><td>{h.days} days</td>{visibleModels.global && <td className="number">{percent(h.global_probability)}</td>}{visibleModels.segment && <td className="number">{percent(h.segment_probability)}</td>}{visibleModels.personalized && <td className="number">{percent(h.personalized_probability)}</td>}</tr>)}</tbody></table></div></Panel>
      </div>
    </>}</QueryState></div>
  </div>;
}

const mappingFields = [
  { key: 'Invoice', label: 'Invoice', required: true, candidates: ['invoice', 'invoiceno', 'invoice_no', 'order_id'] },
  { key: 'StockCode', label: 'StockCode', required: true, candidates: ['stockcode', 'stock_code', 'sku'] },
  { key: 'Description', label: 'Description', required: true, candidates: ['description', 'product'] },
  { key: 'Quantity', label: 'Quantity', required: true, candidates: ['quantity', 'qty'] },
  { key: 'InvoiceDate', label: 'InvoiceDate', required: true, candidates: ['invoicedate', 'invoice_date', 'date', 'purchase_date'] },
  { key: 'Price', label: 'Price', required: true, candidates: ['price', 'unit_price', 'unitprice'] },
  { key: 'Customer ID', label: 'Customer ID', required: true, candidates: ['customerid', 'customer_id', 'customer'] },
  { key: 'Country', label: 'Country', required: true, candidates: ['country'] },
];
function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<UploadPreview | null>(null);
  const [analysis, setAnalysis] = useState<UploadAnalysis | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const previewMutation = usePreviewUpload({ mutation: { onSuccess: (data) => { setPreview(data); setAnalysis(null); const normalized: Record<string, string> = {}; mappingFields.forEach((field) => { const match = data.columns.find((column) => field.candidates.includes(column.toLowerCase().replace(/[^a-z0-9]/g, ''))); if (match) normalized[field.key] = match; }); setMapping(normalized); } } });
  const analyzeMutation = useAnalyzeUpload({ mutation: { onSuccess: setAnalysis } });
  const exportMutation = useExportUpload();
  const [exportError, setExportError] = useState('');
  const uploadFile = (selected: File | null) => { if (!selected) return; setFile(selected); setPreview(null); setAnalysis(null); setMapping({}); previewMutation.mutate({ data: { file: selected } }); };
  const runAnalysis = () => { if (!file) return; analyzeMutation.mutate({ data: { file, mapping: JSON.stringify(mapping) } }); };
  const download = (kind: 'cleaned_transactions' | 'customer_features') => {
    if (!file) return;
    setExportError('');
    exportMutation.mutate({ data: { file, mapping: JSON.stringify(mapping), kind } }, { onSuccess: (csv) => { const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `${kind}.csv`; a.click(); URL.revokeObjectURL(url); }, onError: () => setExportError('The export could not be prepared. Try again.') });
  };
  const requiredMapped = mappingFields.filter((f) => f.required).every((f) => mapping[f.key]);
  const a = analysis;
  return <div className="content">
    <PageHeading eyebrow="Descriptive only · nothing saved" title="Upload analysis" description="Preview a CSV or XLSX, map transaction columns, inspect descriptive validation and download reprocessed CSVs. Uploads are not persisted." />
    <div className="historical-banner"><ShieldCheck size={15} /><span><strong>Private, in-memory workflow.</strong> This tool does not create forecasts or save uploaded records. The analysis is descriptive validation only.</span></div>
    <div className="grid two">
      <Panel title="Choose a transaction file" note="Supported formats are CSV and XLSX">
        <label className="upload-drop" htmlFor="upload-file" style={{ display: 'block', cursor: 'pointer' }}><UploadCloud size={25} /><div style={{ fontWeight: 700, color: '#38574b', fontSize: 12 }}>{file ? file.name : 'Select a CSV or XLSX file'}</div><div className="tiny" style={{ marginTop: 5 }}>{file ? 'Choose another file to replace this preview' : 'Your data stays in the current analysis session'}</div><input id="upload-file" type="file" accept=".csv,.xlsx" style={{ display: 'none' }} onChange={(e) => uploadFile(e.target.files?.[0] ?? null)} data-testid="input-upload-file" /></label>
        {previewMutation.isPending && <div style={{ marginTop: 14 }}><Loading rows={1} /></div>}
        {previewMutation.isError && <div className="error-box" style={{ marginTop: 12 }}>Preview failed. Check that the file is CSV or XLSX, then select it again.</div>}
        {preview && <div style={{ marginTop: 15 }}><div className="metric-label"><span>{preview.file_name}</span><span className="number">{number(preview.row_count)} rows · {preview.columns.length} columns</span></div><div className="table-scroll" style={{ marginTop: 8 }}><table><thead><tr>{preview.columns.slice(0, 6).map((col) => <th key={col}>{col}</th>)}</tr></thead><tbody>{preview.preview_rows.slice(0, 4).map((row, i) => <tr key={i}>{preview.columns.slice(0, 6).map((col) => <td key={col}>{String(row[col] ?? '—')}</td>)}</tr>)}</tbody></table></div></div>}
      </Panel>
      <Panel title="Map transaction columns" note="Choose which uploaded headers correspond to the expected fields">
        {preview ? <><div className="mapping-grid">{mappingFields.map((f) => <div key={f.key}><label className="field-label" htmlFor={`map-${f.key}`}>{f.label}{f.required ? ' · required' : ''}</label><select className="select" id={`map-${f.key}`} value={mapping[f.key] ?? ''} onChange={(e) => { setMapping({ ...mapping, [f.key]: e.target.value }); setAnalysis(null); }} data-testid={`select-map-${f.key}`}><option value="">Not mapped</option>{preview.columns.map((col) => <option value={col} key={col}>{col}</option>)}</select></div>)}</div><div style={{ display: 'flex', gap: 10, alignItems: 'center', marginTop: 16, flexWrap: 'wrap' }}><button className="button" disabled={!file || !requiredMapped || analyzeMutation.isPending} onClick={runAnalysis} data-testid="button-analyze-upload">{analyzeMutation.isPending ? <LoaderCircle /> : <FileSpreadsheet />}{analyzeMutation.isPending ? 'Analyzing' : 'Analyze descriptively'}</button><span className="tiny">{requiredMapped ? 'Required fields are mapped.' : 'Map each required field to continue.'}</span></div></> : <div className="empty-box">Upload a file to map its available headers.</div>}
      </Panel>
    </div>
    {analyzeMutation.isError && <div className="error-box" style={{ marginTop: 16 }}>Analysis failed. Check the required fields and selected mappings, then try again.</div>}
    {exportError && <div className="error-box" style={{ marginTop: 16 }}>{exportError}</div>}
    {a && <div style={{ marginTop: 16 }}>
      <div className="grid kpis">
        <Metric label="Cleaned rows" value={number(a.summary.cleaned_rows)} foot={`${number(a.summary.input_rows)} source rows`} icon={Database} />
        <Metric label="Customers" value={number(a.summary.customer_count)} foot={`${number(a.summary.order_count)} orders`} icon={Users} />
        <Metric label="Positive gross revenue" value={money(a.summary.positive_gross_revenue)} foot={`Reference date ${dateShort(a.summary.reference_date)}`} icon={Wallet} />
        <Metric label="Excluded rows" value={number(a.summary.excluded_rows)} foot={`${number(a.summary.duplicate_rows_removed)} duplicates removed`} icon={Filter} />
      </div>
      <div className="grid two">
        <Panel title="Cleaning and missing values" note="Descriptive quality checks on this upload">
          <div className="table-scroll"><table><thead><tr><th>Check</th><th>Rows</th></tr></thead><tbody><tr><td>Duplicate rows in input</td><td className="number">{number(a.summary.duplicate_rows)}</td></tr><tr><td>Missing customer rows removed</td><td className="number">{number(a.summary.missing_customer_rows_removed)}</td></tr><tr><td>Retained cancellation rows</td><td className="number">{number(a.summary.retained_cancellation_rows)}</td></tr><tr><td>Retained zero-price rows</td><td className="number">{number(a.summary.retained_zero_price_rows)}</td></tr>{a.missing_values.map((m) => <tr key={m.column}><td>Missing · {m.column}</td><td className="number">{number(m.missing_count)}</td></tr>)}</tbody></table></div>
        </Panel>
        <Panel title="Order frequency" note="Customers grouped by observed order count">
          {a.order_frequency.length ? <div className="chart-wrap"><ResponsiveContainer><BarChart data={a.order_frequency}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="label" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip /><Bar dataKey="customers" fill="#315a4c" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div> : <div className="empty-box">No order frequency groups.</div>}
        </Panel>
      </div>
      <div className="grid equal" style={{ marginTop: 16 }}>
        <Panel title="Revenue trend" note={a.trend_period ? `Grouped by ${a.trend_period}` : 'No trend period was returned'}>{a.revenue_trend.length ? <div className="chart-wrap"><ResponsiveContainer><AreaChart data={a.revenue_trend}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="period" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(v) => money(Number(v))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} width={56} /><Tooltip formatter={(v) => money(Number(v))} /><Area type="monotone" dataKey="revenue" stroke="#315a4c" fill="#d8e2d8" /></AreaChart></ResponsiveContainer></div> : <div className="empty-box">No revenue trend returned.</div>}</Panel>
        <Panel title="Customer feature preview" note="Derived RFM features from the uploaded records">
          {a.customer_features_preview.length ? <div className="table-scroll"><table><thead><tr>{Object.keys(a.customer_features_preview[0]).slice(0, 6).map((key) => <th key={key}>{key}</th>)}</tr></thead><tbody>{a.customer_features_preview.slice(0, 8).map((row, i) => <tr key={i}>{Object.keys(a.customer_features_preview[0]).slice(0, 6).map((key) => <td key={key}>{String(row[key] ?? '—')}</td>)}</tr>)}</tbody></table></div> : <div className="empty-box">No feature preview returned.</div>}
        </Panel>
      </div>
      <div className="grid equal" style={{ marginTop: 16 }}>
        {a.rfm_distributions.map((distribution) => <Panel key={distribution.field} title={distribution.label} note={`Descriptive distribution · ${distribution.field}`}>
          {distribution.bins.length ? <div className="chart-wrap"><ResponsiveContainer><BarChart data={distribution.bins.map((bin) => ({ ...bin, interval: `${bin.lower}–${bin.upper}` }))}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="interval" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => number(Number(value))} labelFormatter={(label) => `Range ${label}`} /><Bar dataKey="customers" name="Customers" fill="#78918a" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div> : <div className="empty-box">No distribution bins were returned.</div>}
        </Panel>)}
        {!a.rfm_distributions.length && <Panel title="RFM distributions" note="Descriptive customer-feature distributions"><div className="empty-box">No RFM distributions were returned for this upload.</div></Panel>}
      </div>
      <Panel title="Download analysis outputs" note="Exports reprocess the selected file using the current mapping; no file is stored" extra={<ArrowDownToLine size={15} color="#71847a" />}>
        <div className="filter-row"><button className="button secondary" disabled={!file || exportMutation.isPending} onClick={() => download('cleaned_transactions')} data-testid="button-export-cleaned"><ArrowDownToLine />Cleaned transactions CSV</button><button className="button secondary" disabled={!file || exportMutation.isPending} onClick={() => download('customer_features')} data-testid="button-export-features"><ArrowDownToLine />Customer features CSV</button>{exportMutation.isPending && <span className="tiny">Preparing download…</span>}</div>
      </Panel>
    </div>}
  </div>;
}

function Performance() {
  const q = useGetModelPerformance({ query: { queryKey: getGetModelPerformanceQueryKey() } });
  const image30 = useGetCalibrationImage({ query: { queryKey: getGetCalibrationImageQueryKey() } });
  const image90 = useGetCalibration90dImage({ query: { queryKey: getGetCalibration90dImageQueryKey() } });
  const url30 = image30.data?.url;
  const url90 = image90.data?.url;
  const d = q.data;
  return <div className="content">
    <PageHeading eyebrow="Notebook 06 / 07" title="Model performance" description="Saved evaluation metrics for purchase probabilities and revenue forecasts on the historical test set." />
    <HistoricalNotice />
    <QueryState loading={q.isLoading} error={q.isError} empty={!d} retry={() => void q.refetch()}>
      {d && <>
        <div className="grid kpis"><Metric label="Test customers" value={number(d.test_customers)} foot={`Evaluation cutoff ${dateShort(d.cutoff_date)}`} icon={Users} /><Metric label="Purchase metric rows" value={number(d.purchase_metrics.length)} foot="Across saved models and horizons" icon={BarChart3} /><Metric label="Revenue metric rows" value={number(d.revenue_metrics.length)} foot="Saved evaluation outcomes" icon={Wallet} /><Metric label="Group evaluation rows" value={number(d.revenue_group_metrics.length)} foot="Revenue by saved cohort group" icon={Filter} /></div>
        <div className="grid equal">
          <Panel title="Purchase prediction metrics" note="Saved Notebook 06 evaluation"><MetricTable rows={d.purchase_metrics} columns={[['model', 'Model'], ['horizon_days', 'Horizon'], ['brier_score', 'Brier score'], ['roc_auc', 'ROC AUC'], ['average_precision', 'Avg precision'], ['calibration_error', 'Calibration error'], ['log_loss', 'Log loss'], ['actual_purchase_rate', 'Actual rate']]} format={(key, value) => key.includes('rate') ? percent(Number(value)) : typeof value === 'number' ? key === 'horizon_days' ? `${value}d` : value.toFixed(3) : String(value)} /></Panel>
          <Panel title="Revenue forecast metrics" note="Saved Notebook 07 evaluation"><MetricTable rows={d.revenue_metrics} columns={[['model', 'Model'], ['horizon_days', 'Horizon'], ['mae', 'MAE'], ['rmse', 'RMSE'], ['mean_forecast_bias', 'Mean bias'], ['total_revenue_bias', 'Total bias'], ['aggregate_calibration_ratio', 'Calibration ratio']]} format={(key, value) => key === 'horizon_days' ? `${value}d` : key.includes('ratio') ? Number(value).toFixed(3) : key === 'model' ? String(value) : money(Number(value))} /></Panel>
        </div>
        <div className="grid equal" style={{ marginTop: 16 }}>
          <Panel title="Purchase-history evaluation" note="Saved evaluation grouped by historical customer history"><MetricTable rows={d.purchase_history_metrics} columns={[['history_group', 'History group'], ['horizon_days', 'Horizon'], ['n_customers', 'Customers'], ['actual_purchase_rate', 'Actual rate'], ['mean_predicted_probability', 'Mean predicted'], ['brier_score', 'Brier score'], ['roc_auc', 'ROC AUC']]} format={(key, value) => key === 'history_group' ? String(value) : key === 'horizon_days' ? `${value}d` : key === 'n_customers' ? number(Number(value)) : ['actual_purchase_rate', 'mean_predicted_probability'].includes(key) ? percent(Number(value)) : Number(value).toFixed(3)} /></Panel>
          <Panel title="Revenue by cohort group" note="Saved subgroup diagnostics"><MetricTable rows={d.revenue_group_metrics} columns={[['group_type', 'Group type'], ['group', 'Group'], ['model', 'Model'], ['horizon_days', 'Horizon'], ['mae', 'MAE'], ['rmse', 'RMSE'], ['aggregate_calibration_ratio', 'Calibration ratio']]} format={(key, value) => key === 'horizon_days' ? `${value}d` : key === 'aggregate_calibration_ratio' ? Number(value).toFixed(3) : ['mae', 'rmse'].includes(key) ? money(Number(value)) : String(value)} /></Panel>
        </div>
        <div className="grid equal" style={{ marginTop: 16 }}>
          <Panel title="Purchase-clock calibration" note="Saved calibration evaluation image">{image30.isLoading ? <div className="skeleton" /> : image30.isError ? <div className="empty-box">Calibration image could not be loaded.</div> : url30 ? <img src={url30} alt="Saved purchase-clock calibration plot" style={{ display: 'block', width: '100%', borderRadius: 7 }} /> : <div className="empty-box">No calibration image available.</div>}</Panel>
          <Panel title="90-day calibration" note="Saved 90-day calibration evaluation image">{image90.isLoading ? <div className="skeleton" /> : image90.isError ? <div className="empty-box">Calibration image could not be loaded.</div> : url90 ? <img src={url90} alt="Saved 90-day calibration plot" style={{ display: 'block', width: '100%', borderRadius: 7 }} /> : <div className="empty-box">No calibration image available.</div>}</Panel>
        </div>
      </>}
    </QueryState>
  </div>;
}
function MetricTable({ rows, columns, format }: { rows: object[]; columns: [string, string][]; format: (key: string, value: unknown) => string }) {
  if (!rows.length) return <div className="empty-box">No saved evaluation rows.</div>;
  return <div className="table-scroll"><table><thead><tr>{columns.map(([, label]) => <th key={label}>{label}</th>)}</tr></thead><tbody>{rows.map((item, i) => { const row = item as Record<string, unknown>; return <tr key={`${String(row.model ?? row.group ?? 'row')}-${i}`}>{columns.map(([key]) => <td className={typeof row[key] === 'number' ? 'number' : ''} key={key}>{format(key, row[key])}</td>)}</tr>; })}</tbody></table></div>;
}
function NotFound() {
  return <div className="content"><PageHeading eyebrow="Not found" title="This workspace page is unavailable" description="Choose a destination from the workspace navigation." /><NavLink className="button" to="/">Return to overview</NavLink></div>;
}
function App() {
  return <QueryClientProvider client={queryClient}><BrowserRouter><AppShell /></BrowserRouter></QueryClientProvider>;
}
export default App;
