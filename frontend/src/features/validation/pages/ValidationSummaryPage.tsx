import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { validationApi } from '../api';
import { Can } from '@/components/guards';
import { Badge, Button, Card, Spinner } from '@/components/ui';
import { P } from '@/constants/permissions';
import { JobProgress } from '@/features/runs/components/JobProgress';
import { useRunId } from '@/hooks/useRunId';
import { fmtDateTime } from '@/lib/format';

export default function ValidationSummaryPage() {
  const runId = useRunId();
  const [jobId, setJobId] = useState<string | null>(null);
  const summary = useQuery({ queryKey: ['runs', runId, 'validation'], queryFn: () => validationApi.summary(runId) });
  if (!summary.data) return <Spinner />;
  const s = summary.data;
  return (
    <Card title={`Validation · ${s.passed} passed, ${s.failed} failed`} actions={
      <Can perm={P.VALIDATION_RUN}><Button onClick={async () => setJobId((await validationApi.run(runId)).job_id)}>Re-run checks</Button></Can>}>
      <JobProgress jobId={jobId} onDone={() => summary.refetch()} />
      <p className="mb-2 text-xs text-gray-500">Last run {fmtDateTime(s.at)}</p>
      <table className="w-full text-sm">
        <thead className="text-left text-gray-500"><tr><th>Check</th><th>Result</th><th>Failed rows</th><th>Sample IDs</th></tr></thead>
        <tbody>{s.checks.map((c) => (
          <tr key={c.name} className="border-t"><td className="py-2">{c.name}</td><td><Badge value={c.status} /></td>
            <td>{c.failed_rows}</td><td className="text-gray-500">{c.sample_ids.slice(0, 3).join(', ')}</td></tr>))}
        </tbody>
      </table>
    </Card>
  );
}
