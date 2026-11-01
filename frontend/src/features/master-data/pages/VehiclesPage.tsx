import { useQuery } from '@tanstack/react-query';
import { createColumnHelper } from '@tanstack/react-table';
import { useState } from 'react';

import { masterApi } from '../api';
import { DataTable } from '@/components/data';
import { Badge, Card } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { fmtDate } from '@/lib/format';
import { useRunList } from '@/lib/resource';
import type { Vehicle } from '@/types/entities';

const col = createColumnHelper<Vehicle>();
const columns = [
  col.accessor('vehicle_id', { header: 'Vehicle' }),
  col.accessor('type', { header: 'Type' }),
  col.accessor('status', { header: 'Status', cell: (c) => <Badge value={c.getValue()} /> }),
  col.accessor((v) => v.restricted_zones.join(', ') || '—', { id: 'zones', header: 'Restricted zones' }),
];

export default function VehiclesPage() {
  const runId = useRunId();
  const { query, setPage } = usePagination();
  const [selected, setSelected] = useState<string | null>(null);
  const vehicles = useRunList<Vehicle>(runId, 'vehicles', query);
  const caps = useQuery({ queryKey: ['runs', runId, 'capacities', selected], queryFn: () => masterApi.capacities(runId, selected!), enabled: !!selected });
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="col-span-2"><Card title="Fleet"><DataTable columns={columns} data={vehicles.data} loading={vehicles.isLoading} onPageChange={setPage} onRowClick={(v) => setSelected(v.vehicle_id)} /></Card></div>
      <Card title={selected ? `Capacity history · ${selected}` : 'Select a vehicle'}>
        {caps.data?.map((c) => (
          <div key={c.capacity_id} className="border-b py-2 text-sm">
            <b>{c.max_weight_kg} kg · {c.max_volume_m3} m³ · {c.max_stops} stops</b>
            <p className="text-gray-500">{fmtDate(c.effective_from)} → {fmtDate(c.effective_to)}</p>
          </div>))}
      </Card>
    </div>
  );
}
