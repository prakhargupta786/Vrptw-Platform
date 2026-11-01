import { createColumnHelper } from '@tanstack/react-table';
import { useState } from 'react';

import { DataTable, FilterBar } from '@/components/data';
import { Badge, Card } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { useRunList } from '@/lib/resource';
import type { Delivery } from '@/types/entities';

const col = createColumnHelper<Delivery>();
const columns = [
  col.accessor('delivery_id', { header: 'Delivery' }),
  col.accessor('order_id', { header: 'Order' }),
  col.accessor('required_vehicle_type', { header: 'Vehicle type' }),
  col.accessor('service_minutes', { header: 'Service (min)' }),
  col.accessor('status', { header: 'Status', cell: (c) => <Badge value={c.getValue()} /> }),
];

export default function DeliveriesPage() {
  const runId = useRunId();
  const { query, setPage } = usePagination();
  const [filters, setFilters] = useState<Record<string, string | undefined>>({});
  const deliveries = useRunList<Delivery>(runId, 'deliveries', { ...query, ...filters });
  return (
    <Card title="Deliveries">
      <FilterBar values={filters} onChange={(k, v) => setFilters((f) => ({ ...f, [k]: v }))} filters={[
        { key: 'status', label: 'Status', options: ['pending', 'assigned', 'unserved', 'done'] },
        { key: 'required_vehicle_type', label: 'Vehicle', options: ['mini', 'van', 'truck'] },
      ]} />
      <DataTable columns={columns} data={deliveries.data} loading={deliveries.isLoading} onPageChange={setPage} />
    </Card>
  );
}
