import { createColumnHelper } from '@tanstack/react-table';

import { DataTable } from '@/components/data';
import { Card } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { useRunList } from '@/lib/resource';
import type { Unserved } from '@/types/entities';

const col = createColumnHelper<Unserved>();
const columns = [col.accessor('delivery_id', { header: 'Delivery' }), col.accessor('reason', { header: 'Reason' })];

export default function UnservedPage() {
  const runId = useRunId();
  const { query, setPage } = usePagination();
  const list = useRunList<Unserved>(runId, 'unserved', query);
  // TODO: "Assign to route" action -> planningApi.addStop
  return <Card title="Unserved deliveries"><DataTable columns={columns} data={list.data} loading={list.isLoading} onPageChange={setPage} /></Card>;
}
