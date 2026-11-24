import { useMemo, useState } from 'react';
import { AlertTriangle, BookOpen, CheckCircle2, ExternalLink, FileText, History, Search } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useGetResearchSummary } from '@workspace/api-client-react';
import type { FinalResearchSummary } from '@workspace/api-client-react';
import type { ReactNode } from 'react';

const REPOSITORY = 'https://github.com/Punit-IITPKD/OELP_project';
const RESEARCH_BRANCH = 'feat/phase7-final-research-integration';
const METHODS_DOCUMENTS: Record<string, string> = {
  '01': 'docs/INFERENCE_PIPELINE.md',
  '02': 'docs/INFERENCE_PIPELINE.md',
  '03': 'docs/INFERENCE_PIPELINE.md',
  '04': 'docs/INFERENCE_PIPELINE.md',
  '05': 'docs/INFERENCE_PIPELINE.md',
  '06': 'docs/INFERENCE_PIPELINE.md',
  '07': 'docs/INFERENCE_PIPELINE.md',
  '08': 'docs/BEHAVIOR_MONITORING.md',
  '09': 'docs/PREDICTION_RELIABILITY_AND_EXPLAINABILITY.md',
  '10': 'docs/REVENUE_EXPOSURE_AND_RETENTION_PLANNING.md',
  '11': 'docs/CUSTOMER_TRAJECTORY_ANALYSIS.md',
};

type Row = Record<string, unknown>;

function asRecord(value: unknown): Row {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Row : {};
}

function asRows(value: unknown): Row[] {
  return Array.isArray(value) ? value.filter((row): row is Row => !!row && typeof row === 'object' && !Array.isArray(row)) : [];
}

function text(value: unknown, fallback = '—'): string {
  return typeof value === 'string' && value.trim() ? value : fallback;
}

function number(value: unknown, digits = 1): string {
  return typeof value === 'number' && Number.isFinite(value)
    ? new Intl.NumberFormat('en-GB', { maximumFractionDigits: digits }).format(value)
    : '—';
}

function percentage(value: unknown, digits = 1): string {
  return typeof value === 'number' && Number.isFinite(value)
    ? `${(value * 100).toFixed(digits)}%`
    : '—';
}

function pounds(value: unknown): string {
  return typeof value === 'number' && Number.isFinite(value)
    ? new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(value)
    : '—';
}

function sourceUrl(path: string): string {
  return `${REPOSITORY}/blob/${RESEARCH_BRANCH}/${path}`;
}

function EvidenceBadge({ status }: { status: string }) {
  const label = status.replaceAll('_', ' ');
  return <span className={`research-status research-status-${status}`}>{label}</span>;
}

function DataTable({ caption, headers, rows }: { caption: string; headers: string[]; rows: ReactNode[] }) {
  return <div className="research-table-scroll"><table className="research-table">
    <caption>{caption}</caption>
    <thead><tr>{headers.map((header) => <th scope="col" key={header}>{header}</th>)}</tr></thead>
    <tbody>{rows}</tbody>
  </table></div>;
}

function Section({ id, title, description, children }: { id: string; title: string; description?: string; children: ReactNode }) {
  return <section className="research-section" id={id}>
    <div className="research-section-heading"><div><h2>{title}</h2>{description && <p>{description}</p>}</div></div>
    {children}
  </section>;
}

function MetricCard({ label, value, note, icon: Icon }: { label: string; value: string; note: string; icon: LucideIcon }) {
  return <div className="panel research-metric">
    <div className="research-metric-top"><span>{label}</span><Icon size={17} aria-hidden="true" /></div>
    <strong>{value}</strong>
    <small>{note}</small>
  </div>;
}

function LoadingState() {
  return <div className="content" role="status" aria-live="polite" aria-label="Loading research summary">
    <div className="page-heading"><div><div className="eyebrow">FINAL RESEARCH SYNTHESIS</div><h1>Research overview</h1><p>Loading the checked-in notebook evaluation summary.</p></div></div>
    <div className="grid"><div className="skeleton" /><div className="skeleton" /></div>
  </div>;
}

function ErrorState({ retry }: { retry: () => void }) {
  return <div className="content">
    <div className="error-box" role="alert">
      The research summary could not be loaded. Confirm the generated evaluation is current, then try again.
      <button className="button secondary" onClick={retry} style={{ marginLeft: 10 }}>Retry</button>
    </div>
  </div>;
}

export default function ResearchPage() {
  const query = useGetResearchSummary();
  const [hypothesisFilter, setHypothesisFilter] = useState('all');
  const [moduleSearch, setModuleSearch] = useState('');
  const data = query.data as FinalResearchSummary | undefined;
  const hypotheses = data?.research_hypotheses ?? [];
  const visibleHypotheses = useMemo(
    () => hypotheses.filter((item) => hypothesisFilter === 'all' || item.evidence_status === hypothesisFilter),
    [hypotheses, hypothesisFilter],
  );
  const modules = useMemo(
    () => (data?.notebook_registry ?? []).filter((item) =>
      `${item.notebook_id} ${item.title} ${item.objective}`.toLowerCase().includes(moduleSearch.toLowerCase()),
    ),
    [data?.notebook_registry, moduleSearch],
  );

  if (query.isLoading) return <LoadingState />;
  if (query.isError || !data) return <ErrorState retry={() => void query.refetch()} />;

  const scope = asRecord(data.research_scope);
  const coverage = asRecord(data.coverage_summary);
  const purchase = asRecord(data.purchase_clock_evaluation);
  const spending = asRecord(data.spending_forecast_evaluation);
  const behavior = asRecord(data.behavior_evaluation);
  const reliability = asRecord(data.reliability_evaluation);
  const revenue = asRecord(data.revenue_exposure_evaluation);
  const trajectory = asRecord(data.trajectory_evaluation);
  const trajectoryScope = asRecord(coverage.trajectory);
  const clusterEligibility = asRecord(coverage.trajectory_method_eligibility);
  const functional = asRecord(trajectory.functional_analysis);
  const functionalTest = asRecord(functional.test_evaluation);
  const trajectoryQuestion = asRecord(asRecord(data.additional_research_questions).incremental_predictive_value);
  const definitions = asRecord(data.financial_definitions);
  const sourceManifest = data.source_manifest ?? [];
  const purchaseMetrics = asRows(purchase.test_metrics);
  const spendingMetrics = asRows(spending.test_metrics);
  const calibrationMetrics = asRows(reliability.purchase_calibration);
  const hypothesisCounts = data.hypothesis_status_counts ?? {};
  const moduleCount = data.notebook_registry.length;
  const horizonCount = Array.isArray(scope.forecast_horizons_days) ? scope.forecast_horizons_days.length : 0;
  const testCount = number(scope.test_customer_count, 0);
  const observedStart = text(scope.observed_start).slice(0, 10);
  const observedEnd = text(scope.observed_end).slice(0, 10);
  const officialCutoff = text(scope.official_test_cutoff);
  const evidenceStatusOptions = [...new Set(hypotheses.map((item) => item.evidence_status))].sort();

  return <div className="content research-page">
    <div className="page-heading">
      <div>
        <div className="eyebrow">FINAL RESEARCH SYNTHESIS</div>
        <h1>Research overview</h1>
        <p>One evidence-linked view of the project’s 11 notebooks, their saved evaluations, cohort coverage, and limits.</p>
      </div>
      <a className="button secondary research-source-button" href={sourceUrl('docs/FINAL_RESEARCH_EVALUATION.md')} target="_blank" rel="noreferrer">
        <FileText size={15} /> Final evaluation
      </a>
    </div>

    <div className="historical-banner" role="note">
      <History size={15} aria-hidden="true" />
      <span><strong>Historical research only.</strong> The evidence is from {text(scope.dataset)} ({observedStart}–{observedEnd}), evaluated at the {officialCutoff} cutoff. It is not a live forecast, churn label, or treatment-effect estimate.</span>
    </div>

    <div className="research-metric-grid">
      <MetricCard label="Research notebooks" value={number(moduleCount, 0)} note="Methods, findings, and sources linked below" icon={BookOpen} />
      <MetricCard label="Locked TEST cohort" value={testCount} note={`Customers at the ${officialCutoff} cutoff`} icon={CheckCircle2} />
      <MetricCard label="Saved forecast horizons" value={number(horizonCount, 0)} note={`${Array.isArray(scope.forecast_horizons_days) ? scope.forecast_horizons_days.join(' / ') : ''} days`} icon={History} />
      <MetricCard label="Evidence source files" value={number(sourceManifest.length, 0)} note="SHA-256 manifest included in the response" icon={FileText} />
    </div>

    <Section id="cohort-coverage" title="Cohort and method coverage" description="Eligibility varies by method; these counts share the historical TEST cohort as a reference and are not interchangeable populations.">
      <div className="research-coverage-grid">
        <div className="research-coverage-card"><span>Common TEST cohort</span><strong>{number(trajectoryScope.official_test_customers, 0)}</strong><small>Denominator at the official cutoff</small></div>
        <div className="research-coverage-card"><span>Summary trajectory support</span><strong>{number(coverage.trajectory_summary_eligible_test, 0)}</strong><small>At least the saved trajectory summary requirements</small></div>
        <div className="research-coverage-card"><span>Shape-cluster eligible</span><strong>{number(clusterEligibility.TEST, 0)}</strong><small>All required curve windows and history support</small></div>
        <div className="research-coverage-card"><span>Functional curves evaluated</span><strong>{number(functionalTest.evaluated_curves, 0)}</strong><small>TRAIN-fitted representation; evaluated once on TEST</small></div>
      </div>
      <p className="research-footnote">Behavior indicators, reliability subgroups, and revenue screens apply their own history and support rules. See each notebook’s coverage fields and methods document before comparing counts.</p>
    </Section>

    <Section id="hypotheses" title="Research hypotheses and evidence" description="Statuses preserve the original saved evaluation labels, grouped into evidence categories without treating descriptive results as causal.">
      <div className="research-evidence-toolbar">
        <div className="research-status-counts" aria-label="Hypothesis counts by evidence status">
          {Object.entries(hypothesisCounts).map(([status, count]) => <div className="research-count-chip" key={status}><EvidenceBadge status={status} /><strong>{number(count, 0)}</strong></div>)}
        </div>
        <label className="field research-filter"><span>Filter evidence</span>
          <select value={hypothesisFilter} onChange={(event) => setHypothesisFilter(event.target.value)}>
            <option value="all">All statuses</option>
            {evidenceStatusOptions.map((status) => <option value={status} key={status}>{status.replaceAll('_', ' ')}</option>)}
          </select>
        </label>
      </div>
      <div className="research-hypothesis-list">
        {visibleHypotheses.map((item) => <article className="research-hypothesis" key={item.id}>
          <div className="research-hypothesis-meta"><span>Notebook {item.notebook_id} · {item.id}</span><EvidenceBadge status={item.evidence_status} /></div>
          <h3>{item.statement}</h3>
          <p>{item.evidence_summary}</p>
          <div className="research-hypothesis-details">
            <div><strong>Reference baseline</strong><span>{item.reference_baseline ?? 'Not recorded in the saved summary'}</span></div>
            <div><strong>Primary metric</strong><span>{item.primary_metric.replaceAll('_', ' ')}</span></div>
            <div><strong>Evaluation support</strong><span>{item.evaluation_horizons_days.length ? item.evaluation_horizons_days.map((horizon) => `${horizon}d`).join(' · ') : 'Not horizon-based'} · n={number(item.cohort_size, 0)}</span></div>
            <div><strong>Selection protocol</strong><span>{item.selection_protocol}</span></div>
            <div><strong>TEST protocol</strong><span>{item.test_protocol}</span></div>
          </div>
          {item.uncertainty_intervals.length > 0 && <div className="research-interval-list"><strong>Saved 95% intervals</strong>{item.uncertainty_intervals.map((interval, index) => {
            const result = asRecord(interval);
            return <span key={`${String(result.horizon_days)}-${index}`}>{number(result.horizon_days, 0)}d: {number(result.estimate, 4)} [{number(result.lower, 4)}, {number(result.upper, 4)}]</span>;
          })}</div>}
          <small>Saved label: <code>{item.raw_status ?? 'not recorded'}</code> · Source field: <code>{item.source_field}</code></small>
        </article>)}
        {!visibleHypotheses.length && <div className="empty-box">No hypotheses match this evidence status.</div>}
      </div>
      <div className="research-callout"><AlertTriangle size={17} aria-hidden="true" /><div><strong>Trajectory incremental-prediction question: {text(trajectoryQuestion.evidence_status, 'not recorded').replaceAll('_', ' ')}.</strong><span>{text(trajectoryQuestion.interpretation)}</span></div></div>
    </Section>

    <Section id="purchase-clock" title="Purchase Clock evaluation" description="Saved-model TEST comparisons from the original evaluation artifact. These values are shown as recorded; this dashboard does not recompute or adjust predictions.">
      <DataTable caption="Purchase probability metrics by horizon and model" headers={['Horizon', 'Model', 'Customers', 'Observed rate', 'Mean predicted', 'Brier', 'ROC AUC', 'Average precision', 'Calibration error']} rows={purchaseMetrics.map((row, index) =>
        <tr key={`${String(row.horizon_days)}-${String(row.model)}-${index}`}>
          <td>{number(row.horizon_days, 0)} days</td><td>{text(row.model)}</td><td>{number(row.n_customers, 0)}</td>
          <td>{percentage(row.actual_purchase_rate)}</td><td>{percentage(row.mean_predicted_probability)}</td>
          <td>{number(row.brier_score, 4)}</td><td>{number(row.roc_auc, 3)}</td>
          <td>{number(row.average_precision, 3)}</td><td>{number(row.calibration_error, 4)}</td>
        </tr>,
      )} />
    </Section>

    <Section id="spending" title="Spending forecast evaluation" description="Expected gross-revenue forecasts are two-stage estimates; model disagreement is not a counterfactual or revenue loss.">
      <DataTable caption="TEST revenue forecast diagnostics" headers={['Horizon', 'Model', 'Customers', 'MAE', 'RMSE', 'Mean bias', 'Portfolio bias', 'Calibration ratio']} rows={spendingMetrics.map((row, index) =>
        <tr key={`${String(row.horizon_days)}-${String(row.model)}-${index}`}>
          <td>{number(row.horizon_days, 0)} days</td><td>{text(row.model)}</td><td>{number(row.n_customers, 0)}</td>
          <td>{pounds(row.mae)}</td><td>{pounds(row.rmse)}</td><td>{pounds(row.mean_forecast_bias)}</td>
          <td>{pounds(row.total_revenue_bias)}</td><td>{number(row.aggregate_calibration_ratio, 3)}</td>
        </tr>,
      )} />
    </Section>

    <Section id="reliability" title="Prediction reliability" description="Reliability intervals describe empirical group metrics, not confidence for an individual customer.">
      <div className="research-horizon-grid">
        {calibrationMetrics.map((row) => <article className="panel research-horizon-card" key={String(row.horizon_days)}>
          <div className="eyebrow">{number(row.horizon_days, 0)}-DAY HORIZON</div>
          <strong>{number(row.n_customers, 0)} customers</strong>
          <dl><div><dt>Brier score</dt><dd>{number(row.brier_score, 4)}</dd></div><div><dt>Average precision</dt><dd>{number(row.average_precision, 3)}</dd></div><div><dt>Calibration error</dt><dd>{number(row.expected_calibration_error, 4)}</dd></div></dl>
        </article>)}
      </div>
    </Section>

    <Section id="behavior" title="Behavior monitoring" description="Notebook 08 reports continuous indicators, not churn labels or an operational alert policy.">
      <div className="research-callout research-callout-neutral"><Search size={17} aria-hidden="true" /><div><strong>{text(behavior.policy_status, 'No policy status recorded').replaceAll('_', ' ')}</strong><span>{text(behavior.candidate_f_status)}</span></div></div>
      <p className="research-footnote">The saved evidence includes bootstrap comparisons and subgroup results. The conditional Purchase Clock comparison remains unresolved because a chronologically eligible training vintage was unavailable.</p>
    </Section>

    <Section id="revenue-exposure" title="Revenue exposure and planning" description="Financial quantities are kept distinct so a screening proxy is not mistaken for money that can be recovered.">
      <div className="research-financial-banner">
        <div><span>Reference-based exposure</span><strong>{text(definitions.reference_exposure_status, 'not reported').replaceAll('_', ' ')}</strong></div>
        <p>{text(definitions.reference_exposure_reason)}</p>
      </div>
      <div className="research-definition-grid">
        <div><strong>Expected revenue</strong><p>{text(definitions.expected_revenue)}</p></div>
        <div><strong>Nonreturn-spending proxy</strong><p>{text(definitions.opportunity_proxy)}</p></div>
        <div><strong>Campaign scenarios</strong><p>{text(asRecord(revenue.scenario_sensitivity).interpretation, 'Inputs are hypothetical; no treatment effect is estimated.')}</p></div>
      </div>
    </Section>

    <Section id="trajectories" title="Trajectory and functional analysis" description="Selected representations use TRAIN/VAL evidence and are evaluated on the held-out cohort; method-specific eligibility is shown above.">
      <div className="research-trajectory-grid">
        <div className="panel"><div className="eyebrow">CLUSTERING</div><strong>{text(asRecord(trajectory.cluster_selection).status).replaceAll('_', ' ')}</strong><p>{text(asRecord(trajectory.cluster_selection).selection_rule)}</p></div>
        <div className="panel"><div className="eyebrow">FUNCTIONAL REPRESENTATION</div><strong>{text(functional.status).replaceAll('_', ' ')}</strong><p>{text(functional.method).replaceAll('_', ' ')}</p></div>
        <div className="panel"><div className="eyebrow">INCREMENTAL PREDICTION</div><strong>Inconclusive</strong><p>{text(trajectoryQuestion.interpretation)}</p></div>
      </div>
      <p className="research-footnote">Cluster labels are descriptive, not risk ranks. The trajectory-only comparison does not establish conditional incremental value over the saved Purchase Clock.</p>
    </Section>

    <Section id="notebooks" title="Notebook contribution register" description="Each entry includes its objective, method, evaluation scope, evidence sources, and known limitations.">
      <label className="field research-module-search"><span>Find a notebook</span><input value={moduleSearch} onChange={(event) => setModuleSearch(event.target.value)} placeholder="Search methods or findings" /></label>
      <div className="research-module-grid">
        {modules.map((item) => {
          const notebookPath = item.source_artifacts.find((path) => path.startsWith('notebooks/'));
          const methodPath = METHODS_DOCUMENTS[item.notebook_id];
          return <article className="panel research-module-card" key={item.notebook_id}>
            <div className="research-module-top"><span>NOTEBOOK {item.notebook_id}</span><span>{item.source_version}</span></div>
            <h3>{item.title}</h3>
            <p>{item.objective}</p>
            <dl><div><dt>Method</dt><dd>{item.method}</dd></div>
              <div><dt>Dataset</dt><dd>{item.dataset}</dd></div>
              <div><dt>Horizon coverage</dt><dd>{item.evaluation_horizons_days.length ? item.evaluation_horizons_days.map((horizon) => `${horizon}d`).join(' · ') : 'Descriptive / not horizon-based'}</dd></div>
              <div><dt>Evaluation population</dt><dd>{item.evaluation_population}</dd></div>
              <div><dt>Source version</dt><dd>{item.source_version}</dd></div>
            </dl>
            <div className="research-major-findings"><strong>Validated findings</strong><ul>{item.major_findings.map((finding) => <li key={finding}>{finding}</li>)}</ul></div>
            <ul>{item.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul>
            <div className="research-module-links">
              {notebookPath && <a href={sourceUrl(notebookPath)} target="_blank" rel="noreferrer">Notebook source <ExternalLink size={13} /></a>}
              {methodPath && <a href={sourceUrl(methodPath)} target="_blank" rel="noreferrer">Methods <ExternalLink size={13} /></a>}
            </div>
            <details className="research-reproduction">
              <summary>Reproduction command</summary>
              <pre><code>{item.reproducibility_command}</code></pre>
              <small>This command re-executes research code and may rewrite its notebook outputs. Run it only in a disposable working copy.</small>
            </details>
          </article>;
        })}
        {!modules.length && <div className="empty-box">No notebooks match this search.</div>}
      </div>
    </Section>

    <Section id="provenance" title="Evidence provenance" description="The final summary includes source hashes so its conclusions can be traced to the checked-in evaluations and model metadata.">
      <div className="research-table-scroll"><table className="research-table">
        <caption>Source artifact checksums</caption>
        <thead><tr><th scope="col">Source file</th><th scope="col">SHA-256</th></tr></thead>
        <tbody>{sourceManifest.map((source) => <tr key={source.path}><td><a href={sourceUrl(source.path)} target="_blank" rel="noreferrer" className="research-file-link">{source.path}</a></td><td><code>{source.sha256.slice(0, 16)}…</code></td></tr>)}</tbody>
      </table></div>
    </Section>

    <Section id="limitations" title="How to interpret this dashboard" description="The summaries preserve the original research scope; they do not broaden the conclusions.">
      <ul className="research-limitations">{data.limitations.map((limitation) => <li key={limitation}>{limitation}</li>)}</ul>
      <div className="research-methodology-links">
        <a href={sourceUrl('docs/FINAL_RESEARCH_EVALUATION.md')} target="_blank" rel="noreferrer">Final research evaluation <ExternalLink size={14} /></a>
        <a href={sourceUrl('docs/FINAL_REPRODUCIBILITY_GUIDE.md')} target="_blank" rel="noreferrer">Reproducibility guide <ExternalLink size={14} /></a>
      </div>
    </Section>
  </div>;
}
