import { createColumnHelper } from '@tanstack/react-table';
import { useState } from 'react';

import { DataTable, FilterBar } from '@/components/data';
import { Badge, Card } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { fmtDateTime } from '@/lib/format';
import { useRunList } from '@/lib/resource';
import type { Outcome } from '@/types/entities';

const col = createColumnHelper<Outcome>();
const columns = [
  col.accessor('delivery_id', { header: 'Delivery' }),
  col.accessor('status', { header: 'Status', cell: (c) => <Badge value={c.getValue()} /> }),
  col.accessor('reason_code', { header: 'Reason', cell: (c) => c.getValue() ?? '—' }),
  col.accessor('actual_arrival', { header: 'Arrived', cell: (c) => fmtDateTime(c.getValue()) }),
  col.accessor('delay_minutes', { header: 'Delay (min)', cell: (c) => Math.round(c.getValue()) }),
];

export default function OutcomesPage() {
  const runId = useRunId();
  const { query, setPage } = usePagination();
  const [filters, setFilters] = useState<Record<string, string | undefined>>({});
  const list = useRunList<Outcome>(runId, 'outcomes', { ...query, ...filters });
  return (
    <Card title="Delivery outcomes">
      <FilterBar values={filters} onChange={(k, v) => setFilters((f) => ({ ...f, [k]: v }))} filters={[
        { key: 'status', label: 'Status', options: ['delivered', 'late', 'failed', 'skipped'] },
        { key: 'reason_code', label: 'Reason', options: ['CUSTOMER_ABSENT', 'ACCESS_RESTRICTED', 'OUTSIDE_WINDOW'] },
      ]} />
      <DataTable columns={columns} data={list.data} loading={list.isLoading} onPageChange={setPage} />
    </Card>
  );
}
