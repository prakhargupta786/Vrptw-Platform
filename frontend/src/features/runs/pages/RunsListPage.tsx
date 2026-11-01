import { createColumnHelper } from '@tanstack/react-table';
import { Link, useNavigate } from 'react-router-dom';

import { useRuns } from '../hooks';
import { DataTable } from '@/components/data';
import { Can } from '@/components/guards';
import { Badge, Button, Card } from '@/components/ui';
import { P } from '@/constants/permissions';
import { ROUTES } from '@/constants/routes';
import { usePagination } from '@/hooks/usePagination';
import { fmtDateTime } from '@/lib/format';
import type { Run } from '@/types/entities';

const col = createColumnHelper<Run>();
const columns = [
  col.accessor('name', { header: 'Name' }),
  col.accessor('seed', { header: 'Seed' }),
  col.accessor((r) => `${r.config.scale.sites} / ${r.config.scale.deliveries} / ${r.config.scale.vehicles} / ${r.config.scale.days}d`, { id: 'scale', header: 'Sites / Deliveries / Vehicles / Days' }),
  col.accessor('status', { header: 'Status', cell: (c) => <Badge value={c.getValue()} /> }),
  col.accessor('created_at', { header: 'Created', cell: (c) => fmtDateTime(c.getValue()) }),
];

export default function RunsListPage() {
  const { query, setPage } = usePagination();
  const runs = useRuns(query);
  const navigate = useNavigate();
  return (
    <Card title="Generation runs" actions={<Can perm={P.RUNS_CREATE}><Link to={ROUTES.newRun}><Button>New run</Button></Link></Can>}>
      <DataTable columns={columns} data={runs.data} loading={runs.isLoading} onPageChange={setPage} onRowClick={(r) => navigate(ROUTES.run(r.id))} />
    </Card>
  );
}
