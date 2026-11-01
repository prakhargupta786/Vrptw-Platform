import { type ColumnDef, flexRender, getCoreRowModel, useReactTable } from '@tanstack/react-table';

import { EmptyState } from './EmptyState';
import { Pagination } from './Pagination';
import { Spinner } from '../ui/Spinner';
import type { Paginated } from '@/types/api';

interface Props<T> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  columns: ColumnDef<T, any>[];
  data?: Paginated<T>;
  loading?: boolean;
  onPageChange?: (page: number) => void;
  onRowClick?: (row: T) => void;
}

/** Server-paginated table: the API does paging/sorting; this only renders a page. */
export function DataTable<T>({ columns, data, loading, onPageChange, onRowClick }: Props<T>) {
  const table = useReactTable({ data: data?.items ?? [], columns, getCoreRowModel: getCoreRowModel(), manualPagination: true });
  if (loading) return <Spinner />;
  if (!data?.items.length) return <EmptyState />;
  return (
    <div>
      <table className="w-full text-left text-sm">
        <thead className="border-b text-gray-500">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>{hg.headers.map((h) => <th key={h.id} className="px-2 py-2 font-medium">{flexRender(h.column.columnDef.header, h.getContext())}</th>)}</tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className={`border-b ${onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}`} onClick={() => onRowClick?.(row.original)}>
              {row.getVisibleCells().map((c) => <td key={c.id} className="px-2 py-2">{flexRender(c.column.columnDef.cell, c.getContext())}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
      {onPageChange && <Pagination page={data.page} pageSize={data.page_size} total={data.total} onChange={onPageChange} />}
    </div>
  );
}
