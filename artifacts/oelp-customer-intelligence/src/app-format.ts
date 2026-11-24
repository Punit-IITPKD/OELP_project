export const money = (value?: number | null) =>
  value == null || !Number.isFinite(value)
    ? '—'
    : new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(value);

export const number = (value?: number | null) =>
  value == null || !Number.isFinite(value)
    ? '—'
    : new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 }).format(value);

export const percent = (value?: number | null) =>
  value == null || !Number.isFinite(value) ? '—' : `${(value * 100).toFixed(1)}%`;

export const dateShort = (value?: string | null) =>
  value
    ? new Date(value).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    : '—';

export const COLORS = ['#315a4c', '#d8ad5e', '#c57d5c', '#78918a', '#a8ad78', '#b9757d', '#789eb0'];
