import { useQuery } from '@tanstack/react-query';

import { qk } from '@/constants/queryKeys';
import { http } from '@/lib/http';
import type { Job } from '@/types/entities';

/** Polls GET /jobs/{id} every 2s until the job succeeds or fails. */
export function useJobPolling(jobId: string | null) {
  return useQuery({
    queryKey: qk.job(jobId ?? ''),
    queryFn: async () => (await http.get<Job>(`/jobs/${jobId}`)).data,
    enabled: !!jobId,
    refetchInterval: (q) => (q.state.data && ['succeeded', 'failed'].includes(q.state.data.status) ? false : 2000),
  });
}
