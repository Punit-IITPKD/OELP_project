import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { NavLink } from 'react-router-dom';
import {
  ArrowDownToLine, ArrowLeftRight, Clock3, Search, ShieldCheck, ShoppingBag, Users, Wallet,
} from 'lucide-react';
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import {
  getGetCustomerExplanationQueryKey, getGetCustomerForecastQueryKey, getGetCustomerHistoryQueryKey,
  getGetCustomerQueryKey, getGetCustomerReliabilityQueryKey, getGetCustomersQueryKey,
  getGetRevenueExposureCustomerQueryKey, useGetCustomer, useGetCustomerExplanation,
  useGetCustomerForecast, useGetCustomerHistory, useGetCustomerReliability, useGetCustomers,
  useGetRevenueExposureCustomer,
} from '@workspace/api-client-react';
import type { CustomerListItem } from '@workspace/api-client-react';
import BehaviorHistory from '../BehaviorHistory';
import {
  HistoricalNotice, KeyValueTable, Metric, PageHeading, Panel, QueryState,
  displayValue, dateShort, money, number, percent,
} from '../components/app-shared';

function RevenueExposureProfile({ customerId, cutoffDate }: { customerId: number; cutoffDate: string }) {
  const [horizon, setHorizon] = useState<30 | 60 | 90>(30);
  const params = useMemo(() => ({ horizon_days: horizon }), [horizon]);
  const detail = useGetRevenueExposureCustomer(customerId, params, {
    query: {
      queryKey: getGetRevenueExposureCustomerQueryKey(customerId, params),
      enabled: customerId > 0,
    },
  });
  const row = detail.data;
  return <Panel
    title="Revenue Exposure & Strategy"
    note="Saved forecast and group evidence for this customer at the same historical cutoff; no campaign outcome is inferred."
    extra={<label className="field-label">Horizon <select className="input revenue-profile-horizon" value={horizon} onChange={(event) => setHorizon(Number(event.target.value) as 30 | 60 | 90)} data-testid="select-customer-revenue-horizon"><option value={30}>30 days</option><option value={60}>60 days</option><option value={90}>90 days</option></select></label>}
  >
    <QueryState loading={detail.isLoading} error={detail.isError} empty={!row} retry={() => void detail.refetch()}>
      {row && <>
        <div className="revenue-profile-grid" data-testid="section-customer-revenue-exposure">
          <div><span>Cutoff</span><strong>{dateShort(row.cutoff_date)}</strong></div>
          <div><span>Purchase probability</span><strong>{percent(row.purchase_probability)}</strong></div>
          <div><span>Conditional expected spending</span><strong>{money(row.conditional_expected_spending_gbp)}</strong></div>
          <div><span>Personalized expected revenue</span><strong>{money(row.personalized_expected_revenue_gbp)}</strong></div>
          <div><span>Nonreturn-spending proxy</span><strong>{money(row.nonreturn_weighted_conditional_spending_proxy_gbp)}</strong></div>
          <div><span>Reference exposure</span><strong>{money(row.estimated_revenue_exposure_gbp)}</strong></div>
          <div><span>Reliability group</span><strong>{row.reliability_status}</strong></div>
          <div><span>Historical evidence</span><strong>{number(row.reliability_evidence_count)} records</strong></div>
          <div><span>Scenario eligibility</span><strong>Check against active planner filters</strong></div>
        </div>
        <div className="revenue-profile-footer">
          <span>Same profile cutoff: {dateShort(cutoffDate)} · Group evidence is not an individual guarantee.</span>
          <NavLink className="button secondary" to={`/revenue-exposure?customer_id=${customerId}&horizon_days=${horizon}`} data-testid="link-customer-revenue-planner">Open planner for customer {customerId}</NavLink>
        </div>
      </>}
    </QueryState>
  </Panel>;
}

function CustomerResearchDetails({ customerId, cutoffDate, historyGroup }: {
  customerId: number;
  cutoffDate: string;
  historyGroup: string;
}) {
  const [horizon, setHorizon] = useState<30 | 60 | 90>(30);
  const [showExplanation, setShowExplanation] = useState(false);
  const [showReliability, setShowReliability] = useState(false);
  const params = useMemo(() => ({ horizon_days: horizon }), [horizon]);
  const explanation = useGetCustomerExplanation(customerId, params, {
    query: { queryKey: getGetCustomerExplanationQueryKey(customerId, params), enabled: showExplanation },
  });
  const reliability = useGetCustomerReliability(customerId, params, {
    query: { queryKey: getGetCustomerReliabilityQueryKey(customerId, params), enabled: showReliability },
  });
  const e = explanation.data;
  const r = reliability.data;
  return <div className="research-stack">
    <Panel title="Forecast explanation & group context" note="Request detail only when needed. All evidence refers to the saved model at its historical cutoff.">
      <div className="research-controls">
        <div className="field horizon-field"><label className="field-label" htmlFor="customer-research-horizon">Forecast horizon</label><select id="customer-research-horizon" className="select" value={horizon} onChange={(event) => setHorizon(Number(event.target.value) as 30 | 60 | 90)} data-testid="select-customer-research-horizon"><option value={30}>30 days</option><option value={60}>60 days</option><option value={90}>90 days</option></select></div>
        <button className="button" onClick={() => setShowExplanation(true)} data-testid="button-load-customer-explanation">Explain saved forecast</button>
        <button className="button secondary" onClick={() => setShowReliability(true)} data-testid="button-load-customer-reliability">Show group reliability</button>
        <span className="tiny">Cutoff {dateShort(cutoffDate)} · {historyGroup || 'History group not recorded'}</span>
      </div>
    </Panel>
    {showExplanation && <Panel title={`Why this ${horizon}-day forecast?`} note="Feature substitutions are noncausal model-input sensitivities, not interventions or explanations of customer intent.">
      <QueryState loading={explanation.isLoading} error={explanation.isError} empty={!e} retry={() => void explanation.refetch()}>
        {e && <>
          <div className="research-callout"><strong>Saved output:</strong> {percent(e.purchase_probability)} purchase probability · {money(e.personalized_expected_revenue)} personalized expected revenue · {money(e.conditional_expected_spending)} conditional expected spending. <span className="tiny">Model {e.model_version} · cutoff {dateShort(e.cutoff_date)} · {e.horizon_days}-day horizon</span></div>
          <div className="grid equal">
            <Panel title="Forecast vs reference" note="Reference probabilities are retained train-reference values">
              <KeyValueTable values={e.purchase_probabilities} valueFormat={(value) => percent(Number(value))} />
              <div className="research-subhead">Reference probabilities</div>
              <KeyValueTable values={e.reference_probabilities} valueFormat={(value) => percent(Number(value))} />
            </Panel>
            <Panel title="Model inputs at cutoff" note="Inputs used by this saved customer forecast"><KeyValueTable values={e.model_input} /></Panel>
          </div>
          <div className="grid equal" style={{ marginTop: 14 }}>
            <Panel title="Feature substitutions" note="Noncausal model-input sensitivities against saved reference values">
              {e.feature_effects.length ? <div className="table-scroll"><table><thead><tr><th>Feature</th><th>Observed input</th><th>Reference input</th><th>Reference probabilities</th><th>Probability effects</th></tr></thead><tbody>{e.feature_effects.map((effect, index) => <tr key={`${effect.feature}-${index}`}><td>{effect.feature}</td><td>{displayValue(effect.original_value)}</td><td>{displayValue(effect.reference_value)}</td><td>{displayValue(effect.reference_probabilities)}</td><td>{displayValue(effect.probability_effects)}</td></tr>)}</tbody></table></div> : <div className="empty-box">No feature sensitivity rows were returned.</div>}
              <p className="tiny">A substitution changes model inputs for comparison only. It does not establish causality or a real-world outcome.</p>
            </Panel>
            <Panel title="Interval evidence" note="Saved hazard reconstruction contributions by interval">
              {e.interval_decompositions.length ? <div className="table-scroll"><table><thead><tr><th>Interval</th><th>Predicted hazard</th><th>Reconstructed</th><th>Contributions</th></tr></thead><tbody>{e.interval_decompositions.map((item) => <tr key={`${item.interval_days}-${item.customer_id}`}><td>{item.interval_days} days</td><td className="number">{percent(item.predicted_hazard)}</td><td className="number">{percent(item.reconstructed_hazard)}</td><td>{item.feature_contributions.map((contribution) => `${contribution.model_feature}: ${number(contribution.logit_contribution)}`).join(' · ') || '—'}</td></tr>)}</tbody></table></div> : <div className="empty-box">No interval decomposition was returned.</div>}
            </Panel>
          </div>
          <div className="grid equal" style={{ marginTop: 14 }}>
            <Panel title="Spending model evidence" note={`Retransformation: ${e.retransformation_method}`}>
              <KeyValueTable values={{ conditional_expected_spending: e.conditional_expected_spending, personalized_expected_revenue: e.personalized_expected_revenue, spending_log_score: e.spending_log_score }} valueFormat={(value, key) => key === 'spending_log_score' ? number(Number(value)) : money(Number(value))} />
              {e.spending_log_score_contributions.length > 0 && <div className="table-scroll" style={{ marginTop: 10 }}><table><thead><tr><th>Model feature</th><th>Log-score contribution</th></tr></thead><tbody>{e.spending_log_score_contributions.map((item, index) => <tr key={`${item.model_feature}-${index}`}><td>{item.model_feature}</td><td className="number">{number(item.log_score_contribution)}</td></tr>)}</tbody></table></div>}
              {e.spending_reference_sensitivities.length > 0 && <div className="table-scroll" style={{ marginTop: 10 }}><table><thead><tr><th>Reference substitution</th><th>Log-score difference</th><th>Conditional-spending difference</th><th>Direction</th></tr></thead><tbody>{e.spending_reference_sensitivities.map((item, index) => <tr key={`${item.feature}-${index}`}><td>{item.feature} · {displayValue(item.reference_value)}</td><td className="number">{number(item.log_score_difference)}</td><td className="number">{money(item.conditional_spending_difference)}</td><td>{item.effect_direction}</td></tr>)}</tbody></table></div>}
            </Panel>
            <Panel title="Limitations" note="Interpret this saved output within its research scope"><ul className="research-list">{[...e.model_input_limitations, ...e.limitations].map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul></Panel>
          </div>
        </>}
      </QueryState>
    </Panel>}
    {showReliability && <Panel title="Historical reliability context" note="Group-level TEST diagnostics describe evaluation cohorts, not the individual customer's outcome or a guarantee.">
      <QueryState loading={reliability.isLoading} error={reliability.isError} empty={!r} retry={() => void reliability.refetch()}>
        {r && <>
          <div className="research-callout"><strong>{r.reliability_status}</strong> · {r.history_group} · {r.horizon_days}-day horizon · {number(r.evaluation_group_count)} customers evaluated · cutoff {dateShort(r.cutoff_date)}</div>
          <div className="grid equal">
            <Panel title="Group diagnostics" note="Scores summarize the matching historical evaluation group only"><KeyValueTable values={{ group_brier_score: r.group_brier_score, group_calibration_gap: r.group_calibration_gap }} /></Panel>
            <Panel title="Distribution support" note="Input support flags describe how the saved model's inputs compare with its training distribution">
              {r.distribution_support_flags.length ? <div className="research-flags">{r.distribution_support_flags.map((flag, index) => <div className="research-flag" key={`${flag.model_scope}-${index}`}><strong>{flag.model_scope} · {flag.status}</strong><span>{flag.interpretation}</span><span className="tiny">{number(flag.atypical_feature_count)} atypical features · {flag.flags.length} flags</span>{flag.flags.length > 0 && <span className="research-flag-detail">{displayValue(flag.flags)}</span>}</div>)}</div> : <div className="empty-box">No input-support flags were returned.</div>}
            </Panel>
          </div>
          {r.limitations.length > 0 && <ul className="research-list">{r.limitations.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul>}
        </>}
      </QueryState>
    </Panel>}
  </div>;
}

export default function IntelligencePage() {
  const [search, setSearch] = useState('');
  const [submitted, setSubmitted] = useState('');
  const [customerId, setCustomerId] = useState<number | null>(null);
  const params = useMemo(() => ({ page: 1, page_size: 8, search: submitted || undefined }), [submitted]);
  const list = useGetCustomers(params, { query: { queryKey: getGetCustomersQueryKey(params), enabled: submitted.length > 0 } });
  const profile = useGetCustomer(customerId ?? 0, { query: { queryKey: getGetCustomerQueryKey(customerId ?? 0), enabled: customerId !== null } });
  const history = useGetCustomerHistory(customerId ?? 0, { query: { queryKey: getGetCustomerHistoryQueryKey(customerId ?? 0), enabled: customerId !== null } });
  const forecast = useGetCustomerForecast(customerId ?? 0, { query: { queryKey: getGetCustomerForecastQueryKey(customerId ?? 0), enabled: customerId !== null } });
  const onSearch = (event: FormEvent) => { event.preventDefault(); setSubmitted(search.trim()); setCustomerId(null); };
  const p = profile.data;
  const exportCustomerForecast = () => {
    if (!p) return;
    const rows: [string, string | number][] = [
      ['customer_id', p.customer_id], ['cutoff_date', p.cutoff_date], ['hist_segment', p.hist_segment],
      ['history_group', p.history_group], ['global_purchase_probability_30d', p.global_purchase_probability_30d],
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
      <form className="filter-row" onSubmit={onSearch}><div className="field" style={{ maxWidth: 410 }}><label className="field-label" htmlFor="customer-search">Customer ID</label><div style={{ position: 'relative' }}><Search size={15} style={{ position: 'absolute', top: 11, left: 11, color: '#85938b' }} /><input className="input" id="customer-search" style={{ paddingLeft: 34 }} value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Enter a saved Customer ID" data-testid="input-customer-id" /></div></div><button className="button" type="submit" data-testid="button-search-customer"><Search />Search records</button></form>
      {submitted && !customerId && <QueryState loading={list.isLoading} error={list.isError} empty={list.data?.items.length === 0} retry={() => void list.refetch()}>{list.data && <div className="table-scroll"><table><thead><tr><th>Customer ID</th><th>Full-period retrospective RFM</th><th>Historical cutoff cohort</th><th>Cutoff frequency</th><th>Cutoff gross spend</th><th></th></tr></thead><tbody>{list.data.items.map((customer: CustomerListItem) => <tr key={customer.customer_id}><td className="number">{customer.customer_id}</td><td><span className="badge">{customer.retrospective_description.descriptive_segment}</span></td><td>{customer.hist_segment ?? '—'}</td><td className="number">{number(customer.frequency)}</td><td className="number">{money(customer.monetary_gross)}</td><td><button className="button secondary" onClick={() => setCustomerId(customer.customer_id)} data-testid={`button-open-customer-${customer.customer_id}`}>Open profile</button></td></tr>)}</tbody></table></div>}</QueryState>}
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
          {[['30 days', p.purchase_probability_30d], ['60 days', p.purchase_probability_60d], ['90 days', p.purchase_probability_90d]].map(([label, value]) => <div className="prob-row" key={label as string}><span>{label}</span><div className="track"><div className="fill" style={{ width: `${Math.max(0, Math.min(100, Number(value) * 100))}%` }} /></div><strong className="number">{percent(Number(value))}</strong></div>)}
          <div className="tiny" style={{ marginTop: 15 }}>Global / segment / personalized are retained separately in the saved forecast record.</div>
          <div className="table-scroll" style={{ marginTop: 10 }}><table><thead><tr><th>Horizon</th><th>Global</th><th>Segment</th><th>Personalized</th><th>Expected spend</th></tr></thead><tbody>{[30, 60, 90].map((days) => <tr key={days}><td>{days}d</td><td className="number">{percent(p[`global_purchase_probability_${days}d` as 'global_purchase_probability_30d' | 'global_purchase_probability_60d' | 'global_purchase_probability_90d'])}</td><td className="number">{percent(p[`segment_purchase_probability_${days}d` as 'segment_purchase_probability_30d' | 'segment_purchase_probability_60d' | 'segment_purchase_probability_90d'])}</td><td className="number">{percent(p[`purchase_probability_${days}d` as 'purchase_probability_30d' | 'purchase_probability_60d' | 'purchase_probability_90d'])}</td><td className="number">{money(p[`personalized_expected_revenue_${days}d` as 'personalized_expected_revenue_30d' | 'personalized_expected_revenue_60d' | 'personalized_expected_revenue_90d'])}</td></tr>)}</tbody></table></div>
        </Panel>
        <Panel title="Cumulative probability curve" note="Saved customer-level curve"><QueryState loading={forecast.isLoading} error={forecast.isError} empty={!forecast.data?.cumulative_curve.length} retry={() => void forecast.refetch()}>{forecast.data && <div className="chart-wrap"><ResponsiveContainer><AreaChart data={forecast.data.cumulative_curve}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="day" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis domain={[0, 1]} tickFormatter={(value) => percent(Number(value))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => percent(Number(value))} labelFormatter={(value) => `Day ${value}`} /><Area type="monotone" dataKey="probability" stroke="#315a4c" fill="#d8e2d8" strokeWidth={2} /></AreaChart></ResponsiveContainer></div>}</QueryState></Panel>
        <Panel title="Purchase history" note="Orders before the historical cutoff"><QueryState loading={history.isLoading} error={history.isError} empty={!history.data?.length} retry={() => void history.refetch()}>{history.data && <div className="table-scroll"><table><thead><tr><th>Purchase date</th><th>Invoice</th><th>Gross revenue</th></tr></thead><tbody>{history.data.map((order, index) => <tr key={`${order.invoice}-${index}`}><td>{dateShort(order.purchase_date)}</td><td className="number">{order.invoice}</td><td className="number">{money(order.gross_revenue)}</td></tr>)}</tbody></table></div>}</QueryState></Panel>
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
      {p && <div style={{ marginTop: 16 }}><CustomerResearchDetails customerId={p.customer_id} cutoffDate={p.cutoff_date} historyGroup={p.history_group} /></div>}
      {p && <div style={{ marginTop: 16 }}><RevenueExposureProfile customerId={p.customer_id} cutoffDate={p.cutoff_date} /></div>}
      {p && <div style={{ marginTop: 16 }}><BehaviorHistory customerId={p.customer_id} /></div>}
      {p && <div style={{ marginTop: 16 }}><Panel title="Historical Purchasing Trajectory" note="Explore observed purchase and revenue rates by historical exposure window; no future individual outcome is displayed.">
        <div className="trajectory-profile-link"><div><strong>See the customer’s trajectory in context</strong><span>Compare recorded history support, cluster availability and aggregate profiles at the saved cutoff.</span></div><NavLink className="button secondary" to={`/trajectories?customer_id=${p.customer_id}`} data-testid="link-customer-trajectory">Open trajectory explorer</NavLink></div>
      </Panel></div>}
    </div>}
  </div>;
}
