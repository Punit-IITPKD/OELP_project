import { useGetCustomerBehavior, getGetCustomerBehaviorQueryKey, useGetCustomerBehaviorTrajectory, getGetCustomerBehaviorTrajectoryQueryKey } from '@workspace/api-client-react';
import type { BehaviorCustomerDetail } from '@workspace/api-client-react';
import { AlertCircle, History } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const fmt = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : new Intl.NumberFormat('en-GB', { maximumFractionDigits: 2 }).format(value);
const pct = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : `${(value * 100).toFixed(1)}%`;
const pounds = (value?: number | null) => value == null || !Number.isFinite(value) ? '—' : new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(value);

function Value({ label, value }: { label: string; value: string }) {
  return <div className="behavior-value"><span>{label}</span><strong className="number">{value}</strong></div>;
}

export default function BehaviorHistory({ customerId }: { customerId: number }) {
  const detail = useGetCustomerBehavior(customerId, { query: { enabled: Boolean(customerId), queryKey: getGetCustomerBehaviorQueryKey(customerId) } });
  const trajectory = useGetCustomerBehaviorTrajectory(customerId, { query: { enabled: Boolean(customerId), queryKey: getGetCustomerBehaviorTrajectoryQueryKey(customerId) } });
  const d = detail.data as BehaviorCustomerDetail | undefined;
  return <section className="panel behavior-history" data-testid="section-behavior-history">
    <div className="panel-head"><div><div className="panel-title"><History size={15} style={{ verticalAlign: 'text-bottom', marginRight: 7 }} />Behavior history</div><div className="panel-note">Continuous historical indicators at the saved cutoff; not churn alerts or live recommendations.</div></div>{d && <span className="badge neutral">Cutoff {d.cutoff_date}</span>}</div>
    {detail.isLoading ? <div className="skeleton" aria-label="Loading behavior history" /> : detail.isError ? <div className="error-box"><AlertCircle size={15} /> Behavior history could not be loaded. <button className="button secondary" onClick={() => void detail.refetch()}>Try again</button></div> : !d ? <div className="empty-box">No behavior history is available for this customer.</div> : <>
      <div className="behavior-value-grid">
        <Value label="Elapsed gap" value={`${fmt(d.current_elapsed_gap_days)} days`} />
        <Value label="Median completed gap" value={`${fmt(d.median_completed_gap_days)} days`} />
        <Value label="Gap deviation" value={fmt(d.gap_deviation_score)} />
        <Value label="Purchase-rate ratio" value={fmt(d.purchase_rate_ratio)} />
        <Value label="Revenue-rate ratio" value={fmt(d.revenue_rate_ratio)} />
        <Value label="History sufficiency" value={d.history_sufficiency} />
      </div>
      <div className="behavior-profile-probabilities">
        <span>Historical purchase probabilities</span>
        <strong>30d {pct(d.purchase_probability_30d)}</strong><strong>60d {pct(d.purchase_probability_60d)}</strong><strong>90d {pct(d.purchase_probability_90d)}</strong>
      </div>
      <div className="tiny" style={{ margin: '11px 0' }}>Policy {d.policy_version} · {d.policy_status} · {d.available_indicator_count} indicators available</div>
      <div className="behavior-policy-note" data-testid="copy-no-alert-policy">No validated alert policy is available. These are continuous historical indicators, not churn alerts or live recommendations.</div>
      {!!d.indicator_explanations.length && <ul className="behavior-explanations">{d.indicator_explanations.map((text, i) => <li key={`${i}-${text}`}>{text}</li>)}</ul>}
      {d.alert_reasons.length > 0 && <div className="behavior-policy-note">Alert reasons are not interpreted as validated alerts.</div>}
      <div className="behavior-history-chart">
        {trajectory.isLoading ? <div className="skeleton" aria-label="Loading customer trajectory" /> : trajectory.isError ? <div className="error-box">Trajectory could not be loaded. <button className="button secondary" onClick={() => void trajectory.refetch()}>Try again</button></div> : trajectory.data?.items.length ? <div className="chart-wrap short"><ResponsiveContainer><AreaChart data={trajectory.data.items}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="period_start" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(value, name) => [name === 'Revenue rate' ? pounds(Number(value)) : fmt(Number(value)), name]} /><Area type="monotone" dataKey="order_rate" name="Order rate" stroke="#315a4c" fill="#d8e2d8" /><Area type="monotone" dataKey="revenue_rate" name="Revenue rate" stroke="#c57d5c" fill="#f3e4d8" /></AreaChart></ResponsiveContainer></div> : <div className="empty-box">No trajectory points are available.</div>}
      </div>
    </>}
  </section>;
}
