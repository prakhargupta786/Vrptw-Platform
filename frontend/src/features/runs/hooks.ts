import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { runsApi, type RunCreate } from './api';
import { qk } from '@/constants/queryKeys';

export const useRuns = (q: Parameters<typeof runsApi.list>[0] = {}) =>
  useQuery({ queryKey: qk.runs(q), queryFn: () => runsApi.list(q) });

export const useRun = (id: string) =>
  useQuery({
    queryKey: qk.run(id),
    queryFn: () => runsApi.get(id),
    // keep refreshing while the run is still being built
    refetchInterval: (q) => (q.state.data && ['queued', 'generating', 'validating'].includes(q.state.data.status) ? 3000 : false),
  });

export const useReproducibility = (id: string, enabled: boolean) =>
  useQuery({ queryKey: qk.reproducibility(id), queryFn: () => runsApi.reproducibility(id), enabled, retry: false });

export function useCreateRun() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (b: RunCreate) => runsApi.create(b), onSuccess: () => qc.invalidateQueries({ queryKey: ['runs'] }) });
}

export function useLockRun(id: string) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: () => runsApi.lock(id), onSuccess: (run) => qc.setQueryData(qk.run(id), run) });
}

export function useReproduce(id: string) {
  return useMutation({ mutationFn: () => runsApi.reproduce(id) });
}
