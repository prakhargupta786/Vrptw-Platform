import { http } from '@/lib/http';
import type { JobAccepted } from '@/types/api';
import type { Route, RouteStop, Unserved } from '@/types/entities';
import type { ReasonCode } from '@/types/enums';

export interface PlanIn { date: string; delivery_ids?: string[]; strategy?: 'greedy_insertion' | 'ortools' }
export interface AddStopIn { delivery_id: string; position: number; force?: boolean }
export interface Manifest { route_id: string; load_order: RouteStop[] }

export const planningApi = {
  manifest: async (runId: string, routeId: string) => (await http.get<Manifest>(`/runs/${runId}/routes/${routeId}/manifest`)).data,
  plan: async (runId: string, body: PlanIn) => (await http.post<JobAccepted>(`/runs/${runId}/routes/plan`, body)).data,
  addStop: async (runId: string, routeId: string, body: AddStopIn) => (await http.post<Route>(`/runs/${runId}/routes/${routeId}/stops`, body)).data,
  reorder: async (runId: string, routeId: string, stop_ids: string[]) =>
    (await http.patch<Route>(`/runs/${runId}/routes/${routeId}/stops/reorder`, { stop_ids })).data,
  removeStop: async (runId: string, routeId: string, stopId: string, reason: string) => {
    await http.delete(`/runs/${runId}/routes/${routeId}/stops/${stopId}`, { params: { reason } });
  },
  unserve: async (runId: string, deliveryId: string, reason: ReasonCode) =>
    (await http.post<Unserved>(`/runs/${runId}/deliveries/${deliveryId}/unserve`, { reason })).data,
};
