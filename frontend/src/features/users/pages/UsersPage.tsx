import { createColumnHelper } from '@tanstack/react-table';

import { useDeactivateUser, useUsers } from '../hooks';
import { DataTable } from '@/components/data';
import { Badge, Button, Card } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import type { User } from '@/types/entities';

const col = createColumnHelper<User>();

export default function UsersPage() {
  const { query, setPage } = usePagination();
  const users = useUsers(query);
  const deactivate = useDeactivateUser();
  const columns = [
    col.accessor('name', { header: 'Name' }),
    col.accessor('email', { header: 'Email' }),
    col.accessor('role', { header: 'Role', cell: (c) => <Badge value={c.getValue()} /> }),
    col.accessor('is_active', { header: 'Active', cell: (c) => (c.getValue() ? 'Yes' : 'No') }),
    col.display({ id: 'actions', cell: (c) => c.row.original.is_active && (
      <Button variant="ghost" onClick={() => deactivate.mutate(c.row.original.id)}>Deactivate</Button>) }),
  ];
  // TODO: UserForm modal (components/UserForm.tsx) for create/edit
  return <Card title="Users"><DataTable columns={columns} data={users.data} loading={users.isLoading} onPageChange={setPage} /></Card>;
}
