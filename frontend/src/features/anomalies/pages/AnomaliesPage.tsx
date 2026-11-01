import { useQuery } from '@tanstack/react-query';
import { createColumnHelper } from '@tanstack/react-table';

import { anomaliesApi } from '../api';
import { DataTable } from '@/components/data';
import { Can } from '@/components/guards';
import { Card } from '@/components/ui';
import { P } from '@/constants/permissions';
import { usePagination } from '@/hooks/usePagination';
import { usePermission } from '@/hooks/usePermission';
import { useRunId } from '@/hooks/useRunId';
import { fmtPct } from '@/lib/format';
import { useRunList } from '@/lib/resource';
import type { GroundTruth } from '@/types/entities';

const col = createColumnHelper<GroundTruth>();
const gtColumns = [
  col.accessor('issue_type', { header: 'Issue' }),
  col.accessor('affected_entity', { header: 'Entity' }),
  col.accessor('affected_id', { header: 'ID' }),
  col.accessor('expected_decision', { header: 'Expected decision' }),
];

function GroundTruthTable({ runId }: { runId: string }) {
  const { query, setPage } = usePagination();
  const gt = useRunList<GroundTruth>(runId, 'ground-truth', query);
  return <DataTable columns={gtColumns} data={gt.data} loading={gt.isLoading} onPageChange={setPage} />;
}

export default function AnomaliesPage() {
  const runId = useRunId();
  const canScore = usePermission(P.METRICS_READ);
  const scores = useQuery({ queryKey: ['runs', runId, 'anomaly-scores'], queryFn: () => anomaliesApi.scores(runId), enabled: canScore });
  return (
    <div className="space-y-4">
      <Card title="Detection quality (validation vs ground truth)">
        <table className="w-full text-sm">
          <thead className="text-left text-gray-500"><tr><th>Issue type</th><th>TP</th><th>FP</th><th>FN</th><th>Precision</th><th>Recall</th></tr></thead>
          <tbody>{scores.data?.map((s) => (
            <tr key={s.issue_type} className="border-t"><td className="py-2">{s.issue_type}</td><td>{s.tp}</td><td>{s.fp}</td><td>{s.fn}</td>
              <td>{fmtPct(s.precision)}</td><td>{fmtPct(s.recall)}</td></tr>))}
          </tbody>
        </table>
      </Card>
      <Can perm={P.GROUND_TRUTH_READ}><Card title="Ground truth labels"><GroundTruthTable runId={runId} /></Card></Can>
    </div>
  );
}
