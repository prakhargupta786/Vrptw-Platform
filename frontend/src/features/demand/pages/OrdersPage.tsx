import { createColumnHelper } from '@tanstack/react-table';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { DataTable, FilterBar } from '@/components/data';
import { Badge, Card } from '@/components/ui';
import { ROUTES } from '@/constants/routes';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { fmtDateTime } from '@/lib/format';
import { useRunList } from '@/lib/resource';
import type { Order } from '@/types/entities';

const col = createColumnHelper<Order>();
const columns = [
  col.accessor('order_id', { header: 'Order' }),
  col.accessor('site_id', { header: 'Site' }),
  col.accessor('quantity', { header: 'Qty' }),
  col.accessor('weight_kg', { header: 'Weight (kg)' }),
  col.accessor('priority', { header: 'Priority' }),
  col.accessor('status', { header: 'Status', cell: (c) => <Badge value={c.getValue()} /> }),
  col.accessor('created_at', { header: 'Created', cell: (c) => fmtDateTime(c.getValue()) }),
];

export default function OrdersPage() {
  const runId = useRunId();
  const navigate = useNavigate();
  const { query, setPage } = usePagination();
  const [filters, setFilters] = useState<Record<string, string | undefined>>({});
  const orders = useRunList<Order>(runId, 'orders', { ...query, ...filters });
  return (
    <Card title="Orders">
      <FilterBar values={filters} onChange={(k, v) => setFilters((f) => ({ ...f, [k]: v }))} filters={[
        { key: 'status', label: 'Status', options: ['created', 'planned', 'completed', 'cancelled'] },
        { key: 'priority', label: 'Priority', options: ['low', 'normal', 'high'] },
      ]} />
      <DataTable columns={columns} data={orders.data} loading={orders.isLoading} onPageChange={setPage}
        onRowClick={(o) => navigate(ROUTES.order(runId, o.order_id))} />
    </Card>
  );
}
