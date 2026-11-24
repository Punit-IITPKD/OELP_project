import { useMemo, useState } from 'react';
import { BarChart3, Filter, Users, Wallet } from 'lucide-react';
import {
  getGetCalibration90dImageQueryKey, getGetCalibrationImageQueryKey, getGetModelPerformanceQueryKey,
  getGetReliabilityCalibrationQueryKey, getGetReliabilityRevenueQueryKey,
  getGetReliabilitySubgroupsQueryKey, getGetReliabilitySummaryQueryKey,
  useGetCalibration90dImage, useGetCalibrationImage, useGetModelPerformance,
  useGetReliabilityCalibration, useGetReliabilityRevenue, useGetReliabilitySubgroups,
  useGetReliabilitySummary,
} from '@workspace/api-client-react';
import {
  CalibrationBins, DynamicRecordTable, HistoricalNotice, KeyValueTable, Metric, MetricTable, PageHeading,
  Panel, QueryState, ReliabilityMetricTable, dateShort, displayValue, money, number, percent,
} from '../components/app-shared';

export default function PerformancePage() {
  const [tab, setTab] = useState<'overall' | 'calibration' | 'subgroups' | 'revenue' | 'methodology'>('overall');
  const [subgroupHorizon, setSubgroupHorizon] = useState<30 | 60 | 90>(30);
  const q = useGetModelPerformance({ query: { queryKey: getGetModelPerformanceQueryKey() } });
  const image30 = useGetCalibrationImage({ query: { queryKey: getGetCalibrationImageQueryKey() } });
  const image90 = useGetCalibration90dImage({ query: { queryKey: getGetCalibration90dImageQueryKey() } });
  const summary = useGetReliabilitySummary({ query: { queryKey: getGetReliabilitySummaryQueryKey(), enabled: tab === 'calibration' || tab === 'methodology' } });
  const calibration = useGetReliabilityCalibration({ query: { queryKey: getGetReliabilityCalibrationQueryKey(), enabled: tab === 'calibration' } });
  const subgroupParams = useMemo(() => ({ horizon_days: subgroupHorizon }), [subgroupHorizon]);
  const subgroups = useGetReliabilitySubgroups(subgroupParams, { query: { queryKey: getGetReliabilitySubgroupsQueryKey(subgroupParams), enabled: tab === 'subgroups' } });
  const revenue = useGetReliabilityRevenue({ query: { queryKey: getGetReliabilityRevenueQueryKey(), enabled: tab === 'revenue' } });
  const url30 = image30.data?.url;
  const url90 = image90.data?.url;
  const data = q.data;
  const tabs = [
    ['overall', 'Overall'],
    ['calibration', 'Calibration & reliability'],
    ['subgroups', 'Customer subgroups'],
    ['revenue', 'Revenue error'],
    ['methodology', 'Methodology'],
  ] as const;
  return <div className="content">
    <PageHeading eyebrow="Notebook 06 / 07 / 09" title="Model performance" description="Inspect saved historical test results, reliability diagnostics, subgroup support, and the evaluation method." />
    <HistoricalNotice />
    <div className="research-tabs" role="tablist" aria-label="Model performance sections">
      {tabs.map(([key, label]) => <button type="button" role="tab" aria-selected={tab === key} className={`research-tab${tab === key ? ' active' : ''}`} key={key} onClick={() => setTab(key)} data-testid={`tab-performance-${key}`}>{label}</button>)}
    </div>
    {tab === 'overall' && <QueryState loading={q.isLoading} error={q.isError} empty={!data} retry={() => void q.refetch()}>
      {data && <>
        <div className="research-callout"><strong>Historical TEST evaluation</strong> · {number(data.test_customers)} customers · forecast cutoff {dateShort(data.cutoff_date)}. These are held-out aggregate results from a saved cutoff, not current-business predictions.</div>
        <div className="grid kpis"><Metric label="Test customers" value={number(data.test_customers)} foot={`Evaluation cutoff ${dateShort(data.cutoff_date)}`} icon={Users} /><Metric label="Purchase metric rows" value={number(data.purchase_metrics.length)} foot="Across saved models and horizons" icon={BarChart3} /><Metric label="Revenue metric rows" value={number(data.revenue_metrics.length)} foot="Saved evaluation outcomes" icon={Wallet} /><Metric label="Group evaluation rows" value={number(data.revenue_group_metrics.length)} foot="Revenue by saved cohort group" icon={Filter} /></div>
        <div className="grid equal">
          <Panel title="Purchase prediction metrics" note="Saved Notebook 06 evaluation"><MetricTable rows={data.purchase_metrics} columns={ [['model', 'Model'], ['horizon_days', 'Horizon'], ['brier_score', 'Brier score'], ['roc_auc', 'ROC AUC'], ['average_precision', 'Avg precision'], ['calibration_error', 'Calibration error'], ['log_loss', 'Log loss'], ['actual_purchase_rate', 'Actual rate']] } format={(key, value) => key.includes('rate') ? percent(Number(value)) : typeof value === 'number' ? key === 'horizon_days' ? `${value}d` : value.toFixed(3) : String(value)} /></Panel>
          <Panel title="Revenue forecast metrics" note="Saved Notebook 07 evaluation"><MetricTable rows={data.revenue_metrics} columns={ [['model', 'Model'], ['horizon_days', 'Horizon'], ['mae', 'MAE'], ['rmse', 'RMSE'], ['mean_forecast_bias', 'Mean bias'], ['total_revenue_bias', 'Total bias'], ['aggregate_calibration_ratio', 'Calibration ratio']] } format={(key, value) => key === 'horizon_days' ? `${value}d` : key.includes('ratio') ? Number(value).toFixed(3) : key === 'model' ? String(value) : money(Number(value))} /></Panel>
        </div>
        <div className="grid equal" style={{ marginTop: 16 }}>
          <Panel title="Purchase-history evaluation" note="Saved evaluation grouped by historical customer history"><MetricTable rows={data.purchase_history_metrics} columns={ [['history_group', 'History group'], ['horizon_days', 'Horizon'], ['n_customers', 'Customers'], ['actual_purchase_rate', 'Actual rate'], ['mean_predicted_probability', 'Mean predicted'], ['brier_score', 'Brier score'], ['roc_auc', 'ROC AUC']] } format={(key, value) => key === 'history_group' ? String(value) : key === 'horizon_days' ? `${value}d` : key === 'n_customers' ? number(Number(value)) : ['actual_purchase_rate', 'mean_predicted_probability'].includes(key) ? percent(Number(value)) : Number(value).toFixed(3)} /></Panel>
          <Panel title="Revenue by cohort group" note="Saved subgroup diagnostics"><MetricTable rows={data.revenue_group_metrics} columns={ [['group_type', 'Group type'], ['group', 'Group'], ['model', 'Model'], ['horizon_days', 'Horizon'], ['mae', 'MAE'], ['rmse', 'RMSE'], ['aggregate_calibration_ratio', 'Calibration ratio']] } format={(key, value) => key === 'horizon_days' ? `${value}d` : key === 'aggregate_calibration_ratio' ? Number(value).toFixed(3) : ['mae', 'rmse'].includes(key) ? money(Number(value)) : String(value)} /></Panel>
        </div>
        <div className="grid equal" style={{ marginTop: 16 }}>
          <Panel title="Purchase-clock calibration" note="Saved calibration evaluation image">{image30.isLoading ? <div className="skeleton" /> : image30.isError ? <div className="empty-box">Calibration image could not be loaded.</div> : url30 ? <img src={url30} alt="Saved purchase-clock calibration plot" style={{ display: 'block', width: '100%', borderRadius: 7 }} /> : <div className="empty-box">No calibration image available.</div>}</Panel>
          <Panel title="90-day calibration" note="Saved 90-day calibration evaluation image">{image90.isLoading ? <div className="skeleton" /> : image90.isError ? <div className="empty-box">Calibration image could not be loaded.</div> : url90 ? <img src={url90} alt="Saved 90-day calibration plot" style={{ display: 'block', width: '100%', borderRadius: 7 }} /> : <div className="empty-box">No calibration image available.</div>}</Panel>
        </div>
      </>}
    </QueryState>}
    {tab === 'calibration' && <div className="grid">
      <QueryState loading={summary.isLoading} error={summary.isError} empty={!summary.data} retry={() => void summary.refetch()}>
        {summary.data && <Panel title="Reliability scope" note={`Saved evaluation context · cutoff ${dateShort(calibration.data?.forecast_cutoff ?? String((summary.data.metadata as Record<string, unknown>).forecast_cutoff ?? ''))}`}>
          <div className="research-callout"><strong>{number(summary.data.test_customer_count)} TEST customers</strong> in the saved evaluation scope. Calibration describes aggregate historical behavior; it is not an individual guarantee or a reliability percentage.</div>
          <ReliabilityMetricTable rows={summary.data.purchase_calibration} />
          {summary.data.limitations.length > 0 && <ul className="research-list">{summary.data.limitations.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul>}
        </Panel>}
      </QueryState>
      <QueryState loading={calibration.isLoading} error={calibration.isError} empty={!calibration.data} retry={() => void calibration.refetch()}>
        {calibration.data && <Panel title="Calibration bins by horizon" note={`Forecast cutoff ${dateShort(calibration.data.forecast_cutoff)} · each bin shows predicted and observed averages with its count`}>
          {calibration.data.horizons.length ? <div className="grid">{calibration.data.horizons.map((metric) => {
            const bins = metric.calibration_bins as Record<string, unknown>[];
            return <section className="research-bin-panel" key={metric.horizon_days}>
              <div className="research-subhead">{metric.horizon_days}-day horizon · n={number(metric.customer_count)} · Brier {number(metric.brier_score)} · ECE {number(metric.expected_calibration_error)} · MCE {number(metric.maximum_calibration_error)}</div>
              <CalibrationBins bins={bins} />
            </section>;
          })}</div> : <div className="empty-box">No calibration horizon results were returned.</div>}
        </Panel>}
      </QueryState>
    </div>}
    {tab === 'subgroups' && <Panel title="Customer subgroup reliability" note="Supported cohorts only; rows suppressed or omitted by the API are not inferred.">
      <div className="filter-row"><div className="field" style={{ maxWidth: 220 }}><label className="field-label" htmlFor="subgroup-horizon">Forecast horizon</label><select id="subgroup-horizon" className="select" value={subgroupHorizon} onChange={(event) => setSubgroupHorizon(Number(event.target.value) as 30 | 60 | 90)} data-testid="select-subgroup-horizon"><option value={30}>30 days</option><option value={60}>60 days</option><option value={90}>90 days</option></select></div><span className="tiny">Cutoff {dateShort(subgroups.data?.forecast_cutoff)} · minimum supported group size {subgroups.data ? number(subgroups.data.minimum_group_support) : '—'}</span></div>
      <QueryState loading={subgroups.isLoading} error={subgroups.isError} empty={!subgroups.data} retry={() => void subgroups.refetch()}>
        {subgroups.data && (subgroups.data.items.length ? <div className="table-scroll"><table><thead><tr><th>Group type</th><th>Group</th><th>Horizon</th><th>Customers</th><th>Mean predicted</th><th>Observed rate</th><th>Brier</th><th>Calibration gap</th><th>Evaluation status</th><th>Bootstrap intervals</th></tr></thead><tbody>{subgroups.data.items.map((row, index) => <tr key={`${row.group_type}-${row.group}-${index}`}><td>{row.group_type}</td><td>{row.group}</td><td>{row.horizon_days}d</td><td className="number">{number(row.customer_count)}</td><td className="number">{percent(row.mean_predicted_probability)}</td><td className="number">{percent(row.observed_purchase_rate)}</td><td className="number">{number(row.brier_score)}</td><td className="number">{number(row.calibration_gap)}</td><td>{row.status}{row.status_reason ? ` · ${row.status_reason}` : ''}</td><td>{displayValue(row.bootstrap_intervals)}</td></tr>)}</tbody></table></div> : <div className="empty-box">No supported subgroup rows were returned for this horizon. Group support can be absent; no estimate is substituted.</div>)}
      </QueryState>
      <p className="tiny">Counts and scores describe historical evaluation subgroups, not customer-specific outcomes, guaranteed performance, or current operating populations.</p>
    </Panel>}
    {tab === 'revenue' && <QueryState loading={revenue.isLoading} error={revenue.isError} empty={!revenue.data} retry={() => void revenue.refetch()}>
      {revenue.data && <div className="grid">
        <div className="research-callout"><strong>Aggregate TEST revenue evaluation</strong> · cutoff {dateShort(revenue.data.forecast_cutoff)}. Metrics are computed across the held-out test cohort; they do not reveal any customer's TEST outcome.</div>
        <Panel title="Aggregate revenue error metrics" note="Values are shown as returned by the saved evaluation API"><DynamicRecordTable rows={revenue.data.metrics} /></Panel>
        <Panel title="Revenue error by purchase-history group" note="Subgroup aggregates only"><DynamicRecordTable rows={revenue.data.history_groups} /></Panel>
        <Panel title="Large-spender sensitivity" note="Sensitivity analysis for aggregate error under the saved large-spender definitions"><DynamicRecordTable rows={revenue.data.large_spender_sensitivity} /></Panel>
      </div>}
    </QueryState>}
    {tab === 'methodology' && <QueryState loading={summary.isLoading} error={summary.isError} empty={!summary.data} retry={() => void summary.refetch()}>
      {summary.data && <div className="grid two">
        <Panel title="Evaluation boundary" note="How to read this research workspace">
          <ul className="research-list"><li>Saved forecasts are evaluated against a historical held-out TEST set at the recorded forecast cutoff.</li><li>TEST outcomes are used only for aggregate evaluation summaries. No customer-level TEST outcome is exposed in the explanation or reliability views.</li><li>Reliability diagnostics are group-level summaries and do not promise a probability will materialize for any person.</li><li>Customer explanations compare saved inputs and reference substitutions; these are noncausal model-input sensitivities.</li></ul>
          <div className="research-callout">Evaluation sample: {number(summary.data.test_customer_count)} TEST customers. Forecast cutoff: {dateShort(String((summary.data.metadata as Record<string, unknown>).forecast_cutoff ?? ''))}.</div>
        </Panel>
        <Panel title="Uncertainty definitions" note="Definitions supplied with the saved reliability response">{Object.keys(summary.data.uncertainty_definitions).length ? <KeyValueTable values={summary.data.uncertainty_definitions} /> : <div className="empty-box">No uncertainty definitions were supplied.</div>}</Panel>
        <Panel title="Saved evaluation scope" note="Response metadata"><KeyValueTable values={summary.data.metadata} /></Panel>
        <Panel title="Known limitations" note="Returned with the reliability summary">{summary.data.limitations.length ? <ul className="research-list">{summary.data.limitations.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul> : <div className="empty-box">No additional limitation text was returned.</div>}</Panel>
      </div>}
    </QueryState>}
  </div>;
}
