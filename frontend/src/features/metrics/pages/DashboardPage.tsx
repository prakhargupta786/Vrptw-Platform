import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';

import { metricsApi } from '../api';
import { KpiCard } from '@/components/charts/KpiCard';
import { TimeseriesChart } from '@/components/charts/TimeseriesChart';
import { Card, Spinner } from '@/components/ui';
import { qk } from '@/constants/queryKeys';
import { ROUTES } from '@/constants/routes';
import { fmtKm, fmtMin, fmtPct } from '@/lib/format';
import { useRunStore } from '@/store/run.store';

export default function DashboardPage() {
  const runId = useRunStore((s) => s.runId);
  const kpis = useQuery({ queryKey: qk.metrics(runId ?? '', 'kpis'), queryFn: () => metricsApi.kpis(runId!), enabled: !!runId });
  const series = useQuery({ queryKey: qk.metrics(runId ?? '', 'ts', { m: 'on_time_rate' }), queryFn: () => metricsApi.timeseries(runId!, 'on_time_rate'), enabled: !!runId });
  const reasons = useQuery({ queryKey: qk.metrics(runId ?? '', 'reasons'), queryFn: () => metricsApi.failuresByReason(runId!), enabled: !!runId });

  if (!runId) return <Card title="No run selected"><p className="text-sm">Pick a run from the switcher, or <Link className="underline" to={ROUTES.runs}>open the runs list</Link>.</p></Card>;
  if (!kpis.data) return <Spinner />;
  const k = kpis.data;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <KpiCard label="On-time rate" value={fmtPct(k.on_time_rate)} />
        <KpiCard label="Failed rate" value={fmtPct(k.failed_rate)} />
        <KpiCard label="Avg delay" value={fmtMin(k.avg_delay_min)} />
        <KpiCard label="Unserved" value={k.unserved_count.toLocaleString()} />
        <KpiCard label="Total distance" value={fmtKm(k.total_distance_km)} />
        <KpiCard label="Total travel" value={fmtMin(k.total_travel_min)} />
        <KpiCard label="Overtime shifts" value={String(k.overtime_count)} />
      </div>
      <Card title="On-time rate by day"><TimeseriesChart data={series.data ?? []} label="On-time rate" /></Card>
      <Card title="Failures by reason">
        {reasons.data?.map((r) => <div key={r.reason_code} className="flex justify-between border-b py-1 text-sm"><span>{r.reason_code}</span><span>{r.count} · {fmtPct(r.share)}</span></div>)}
      </Card>
    </div>
  );
}
