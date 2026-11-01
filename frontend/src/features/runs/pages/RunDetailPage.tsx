import { Link, useParams } from 'react-router-dom';

import { ReproducibilityPanel } from '../components/ReproducibilityPanel';
import { useLockRun, useRun } from '../hooks';
import { Can } from '@/components/guards';
import { Badge, Button, Card, Spinner } from '@/components/ui';
import { P } from '@/constants/permissions';
import { ROUTES } from '@/constants/routes';

export default function RunDetailPage() {
  const { runId = '' } = useParams();
  const run = useRun(runId);
  const lock = useLockRun(runId);
  if (run.isLoading || !run.data) return <Spinner />;
  const r = run.data;
  const browsable = !['queued', 'generating', 'failed'].includes(r.status);

  return (
    <div className="space-y-4">
      <Card title={r.name} actions={<div className="flex items-center gap-2"><Badge value={r.status} />
        <Can perm={P.RUNS_LOCK}><Button variant="secondary" disabled={r.status !== 'validated' || lock.isPending} onClick={() => lock.mutate()}>Lock run</Button></Can></div>}>
        <dl className="grid grid-cols-4 gap-4 text-sm">
          <div><dt className="text-gray-500">Seed</dt><dd>{r.seed}</dd></div>
          {Object.entries(r.config.scale).map(([k, v]) => <div key={k}><dt className="text-gray-500">{k}</dt><dd>{v}</dd></div>)}
          <div><dt className="text-gray-500">Anomaly rate</dt><dd>{r.config.anomaly_rate}</dd></div>
        </dl>
        {r.row_counts && (
          <div className="mt-4 grid grid-cols-4 gap-2 text-sm">
            {Object.entries(r.row_counts).map(([t, n]) => <div key={t} className="rounded bg-gray-50 p-2"><span className="text-gray-500">{t}</span> <b>{n}</b></div>)}
          </div>)}
        {browsable && (
          <div className="mt-4 flex flex-wrap gap-2">
            <Link to={ROUTES.routes(runId)}><Button variant="secondary">Routes</Button></Link>
            <Link to={ROUTES.validation(runId)}><Button variant="secondary">Validation</Button></Link>
            <Link to={ROUTES.anomalies(runId)}><Button variant="secondary">Anomalies</Button></Link>
            <Link to={ROUTES.exports(runId)}><Button variant="secondary">Exports</Button></Link>
          </div>)}
      </Card>
      <ReproducibilityPanel runId={runId} enabled={['validated', 'locked'].includes(r.status)} />
    </div>
  );
}
