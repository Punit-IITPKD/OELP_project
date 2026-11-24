import { useMemo, useState } from 'react';
import { ShoppingBag, Sparkles, Users, Wallet } from 'lucide-react';
import { getGetOverviewQueryKey, useGetOverview } from '@workspace/api-client-react';
import { HistoricalNotice, Metric, PageHeading, Panel, QueryState, money, number, percent, dateShort } from '../components/app-shared';

function MonthlyTrend({ rows }: { rows: Array<{ month: string; revenue: number; orders: number }> }) {
  const width = 760;
  const height = 245;
  const left = 42;
  const right = 24;
  const top = 18;
  const bottom = 34;
  const plotWidth = width - left - right;
  const plotHeight = height - top - bottom;
  const maxRevenue = Math.max(1, ...rows.map((row) => row.revenue));
  const maxOrders = Math.max(1, ...rows.map((row) => row.orders));
  const step = rows.length > 1 ? plotWidth / (rows.length - 1) : plotWidth;
  const barWidth = Math.min(24, plotWidth / Math.max(rows.length * 1.8, 1));
  const points = rows.map((row, index) => ({
    x: left + step * index,
    y: top + plotHeight - (row.orders / maxOrders) * plotHeight,
  }));
  const linePath = points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ');
  const labelIndexes = new Set([0, Math.floor((rows.length - 1) / 2), rows.length - 1]);
  return <div className="chart-wrap overview-trend-wrap">
    <svg className="overview-trend-svg" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Monthly historical revenue bars and order-count line">
      <title>Monthly historical revenue and order counts</title>
      {[0, 0.5, 1].map((fraction) => {
        const y = top + plotHeight * fraction;
        return <g key={fraction}><line x1={left} x2={width - right} y1={y} y2={y} stroke="#ebe8de" /><text x={left - 8} y={y + 3} textAnchor="end" fill="#89938c" fontSize="9">{money(maxRevenue * (1 - fraction))}</text></g>;
      })}
      {rows.map((row, index) => {
        const x = left + step * index;
        const barHeight = (row.revenue / maxRevenue) * plotHeight;
        return <g key={row.month}>
          <rect x={x - barWidth / 2} y={top + plotHeight - barHeight} width={barWidth} height={barHeight} rx="3" fill="#315a4c">
            <title>{`${row.month}: ${money(row.revenue)} revenue, ${number(row.orders)} orders`}</title>
          </rect>
          {labelIndexes.has(index) && <text x={x} y={height - 10} textAnchor="middle" fill="#89938c" fontSize="9">{row.month}</text>}
        </g>;
      })}
      <path d={linePath} fill="none" stroke="#d49a65" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
      {points.map((point, index) => <circle key={rows[index].month} cx={point.x} cy={point.y} r="3.5" fill="#d49a65" stroke="#fffefa" strokeWidth="1.5">
        <title>{`${rows[index].month}: ${number(rows[index].orders)} orders`}</title>
      </circle>)}
    </svg>
  </div>;
}

function SegmentBars({ rows }: { rows: Array<{ segment: string; customers: number }> }) {
  const maxCustomers = Math.max(1, ...rows.map((row) => row.customers));
  return <div className="overview-segment-bars" aria-label="Customer counts by descriptive segment">
    {rows.map((row) => <div className="overview-segment-row" key={row.segment}>
      <span>{row.segment}</span>
      <div className="overview-segment-track" role="img" aria-label={`${row.segment}: ${number(row.customers)} customers`}>
        <div style={{ width: `${Math.max(2, row.customers / maxCustomers * 100)}%` }} />
      </div>
      <strong>{number(row.customers)}</strong>
    </div>)}
  </div>;
}

export default function OverviewPage() {
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
            {data.monthly_trend.length ? <MonthlyTrend rows={data.monthly_trend} /> : <div className="empty-box">No monthly trend rows in the saved response.</div>}
          </Panel>
          <Panel title="Descriptive RFM mix" note="Customer share by segment; descriptive classification, not a forecast cohort">
            {segmentData.length ? <SegmentBars rows={segmentData} /> : <div className="empty-box">No descriptive segments in this response.</div>}
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
