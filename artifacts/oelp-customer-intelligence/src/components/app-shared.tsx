import { AlertCircle, History } from 'lucide-react';
import type { ElementType, ReactNode } from 'react';
import { dateShort, money, number, percent } from '../app-format';

export function HistoricalNotice() {
  return <div className="historical-banner" data-testid="notice-historical-demonstration">
    <History size={15} />
    <span><strong>Historical demonstration only.</strong> Forecasts below reproduce saved-model outputs at the recorded historical cutoff. They are not current-business predictions, live forecasts, or recommendations.</span>
  </div>;
}

export function PageHeading({ eyebrow, title, description, action }: {
  eyebrow: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return <div className="page-heading">
    <div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>
    {action}
  </div>;
}

export function Panel({ title, note, children, extra }: {
  title: string;
  note?: string;
  children: ReactNode;
  extra?: ReactNode;
}) {
  return <section className="panel">
    <div className="panel-head"><div><div className="panel-title">{title}</div>{note && <div className="panel-note">{note}</div>}</div>{extra}</div>
    {children}
  </section>;
}

export function Loading({ rows = 2 }: { rows?: number }) {
  return <div className="grid" role="status" aria-live="polite" aria-label="Loading page data">{Array.from({ length: rows }, (_, index) => <div key={index} className="skeleton" />)}</div>;
}

export function QueryState({ loading, error, empty, retry, children }: {
  loading: boolean;
  error: boolean;
  empty?: boolean;
  retry: () => void;
  children: ReactNode;
}) {
  if (loading) return <Loading />;
  if (error) return <div className="error-box" role="alert">
    <AlertCircle size={17} style={{ verticalAlign: 'middle', marginRight: 7 }} />
    Data could not be loaded.
    <button className="button secondary" onClick={retry} style={{ marginLeft: 9 }}>Try again</button>
  </div>;
  if (empty) return <div className="empty-box">No saved historical data is available for this view.</div>;
  return <>{children}</>;
}

export function Metric({ label, value, foot, icon: Icon }: {
  label: string;
  value: string;
  foot: string;
  icon: ElementType;
}) {
  return <div className="panel">
    <div className="metric-label"><span>{label}</span><Icon size={16} color="#83978b" /></div>
    <div className="metric-value number">{value}</div><div className="metric-accent" /><div className="metric-foot">{foot}</div>
  </div>;
}

export function displayValue(value: unknown): string {
  if (value == null) return '—';
  if (typeof value === 'number') return Number.isFinite(value) ? number(value) : '—';
  if (typeof value === 'string' || typeof value === 'boolean') return String(value);
  return JSON.stringify(value);
}

export function KeyValueTable({ values, valueFormat }: {
  values: Record<string, unknown>;
  valueFormat?: (value: unknown, key: string) => string;
}) {
  const entries = Object.entries(values);
  if (!entries.length) return <div className="empty-box">No values were returned.</div>;
  return <div className="research-key-values">{entries.map(([key, value]) => <div key={key}>
    <span>{key.replaceAll('_', ' ')}</span><strong>{valueFormat ? valueFormat(value, key) : displayValue(value)}</strong>
  </div>)}</div>;
}

export function ReliabilityMetricTable({ rows }: { rows: Array<{
  horizon_days: number;
  model: string;
  forecast_cutoff: string;
  customer_count: number;
  brier_score: number;
  log_loss: number;
  roc_auc: number | null;
  average_precision: number | null;
  average_precision_reason: string | null;
  expected_calibration_error: number | null;
  maximum_calibration_error: number | null;
  mean_predicted_probability: number;
  observed_purchase_rate: number;
  signed_calibration_gap: number;
  calibration_note: string;
  test_outcomes_used_for_method_selection: boolean;
}> }) {
  if (!rows.length) return <div className="empty-box">No saved reliability metrics.</div>;
  return <div className="table-scroll"><table><thead><tr>
    <th>Model</th><th>Horizon</th><th>Forecast cutoff</th><th>Customers</th><th>Brier</th><th>Log loss</th>
    <th>ROC AUC</th><th>Avg precision</th><th>ECE</th><th>MCE</th><th>Mean predicted</th><th>Observed rate</th><th>Calibration gap</th>
  </tr></thead><tbody>{rows.map((row, index) => <tr key={`${row.model}-${row.horizon_days}-${index}`}>
    <td>{row.model}</td><td>{row.horizon_days}d</td><td>{dateShort(row.forecast_cutoff)}</td><td className="number">{number(row.customer_count)}</td>
    <td className="number">{number(row.brier_score)}</td><td className="number">{number(row.log_loss)}</td><td className="number">{number(row.roc_auc)}</td>
    <td className="number" title={row.average_precision_reason ?? undefined}>{number(row.average_precision)}</td>
    <td className="number">{number(row.expected_calibration_error)}</td><td className="number">{number(row.maximum_calibration_error)}</td>
    <td className="number">{percent(row.mean_predicted_probability)}</td><td className="number">{percent(row.observed_purchase_rate)}</td><td className="number">{number(row.signed_calibration_gap)}</td>
  </tr>)}</tbody></table>
    <p className="tiny">{rows[0]?.calibration_note} · TEST outcomes used for method selection: {rows.some((row) => row.test_outcomes_used_for_method_selection) ? 'yes' : 'no'}</p>
  </div>;
}

export function CalibrationBins({ bins }: { bins: Record<string, unknown>[] }) {
  if (!bins.length) return <div className="empty-box">No calibration bins were returned for this horizon.</div>;
  return <DynamicRecordTable rows={bins} />;
}

export function DynamicRecordTable({ rows }: { rows: Record<string, unknown>[] }) {
  if (!rows.length) return <div className="empty-box">No saved rows were returned.</div>;
  const columns = Array.from(new Set(rows.flatMap((row) => Object.keys(row))));
  return <div className="table-scroll"><table><thead><tr>{columns.map((column) => <th key={column}>{column.replaceAll('_', ' ')}</th>)}</tr></thead>
    <tbody>{rows.map((row, index) => <tr key={index}>{columns.map((column) =>
      <td className={typeof row[column] === 'number' ? 'number' : ''} key={column}>{displayValue(row[column])}</td>,
    )}</tr>)}</tbody>
  </table></div>;
}

export function MetricTable({ rows, columns, format }: {
  rows: object[];
  columns: [string, string][];
  format: (key: string, value: unknown) => string;
}) {
  if (!rows.length) return <div className="empty-box">No saved evaluation rows.</div>;
  return <div className="table-scroll"><table><thead><tr>{columns.map(([, label]) => <th key={label}>{label}</th>)}</tr></thead>
    <tbody>{rows.map((item, index) => {
      const row = item as Record<string, unknown>;
      return <tr key={`${String(row.model ?? row.group ?? 'row')}-${index}`}>
        {columns.map(([key]) => <td className={typeof row[key] === 'number' ? 'number' : ''} key={key}>{format(key, row[key])}</td>)}
      </tr>;
    })}</tbody>
  </table></div>;
}

export { money, number, percent, dateShort };
