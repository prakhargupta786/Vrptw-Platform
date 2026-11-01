import { useParams } from 'react-router-dom';

import type { OrderDetail } from '../api';
import { Badge, Card, Spinner } from '@/components/ui';
import { useRunId } from '@/hooks/useRunId';
import { fmtDateTime } from '@/lib/format';
import { useRunDetail } from '@/lib/resource';

/** Order-to-delivery traceability (Supplier view). */
export default function OrderDetailPage() {
  const runId = useRunId();
  const { orderId } = useParams();
  const order = useRunDetail<OrderDetail>(runId, 'orders', orderId);
  if (!order.data) return <Spinner />;
  const o = order.data;
  return (
    <div className="space-y-4">
      <Card title={o.order_id} actions={<Badge value={o.status} />}>
        <p className="text-sm">Site {o.site_id} · {o.quantity} units · {o.weight_kg} kg · {o.volume_m3} m³ · {o.priority} priority</p>
      </Card>
      <Card title="Deliveries and outcomes">
        {o.deliveries.map((d) => {
          const out = o.outcomes.find((x) => x.delivery_id === d.delivery_id);
          return (
            <div key={d.delivery_id} className="flex items-center justify-between border-b py-2 text-sm">
              <span>{d.delivery_id} · {d.required_vehicle_type}</span>
              <span className="flex items-center gap-2">
                <Badge value={d.status} />
                {out && <><Badge value={out.status} /><span className="text-gray-500">{fmtDateTime(out.actual_arrival)}{out.reason_code ? ` · ${out.reason_code}` : ''}</span></>}
              </span>
            </div>);
        })}
      </Card>
    </div>
  );
}
