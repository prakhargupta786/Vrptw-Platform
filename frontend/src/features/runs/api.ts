import { clean } from '@/lib/resource';
import { http } from '@/lib/http';
import type { JobAccepted, Paginated, PageQuery } from '@/types/api';
import type { Run, Scale } from '@/types/entities';
import type { AnomalyType, RunStatus } from '@/types/enums';

export interface RunCreate {
  name: string; seed: number; scale: Scale; anomaly_rate: number; anomaly_types: AnomalyType[];
}
export interface FileCompare { name: string; rows_a: number; rows_b: number; sha256_a: string; sha256_b: string; match: boolean }
export interface Reproducibility { match: boolean; files: FileCompare[] }

export const runsApi = {
  list: async (q: PageQuery & { status?: RunStatus; seed?: number } = {}) =>
    (await http.get<Paginated<Run>>('/runs', { params: clean(q) })).data,
  get: async (id: string) => (await http.get<Run>(`/runs/${id}`)).data,
  create: async (body: RunCreate) => (await http.post<JobAccepted>('/runs', body)).data,
  remove: async (id: string) => { await http.delete(`/runs/${id}`); },
  lock: async (id: string) => (await http.post<Run>(`/runs/${id}/lock`)).data,
  reproduce: async (id: string, reruns = 2) => (await http.post<JobAccepted>(`/runs/${id}/reproduce`, { reruns })).data,
  reproducibility: async (id: string) => (await http.get<Reproducibility>(`/runs/${id}/reproducibility`)).data,
};
