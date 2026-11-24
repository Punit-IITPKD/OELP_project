import { useState } from 'react';
import {
  ArrowDownToLine, Database, FileSpreadsheet, Filter, LoaderCircle, ShieldCheck, UploadCloud, Users, Wallet,
} from 'lucide-react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import { useAnalyzeUpload, useExportUpload, usePreviewUpload } from '@workspace/api-client-react';
import type { UploadAnalysis, UploadPreview } from '@workspace/api-client-react';
import { HistoricalNotice, Metric, PageHeading, Panel, QueryState, dateShort, money, number } from '../components/app-shared';

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

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<UploadPreview | null>(null);
  const [analysis, setAnalysis] = useState<UploadAnalysis | null>(null);
  const [mapping, setMapping] = useState<Record<string, string>>({});
  const previewMutation = usePreviewUpload({ mutation: { onSuccess: (data) => {
    setPreview(data);
    setAnalysis(null);
    const normalized: Record<string, string> = {};
    mappingFields.forEach((field) => {
      const match = data.columns.find((column) => field.candidates.includes(column.toLowerCase().replace(/[^a-z0-9]/g, '')));
      if (match) normalized[field.key] = match;
    });
    setMapping(normalized);
  } } });
  const analyzeMutation = useAnalyzeUpload({ mutation: { onSuccess: setAnalysis } });
  const exportMutation = useExportUpload();
  const [exportError, setExportError] = useState('');
  const uploadFile = (selected: File | null) => {
    if (!selected) return;
    setFile(selected);
    setPreview(null);
    setAnalysis(null);
    setMapping({});
    previewMutation.mutate({ data: { file: selected } });
  };
  const runAnalysis = () => {
    if (!file) return;
    analyzeMutation.mutate({ data: { file, mapping: JSON.stringify(mapping) } });
  };
  const download = (kind: 'cleaned_transactions' | 'customer_features') => {
    if (!file) return;
    setExportError('');
    exportMutation.mutate({ data: { file, mapping: JSON.stringify(mapping), kind } }, {
      onSuccess: (csv) => {
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `${kind}.csv`;
        anchor.click();
        URL.revokeObjectURL(url);
      },
      onError: () => setExportError('The export could not be prepared. Try again.'),
    });
  };
  const requiredMapped = mappingFields.filter((field) => field.required).every((field) => mapping[field.key]);
  const result = analysis;
  return <div className="content">
    <PageHeading eyebrow="Descriptive only · nothing saved" title="Upload analysis" description="Preview a CSV or XLSX, map transaction columns, inspect descriptive validation and download reprocessed CSVs. Uploads are not persisted." />
    <div className="historical-banner"><ShieldCheck size={15} /><span><strong>Private, in-memory workflow.</strong> This tool does not create forecasts or save uploaded records. The analysis is descriptive validation only.</span></div>
    <div className="grid two">
      <Panel title="Choose a transaction file" note="Supported formats are CSV and XLSX">
        <label className="upload-drop" htmlFor="upload-file" style={{ display: 'block', cursor: 'pointer' }}><UploadCloud size={25} /><div style={{ fontWeight: 700, color: '#38574b', fontSize: 12 }}>{file ? file.name : 'Select a CSV or XLSX file'}</div><div className="tiny" style={{ marginTop: 5 }}>{file ? 'Choose another file to replace this preview' : 'Your data stays in the current analysis session'}</div><input id="upload-file" type="file" accept=".csv,.xlsx" style={{ display: 'none' }} onChange={(event) => uploadFile(event.target.files?.[0] ?? null)} data-testid="input-upload-file" /></label>
        {previewMutation.isPending && <div style={{ marginTop: 14 }}><div className="skeleton" /></div>}
        {previewMutation.isError && <div className="error-box" style={{ marginTop: 12 }}>Preview failed. Check that the file is CSV or XLSX, then select it again.</div>}
        {preview && <div style={{ marginTop: 15 }}><div className="metric-label"><span>{preview.file_name}</span><span className="number">{number(preview.row_count)} rows · {preview.columns.length} columns</span></div><div className="table-scroll" style={{ marginTop: 8 }}><table><thead><tr>{preview.columns.slice(0, 6).map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{preview.preview_rows.slice(0, 4).map((row, index) => <tr key={index}>{preview.columns.slice(0, 6).map((column) => <td key={column}>{String(row[column] ?? '—')}</td>)}</tr>)}</tbody></table></div></div>}
      </Panel>
      <Panel title="Map transaction columns" note="Choose which uploaded headers correspond to the expected fields">
        {preview ? <><div className="mapping-grid">{mappingFields.map((field) => <div key={field.key}><label className="field-label" htmlFor={`map-${field.key}`}>{field.label}{field.required ? ' · required' : ''}</label><select className="select" id={`map-${field.key}`} value={mapping[field.key] ?? ''} onChange={(event) => { setMapping({ ...mapping, [field.key]: event.target.value }); setAnalysis(null); }} data-testid={`select-map-${field.key}`}><option value="">Not mapped</option>{preview.columns.map((column) => <option value={column} key={column}>{column}</option>)}</select></div>)}</div><div style={{ display: 'flex', gap: 10, alignItems: 'center', marginTop: 16, flexWrap: 'wrap' }}><button className="button" disabled={!file || !requiredMapped || analyzeMutation.isPending} onClick={runAnalysis} data-testid="button-analyze-upload">{analyzeMutation.isPending ? <LoaderCircle /> : <FileSpreadsheet />}{analyzeMutation.isPending ? 'Analyzing' : 'Analyze descriptively'}</button><span className="tiny">{requiredMapped ? 'Required fields are mapped.' : 'Map each required field to continue.'}</span></div></> : <div className="empty-box">Upload a file to map its available headers.</div>}
      </Panel>
    </div>
    {analyzeMutation.isError && <div className="error-box" style={{ marginTop: 16 }}>Analysis failed. Check the required fields and selected mappings, then try again.</div>}
    {exportError && <div className="error-box" style={{ marginTop: 16 }}>{exportError}</div>}
    {result && <div style={{ marginTop: 16 }}>
      <div className="grid kpis">
        <Metric label="Cleaned rows" value={number(result.summary.cleaned_rows)} foot={`${number(result.summary.input_rows)} source rows`} icon={Database} />
        <Metric label="Customers" value={number(result.summary.customer_count)} foot={`${number(result.summary.order_count)} orders`} icon={Users} />
        <Metric label="Positive gross revenue" value={money(result.summary.positive_gross_revenue)} foot={`Reference date ${dateShort(result.summary.reference_date)}`} icon={Wallet} />
        <Metric label="Excluded rows" value={number(result.summary.excluded_rows)} foot={`${number(result.summary.duplicate_rows_removed)} duplicates removed`} icon={Filter} />
      </div>
      <div className="grid two">
        <Panel title="Cleaning and missing values" note="Descriptive quality checks on this upload">
          <div className="table-scroll"><table><thead><tr><th>Check</th><th>Rows</th></tr></thead><tbody><tr><td>Duplicate rows in input</td><td className="number">{number(result.summary.duplicate_rows)}</td></tr><tr><td>Missing customer rows removed</td><td className="number">{number(result.summary.missing_customer_rows_removed)}</td></tr><tr><td>Retained cancellation rows</td><td className="number">{number(result.summary.retained_cancellation_rows)}</td></tr><tr><td>Retained zero-price rows</td><td className="number">{number(result.summary.retained_zero_price_rows)}</td></tr>{result.missing_values.map((missing) => <tr key={missing.column}><td>Missing · {missing.column}</td><td className="number">{number(missing.missing_count)}</td></tr>)}</tbody></table></div>
        </Panel>
        <Panel title="Order frequency" note="Customers grouped by observed order count">
          {result.order_frequency.length ? <div className="chart-wrap"><ResponsiveContainer><BarChart data={result.order_frequency}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="label" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip /><Bar dataKey="customers" fill="#315a4c" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div> : <div className="empty-box">No order frequency groups.</div>}
        </Panel>
      </div>
      <div className="grid equal" style={{ marginTop: 16 }}>
        <Panel title="Revenue trend" note={result.trend_period ? `Grouped by ${result.trend_period}` : 'No trend period was returned'}>{result.revenue_trend.length ? <div className="chart-wrap"><ResponsiveContainer><AreaChart data={result.revenue_trend}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="period" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tickFormatter={(value) => money(Number(value))} tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} width={56} /><Tooltip formatter={(value) => money(Number(value))} /><Area type="monotone" dataKey="revenue" stroke="#315a4c" fill="#d8e2d8" /></AreaChart></ResponsiveContainer></div> : <div className="empty-box">No revenue trend returned.</div>}</Panel>
        <Panel title="Customer feature preview" note="Derived RFM features from the uploaded records">
          {result.customer_features_preview.length ? <div className="table-scroll"><table><thead><tr>{Object.keys(result.customer_features_preview[0]).slice(0, 6).map((key) => <th key={key}>{key}</th>)}</tr></thead><tbody>{result.customer_features_preview.slice(0, 8).map((row, index) => <tr key={index}>{Object.keys(result.customer_features_preview[0]).slice(0, 6).map((key) => <td key={key}>{String(row[key] ?? '—')}</td>)}</tr>)}</tbody></table></div> : <div className="empty-box">No feature preview returned.</div>}
        </Panel>
      </div>
      <div className="grid equal" style={{ marginTop: 16 }}>
        {result.rfm_distributions.map((distribution) => <Panel key={distribution.field} title={distribution.label} note={`Descriptive distribution · ${distribution.field}`}>
          {distribution.bins.length ? <div className="chart-wrap"><ResponsiveContainer><BarChart data={distribution.bins.map((bin) => ({ ...bin, interval: `${bin.lower}–${bin.upper}` }))}><CartesianGrid stroke="#ebe8de" vertical={false} /><XAxis dataKey="interval" tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><YAxis tick={{ fontSize: 9, fill: '#89938c' }} axisLine={false} tickLine={false} /><Tooltip formatter={(value) => number(Number(value))} labelFormatter={(label) => `Range ${label}`} /><Bar dataKey="customers" name="Customers" fill="#78918a" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div> : <div className="empty-box">No distribution bins were returned.</div>}
        </Panel>)}
        {!result.rfm_distributions.length && <Panel title="RFM distributions" note="Descriptive customer-feature distributions"><div className="empty-box">No RFM distributions were returned for this upload.</div></Panel>}
      </div>
      <Panel title="Download analysis outputs" note="Exports reprocess the selected file using the current mapping; no file is stored" extra={<ArrowDownToLine size={15} color="#71847a" />}>
        <div className="filter-row"><button className="button secondary" disabled={!file || exportMutation.isPending} onClick={() => download('cleaned_transactions')} data-testid="button-export-cleaned"><ArrowDownToLine />Cleaned transactions CSV</button><button className="button secondary" disabled={!file || exportMutation.isPending} onClick={() => download('customer_features')} data-testid="button-export-features"><ArrowDownToLine />Customer features CSV</button>{exportMutation.isPending && <span className="tiny">Preparing download…</span>}</div>
      </Panel>
    </div>}
  </div>;
}
