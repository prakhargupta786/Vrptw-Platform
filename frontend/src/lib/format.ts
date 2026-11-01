export const fmtPct = (v: number, digits = 1) => `${(v * 100).toFixed(digits)}%`;
export const fmtKm = (v: number) => `${v.toFixed(1)} km`;
export const fmtMin = (v: number) => (v >= 60 ? `${Math.floor(v / 60)}h ${Math.round(v % 60)}m` : `${Math.round(v)}m`);
export const fmtDateTime = (iso: string | null) => (iso ? new Date(iso).toLocaleString() : '—');
export const fmtDate = (iso: string | null) => (iso ? new Date(iso).toLocaleDateString() : '—');
export const fmtBytes = (n: number | null) =>
  n == null ? '—' : n < 1024 ** 2 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1024 ** 2).toFixed(1)} MB`;
