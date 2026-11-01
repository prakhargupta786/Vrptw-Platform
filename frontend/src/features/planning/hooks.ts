import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { planningApi, type AddStopIn } from './api';
import { qk } from '@/constants/queryKeys';

export const useManifest = (runId: string, routeId: string) =>
  useQuery({ queryKey: qk.detail(runId, 'manifest', routeId), queryFn: () => planningApi.manifest(runId, routeId) });

/** All route mutations invalidate the route detail + routes list (totals and flags are recomputed server-side). */
function useRouteMutation<V>(runId: string, routeId: string, fn: (v: V) => Promise<unknown>) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.detail(runId, 'routes', routeId) });
      qc.invalidateQueries({ queryKey: ['runs', runId, 'routes'] });
      qc.invalidateQueries({ queryKey: ['runs', runId, 'unserved'] });
    },
  });
}

export const useAddStop = (runId: string, routeId: string) =>
  useRouteMutation(runId, routeId, (b: AddStopIn) => planningApi.addStop(runId, routeId, b));
export const useReorderStops = (runId: string, routeId: string) =>
  useRouteMutation(runId, routeId, (ids: string[]) => planningApi.reorder(runId, routeId, ids));
export const useRemoveStop = (runId: string, routeId: string) =>
  useRouteMutation(runId, routeId, ({ stopId, reason }: { stopId: string; reason: string }) => planningApi.removeStop(runId, routeId, stopId, reason));
