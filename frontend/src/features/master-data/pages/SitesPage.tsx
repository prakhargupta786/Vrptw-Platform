import { createColumnHelper } from '@tanstack/react-table';
import { useState } from 'react';

import { DataTable, FilterBar } from '@/components/data';
import { RouteMap } from '@/components/map/RouteMap';
import { Card } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import { useRunId } from '@/hooks/useRunId';
import { useRunList } from '@/lib/resource';
import type { Site } from '@/types/entities';

const col = createColumnHelper<Site>();
const columns = [
  col.accessor('site_id', { header: 'Site' }),
  col.accessor('name', { header: 'Name' }),
  col.accessor('region', { header: 'Region' }),
  col.accessor('address_type', { header: 'Type' }),
  col.accessor((s) => s.access_restrictions.max_vehicle_type ?? '—', { id: 'max', header: 'Max vehicle' }),
  col.accessor((s) => `${s.lat.toFixed(4)}, ${s.lon.toFixed(4)}`, { id: 'coords', header: 'Lat, Lon' }),
];

export default function SitesPage() {
  const runId = useRunId();
  const { query, setPage } = usePagination(100);
  const [filters, setFilters] = useState<Record<string, string | undefined>>({});
  const sites = useRunList<Site>(runId, 'sites', { ...query, ...filters });
  return (
    <div className="space-y-4">
      <Card title="Sites map"><RouteMap points={(sites.data?.items ?? []).map((s) => ({ id: s.site_id, lat: s.lat, lon: s.lon, label: s.site_id }))} /></Card>
      <Card title="Customer sites">
        <FilterBar filters={[{ key: 'address_type', label: 'Type', options: ['residential', 'commercial', 'industrial'] }]}
          values={filters} onChange={(k, v) => setFilters((f) => ({ ...f, [k]: v }))} />
        <DataTable columns={columns} data={sites.data} loading={sites.isLoading} onPageChange={setPage} />
      </Card>
    </div>
  );
}
