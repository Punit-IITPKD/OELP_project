import { useMemo, useState } from 'react';
import { ArrowDownToLine } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import {
  getGetCustomersQueryKey, getGetSegmentsQueryKey, useGetCustomers, useGetSegments,
} from '@workspace/api-client-react';
import type { GetCustomersHistoryGroup } from '@workspace/api-client-react';
import { HistoricalNotice, PageHeading, Panel, QueryState, money, number, percent } from '../components/app-shared';

export default function SegmentsPage() {
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
      'customer_id', 'retrospective_segment', 'hist_segment', 'history_group',
      'cutoff_recency_days', 'cutoff_frequency', 'cutoff_gross_spend',
      'retrospective_net_spend', 'retrospective_average_order_value',
      'retrospective_at_risk_flag', 'retrospective_source_start', 'retrospective_source_end',
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
