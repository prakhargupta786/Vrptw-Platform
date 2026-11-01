import { Link, useParams } from 'react-router-dom';

import { StopSequenceEditor } from '../components/StopSequenceEditor';
import { KpiCard } from '@/components/charts/KpiCard';
import { Badge, Button, Card, Spinner } from '@/components/ui';
import { ROUTES } from '@/constants/routes';
import { useRunId } from '@/hooks/useRunId';
import { fmtKm, fmtMin, fmtPct } from '@/lib/format';
import { useRunDetail } from '@/lib/resource';
import type { RouteDetail } from '@/types/entities';

export default function RouteDetailPage() {
  const runId = useRunId();
  const { routeId = '' } = useParams();
  const route = useRunDetail<RouteDetail>(runId, 'routes', routeId);
  if (!route.data) return <Spinner />;
  const r = route.data;
  return (
    <div className="space-y-4">
      <Card title={`${r.route_id} · ${r.route_date}`} actions={<Link to={ROUTES.manifest(runId, routeId)}><Button variant="secondary">Manifest</Button></Link>}>
        <p className="text-sm">Vehicle {r.vehicle_id} · Driver {r.driver_id} · Shift {r.shift_id} {r.flags.map((f) => <Badge key={f} value={f} />)}</p>
      </Card>
      <div className="grid grid-cols-5 gap-3">
        <KpiCard label="Weight" value={fmtPct(r.utilization.weight_pct)} hint={`${r.total_weight_kg} / ${r.capacity.max_weight_kg} kg`} />
        <KpiCard label="Volume" value={fmtPct(r.utilization.volume_pct)} hint={`${r.total_volume_m3} / ${r.capacity.max_volume_m3} m³`} />
        <KpiCard label="Stops" value={fmtPct(r.utilization.stops_pct)} hint={`${r.stops.length} / ${r.capacity.max_stops}`} />
        <KpiCard label="Distance" value={fmtKm(r.total_distance_km)} />
        <KpiCard label="Duration" value={fmtMin(r.planned_duration_min)} />
      </div>
      {/* TODO: RouteMap with stop coordinates once the detail endpoint returns site lat/lon per stop */}
      <Card title="Stop sequence"><StopSequenceEditor runId={runId} routeId={routeId} stops={r.stops} /></Card>
    </div>
  );
}
