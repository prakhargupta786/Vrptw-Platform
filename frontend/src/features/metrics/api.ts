import { clean } from '@/lib/resource';
import { http } from '@/lib/http';
import type { Kpis } from '@/types/entities';
import type { ReasonCode } from '@/types/enums';

export interface ReasonShare { reason_code: ReasonCode; count: number; share: number }
export interface VehicleUtilization { vehicle_id: string; weight_pct: number; volume_pct: number; stops_pct: number }
export interface ShiftUtilization { driver_id: string; used_hours: number; available_hours: number; overtime_minutes: number }
export interface Point { bucket: string; value: number }
type Range = { date_from?: string; date_to?: string };

const base = (runId: string) => `/runs/${runId}/metrics`;
export const metricsApi = {
  kpis: async (runId: string, q: Range & { vehicle_id?: string } = {}) => (await http.get<Kpis>(`${base(runId)}/kpis`, { params: clean(q) })).data,
  failuresByReason: async (runId: string, q: Range = {}) => (await http.get<ReasonShare[]>(`${base(runId)}/failures-by-reason`, { params: clean(q) })).data,
  capacity: async (runId: string, on?: string) => (await http.get<VehicleUtilization[]>(`${base(runId)}/capacity-utilization`, { params: clean({ on }) })).data,
  shifts: async (runId: string, on?: string) => (await http.get<ShiftUtilization[]>(`${base(runId)}/shift-utilization`, { params: clean({ on }) })).data,
  timeseries: async (runId: string, metric: string, granularity: 'day' | 'week' = 'day') =>
    (await http.get<Point[]>(`${base(runId)}/timeseries`, { params: { metric, granularity } })).data,
};
