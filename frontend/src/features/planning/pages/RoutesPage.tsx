import { createColumnHelper } from '@tanstack/react-table';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { DataTable, FilterBar } from '@/components/data';
import { Badge, Card } from '@/components/ui';
import { ROUTES } from '@/constants/routes';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { fmtKm, fmtMin } from '@/lib/format';
import { useRunList } from '@/lib/resource';
import type { Route } from '@/types/entities';

const col = createColumnHelper<Route>();
const columns = [
  col.accessor('route_id', { header: 'Route' }),
  col.accessor('route_date', { header: 'Date' }),
  col.accessor('vehicle_id', { header: 'Vehicle' }),
  col.accessor('driver_id', { header: 'Driver' }),
  col.accessor('total_weight_kg', { header: 'Load (kg)' }),
  col.accessor('total_distance_km', { header: 'Distance', cell: (c) => fmtKm(c.getValue()) }),
  col.accessor('planned_duration_min', { header: 'Duration', cell: (c) => fmtMin(c.getValue()) }),
  col.accessor('flags', { header: 'Flags', cell: (c) => <span className="flex gap-1">{c.getValue().map((f) => <Badge key={f} value={f} />)}</span> }),
];

export default function RoutesPage() {
  const runId = useRunId();
  const navigate = useNavigate();
  const { query, setPage } = usePagination();
  const [filters, setFilters] = useState<Record<string, string | undefined>>({});
  const routes = useRunList<Route>(runId, 'routes', { ...query, ...filters });
  return (
    <Card title="Routes">
      <FilterBar values={filters} onChange={(k, v) => setFilters((f) => ({ ...f, [k]: v }))} filters={[
        { key: 'flag', label: 'Flag', options: ['capacity_exceeded', 'shift_exceeded', 'late'] },
      ]} />
      <DataTable columns={columns} data={routes.data} loading={routes.isLoading} onPageChange={setPage}
        onRowClick={(r) => navigate(ROUTES.route(runId, r.route_id))} />
    </Card>
  );
}
