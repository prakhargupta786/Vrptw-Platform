import { keepPreviousData, useQuery } from '@tanstack/react-query';

import { qk } from '@/constants/queryKeys';
import { http } from './http';
import type { PageQuery, Paginated } from '@/types/api';

type Query = PageQuery & Record<string, string | number | boolean | undefined>;

/** Strips undefined/empty so they don't reach the API as "?status=". */
export const clean = (q: object) => Object.fromEntries(Object.entries(q).filter(([, v]) => v !== undefined && v !== ''));

export async function listRunResource<T>(runId: string, resource: string, q: Query = {}) {
  return (await http.get<Paginated<T>>(`/runs/${runId}/${resource}`, { params: clean(q) })).data;
}

export async function getRunResource<T>(runId: string, resource: string, id: string) {
  return (await http.get<T>(`/runs/${runId}/${resource}/${id}`)).data;
}

/** Generic paginated list for any run-scoped resource (sites, vehicles, orders, routes, …). */
export function useRunList<T>(runId: string, resource: string, q: Query = {}) {
  return useQuery({
    queryKey: qk.list(runId, resource, q),
    queryFn: () => listRunResource<T>(runId, resource, q),
    placeholderData: keepPreviousData,
  });
}

export function useRunDetail<T>(runId: string, resource: string, id: string | undefined) {
  return useQuery({
    queryKey: qk.detail(runId, resource, id ?? ''),
    queryFn: () => getRunResource<T>(runId, resource, id!),
    enabled: !!id,
  });
}
