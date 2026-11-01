import { useQuery } from '@tanstack/react-query';
import { createColumnHelper } from '@tanstack/react-table';
import { useState } from 'react';

import { masterApi } from '../api';
import { DataTable } from '@/components/data';
import { Card } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { fmtDateTime } from '@/lib/format';
import { useRunList } from '@/lib/resource';
import type { Driver } from '@/types/entities';

const col = createColumnHelper<Driver>();
const columns = [
  col.accessor('driver_id', { header: 'Driver' }),
  col.accessor('name', { header: 'Name' }),
  col.accessor('license_class', { header: 'License' }),
  col.accessor('home_depot', { header: 'Home depot' }),
  col.accessor('is_active', { header: 'Active', cell: (c) => (c.getValue() ? 'Yes' : 'No') }),
];

export default function DriversPage() {
  const runId = useRunId();
  const { query, setPage } = usePagination();
  const [selected, setSelected] = useState<string | null>(null);
  const drivers = useRunList<Driver>(runId, 'drivers', query);
  const shifts = useQuery({ queryKey: ['runs', runId, 'shifts', selected], queryFn: () => masterApi.shifts(runId, selected!), enabled: !!selected });
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="col-span-2"><Card title="Drivers"><DataTable columns={columns} data={drivers.data} loading={drivers.isLoading} onPageChange={setPage} onRowClick={(d) => setSelected(d.driver_id)} /></Card></div>
      <Card title={selected ? `Shifts · ${selected}` : 'Select a driver'}>
        {shifts.data?.map((s) => (
          <div key={s.shift_id} className="border-b py-2 text-sm">
            {fmtDateTime(s.start_at)} → {fmtDateTime(s.end_at)}
            <p className="text-gray-500">break {s.break_minutes}m · max {s.max_driving_hours}h driving</p>
          </div>))}
      </Card>
    </div>
  );
}
