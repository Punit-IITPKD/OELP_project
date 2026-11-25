import { useMemo, useState } from 'react';
import { Activity, Users } from 'lucide-react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import {
  getGetForecastSummaryQueryKey, getGetSegmentsQueryKey, useGetForecastSummary, useGetSegments,
} from '@workspace/api-client-react';
import { HistoricalNotice, Metric, PageHeading, Panel, QueryState, dateShort, money, number, percent } from '../components/app-shared';

export default function ForecastingPage() {
  const [segment, setSegment] = useState('');
  const [historyGroup, setHistoryGroup] = useState('');
  const [visibleModels, setVisibleModels] = useState({ global: true, segment: true, personalized: true });
  const params = useMemo(() => ({ hist_segment: segment || undefined, history_group: historyGroup.trim() || undefined }), [segment, historyGroup]);
  const q = useGetForecastSummary(params, { query: { queryKey: getGetForecastSummaryQueryKey(params) } });
  const segments = useGetSegments({ query: { queryKey: getGetSegmentsQueryKey() } });
  const data = q.data;
  const anyModelVisible = Object.values(visibleModels).some(Boolean);
  return <div className="content">
    <PageHeading eyebrow="Saved model outputs" title="Forecast workspace" description="Compare model outputs for historical customer cohorts and validated horizons." />
    <HistoricalNotice />
    <Panel title="Cohort filters" note="Filtering applies to saved historical cohort labels; it does not change or retrain a model">
      <div className="filter-row"><div className="field" style={{ maxWidth: 300 }}><label className="field-label" htmlFor="forecast-segment">Historical cohort</label><select id="forecast-segment" className="select" value={segment} onChange={(event) => setSegment(event.target.value)} data-testid="select-historical-cohort"><option value="">All historical cohorts</option>{(segments.data?.historical_segments ?? []).map((item) => <option value={item.segment} key={item.segment}>{item.segment}</option>)}</select></div><div className="field" style={{ maxWidth: 260 }}><label className="field-label" htmlFor="forecast-history-group">History group</label><input id="forecast-history-group" className="input" value={historyGroup} onChange={(event) => setHistoryGroup(event.target.value)} placeholder="Filter by history group" data-testid="input-history-group" /></div><div className="tiny">Data cutoff: {dateShort(data?.cutoff_date)}</div></div>
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
    <div style={{ marginTop: 16 }}><QueryState loading={q.isLoading} error={q.isError} empty={!data} retry={() => void q.refetch()}>{data && <>
      <div className="grid kpis">
        <Metric label="Eligible customers" value={number(data.eligible_customers)} foot={`Cutoff ${dateShort(data.cutoff_date)}`} icon={Users} />
        <Metric label="Expected returners · 30d" value={number(data.expected_returners_30d)} foot="Saved-model cohort total" icon={Activity} />
        <Metric label="Expected returners · 60d" value={number(data.expected_returners_60d)} foot="Saved-model cohort total" icon={Activity} />
        <Metric label="Expected returners · 90d" value={number(data.expected_returners_90d)} foot="Saved-model cohort total" icon={Activity} />
      </div>
      <div className="grid two">
        <Panel title="Purchase probability by horizon" note={`Historical segment: ${data.hist_segment || 'All cohorts'} · cutoff ${dateShort(data.cutoff_date)}`}>
          {data.horizons.length && anyModelVisible ? <div className="chart-wrap"><ResponsiveContainer><LineChart data={data.horizons}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="days" tickFormatter={(value) => `${value}d`} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis domain={[0, 1]} tickFormatter={(value) => percent(Number(value))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => percent(Number(value))} labelFormatter={(value) => `${value} day horizon`} />{visibleModels.global && <Line type="monotone" dataKey="global_probability" name="Global" stroke="#78918a" strokeWidth={2} />}{visibleModels.segment && <Line type="monotone" dataKey="segment_probability" name="Segment" stroke="#c57d5c" strokeWidth={2} />}{visibleModels.personalized && <Line type="monotone" dataKey="personalized_probability" name="Personalized" stroke="#315a4c" strokeWidth={2.5} />}<Legend /></LineChart></ResponsiveContainer></div> : <div className="empty-box">{data.horizons.length ? 'Select at least one model to display the comparison.' : 'No saved horizon comparisons.'}</div>}
        </Panel>
        <Panel title="Expected revenue comparison" note="Expected revenue across saved comparison models">
          {data.horizons.length && anyModelVisible ? <div className="chart-wrap"><ResponsiveContainer><BarChart data={data.horizons}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="days" tickFormatter={(value) => `${value}d`} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(value) => money(Number(value))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} width={58} /><Tooltip formatter={(value) => money(Number(value))} labelFormatter={(value) => `${value} day horizon`} />{visibleModels.global && <Bar dataKey="historical_rate_expected_revenue" name="Global" fill="#78918a" radius={[3, 3, 0, 0]} />}{visibleModels.segment && <Bar dataKey="segment_expected_revenue" name="Segment" fill="#d8ad5e" radius={[3, 3, 0, 0]} />}{visibleModels.personalized && <Bar dataKey="personalized_expected_revenue" name="Personalized" fill="#315a4c" radius={[3, 3, 0, 0]} />}<Legend /></BarChart></ResponsiveContainer></div> : <div className="empty-box">{data.horizons.length ? 'Select at least one model to display the comparison.' : 'No revenue comparisons saved.'}</div>}
        </Panel>
      </div>
      <div className="grid equal" style={{ marginTop: 16 }}>
        <Panel title="Cumulative returner curve" note="Saved cohort probability curve">{data.cumulative_curve.length ? <div className="chart-wrap"><ResponsiveContainer><AreaChart data={data.cumulative_curve}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="day" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis domain={[0, 1]} tickFormatter={(value) => percent(Number(value))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => percent(Number(value))} /><Area type="monotone" dataKey="probability" stroke="#315a4c" fill="#d8e2d8" strokeWidth={2} /></AreaChart></ResponsiveContainer></div> : <div className="empty-box">No cumulative curve available.</div>}</Panel>
        <Panel title="Saved comparison values" note="The forecast is historical, and cohort totals are not realized outcomes"><div className="table-scroll"><table><thead><tr><th>Horizon</th>{visibleModels.global && <th>Global probability</th>}{visibleModels.segment && <th>Segment probability</th>}{visibleModels.personalized && <th>Personalized probability</th>}</tr></thead><tbody>{data.horizons.map((horizon) => <tr key={horizon.days}><td>{horizon.days} days</td>{visibleModels.global && <td className="number">{percent(horizon.global_probability)}</td>}{visibleModels.segment && <td className="number">{percent(horizon.segment_probability)}</td>}{visibleModels.personalized && <td className="number">{percent(horizon.personalized_probability)}</td>}</tr>)}</tbody></table></div></Panel>
      </div>
    </>}</QueryState></div>
  </div>;
}
