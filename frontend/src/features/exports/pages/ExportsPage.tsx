import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { exportsApi } from '../api';
import { Button, Card } from '@/components/ui';
import { JobProgress } from '@/features/runs/components/JobProgress';
import { useRunId } from '@/hooks/useRunId';
import { fmtBytes, fmtDateTime } from '@/lib/format';

export default function ExportsPage() {
  const runId = useRunId();
  const [jobId, setJobId] = useState<string | null>(null);
  const list = useQuery({ queryKey: ['runs', runId, 'exports'], queryFn: () => exportsApi.list(runId) });
  return (
    <Card title="Exports" actions={<Button onClick={async () => setJobId((await exportsApi.create(runId)).job_id)}>New export bundle</Button>}>
      <JobProgress jobId={jobId} onDone={() => list.refetch()} />
      <table className="mt-2 w-full text-sm">
        <thead className="text-left text-gray-500"><tr><th>Created</th><th>Includes</th><th>Size</th><th>SHA-256</th><th /></tr></thead>
        <tbody>{list.data?.map((e) => (
          <tr key={e.id} className="border-t">
            <td className="py-2">{fmtDateTime(e.created_at)}</td><td>{e.include.join(', ')}</td><td>{fmtBytes(e.size_bytes)}</td>
            <td className="font-mono text-xs">{e.sha256?.slice(0, 12)}…</td>
            <td><Button variant="secondary" onClick={() => exportsApi.download(runId, e.id)}>Download</Button></td>
          </tr>))}
        </tbody>
      </table>
    </Card>
  );
}
