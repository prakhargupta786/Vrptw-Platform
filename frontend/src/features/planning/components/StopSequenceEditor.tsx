import { useEffect, useState } from 'react';

import { useRemoveStop, useReorderStops } from '../hooks';
import { Can } from '@/components/guards';
import { Button } from '@/components/ui';
import { P } from '@/constants/permissions';
import { errorMessage } from '@/lib/http';
import { fmtDateTime } from '@/lib/format';
import type { RouteStop } from '@/types/entities';

/** Move stops up/down, then save the full order. Server re-times stops and returns 409 on rule violations. */
export function StopSequenceEditor({ runId, routeId, stops }: { runId: string; routeId: string; stops: RouteStop[] }) {
  const [order, setOrder] = useState(stops);
  useEffect(() => setOrder(stops), [stops]);
  const reorder = useReorderStops(runId, routeId);
  const remove = useRemoveStop(runId, routeId);
  const move = (i: number, d: -1 | 1) => setOrder((o) => {
    const n = [...o];
    [n[i], n[i + d]] = [n[i + d], n[i]];
    return n;
  });
  const dirty = order.some((s, i) => s.stop_id !== stops[i]?.stop_id);

  return (
    <div className="space-y-2">
      <ol className="divide-y text-sm">
        {order.map((s, i) => (
          <li key={s.stop_id} className="flex items-center justify-between py-2">
            <span><b>{i + 1}.</b> {s.delivery_id} <span className="text-gray-500">· arr {fmtDateTime(s.planned_arrival)}</span></span>
            <Can perm={P.ROUTES_PLAN}>
              <span className="flex gap-1">
                <Button variant="ghost" disabled={i === 0} onClick={() => move(i, -1)}>↑</Button>
                <Button variant="ghost" disabled={i === order.length - 1} onClick={() => move(i, 1)}>↓</Button>
                <Button variant="ghost" onClick={() => remove.mutate({ stopId: s.stop_id, reason: 'replanned' })}>Remove</Button>
              </span>
            </Can>
          </li>))}
      </ol>
      {(reorder.isError || remove.isError) && <p className="text-sm text-red-600">{errorMessage(reorder.error ?? remove.error)}</p>}
      <Can perm={P.ROUTES_PLAN}>
        <Button disabled={!dirty || reorder.isPending} onClick={() => reorder.mutate(order.map((s) => s.stop_id))}>Save sequence</Button>
      </Can>
    </div>
  );
}
