import { useParams } from 'react-router-dom';

import { useManifest } from '../hooks';
import { Card, Spinner } from '@/components/ui';
import { useRunId } from '@/hooks/useRunId';
import { fmtDateTime } from '@/lib/format';

/** Warehouse view: load in reverse of delivery order (last stop goes in first). */
export default function ManifestPage() {
  const runId = useRunId();
  const { routeId = '' } = useParams();
  const m = useManifest(runId, routeId);
  if (!m.data) return <Spinner />;
  const n = m.data.load_order.length;
  return (
    <Card title={`Load manifest · ${routeId}`} actions={<button className="text-sm underline" onClick={() => window.print()}>Print</button>}>
      <table className="w-full text-sm">
        <thead className="text-left text-gray-500"><tr><th>Load #</th><th>Stop #</th><th>Delivery</th><th>Planned arrival</th></tr></thead>
        <tbody>{m.data.load_order.map((s, i) => (
          <tr key={s.stop_id} className="border-t"><td>{i + 1}</td><td>{n - i}</td><td>{s.delivery_id}</td><td>{fmtDateTime(s.planned_arrival)}</td></tr>))}
        </tbody>
      </table>
    </Card>
  );
}
