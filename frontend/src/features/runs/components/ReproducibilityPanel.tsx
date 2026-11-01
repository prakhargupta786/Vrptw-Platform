import { useState } from 'react';

import { JobProgress } from './JobProgress';
import { useReproduce, useReproducibility } from '../hooks';
import { Can } from '@/components/guards';
import { Badge, Button, Card } from '@/components/ui';
import { P } from '@/constants/permissions';

export function ReproducibilityPanel({ runId, enabled }: { runId: string; enabled: boolean }) {
  const [jobId, setJobId] = useState<string | null>(null);
  const report = useReproducibility(runId, enabled);
  const reproduce = useReproduce(runId);
  return (
    <Card title="Reproducibility" actions={
      <Can perm={P.RUNS_RERUN}>
        <Button variant="secondary" disabled={!enabled || reproduce.isPending}
          onClick={() => reproduce.mutate(undefined, { onSuccess: (r) => setJobId(r.job_id) })}>Run check (2 reruns)</Button>
      </Can>}>
      <JobProgress jobId={jobId} onDone={() => report.refetch()} />
      {report.data ? (
        <table className="mt-2 w-full text-sm">
          <thead className="text-gray-500"><tr><th className="text-left">File</th><th>Rows</th><th>SHA-256</th></tr></thead>
          <tbody>{report.data.files.map((f) => (
            <tr key={f.name} className="border-t"><td>{f.name}</td><td className="text-center">{f.rows_a} / {f.rows_b}</td>
              <td className="text-center"><Badge value={f.match ? 'pass' : 'fail'} /></td></tr>))}
          </tbody>
        </table>
      ) : <p className="text-sm text-gray-500">No check has run yet.</p>}
    </Card>
  );
}
