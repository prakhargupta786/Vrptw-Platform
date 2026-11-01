export const qk = {
  me: ['me'] as const,
  users: (q?: object) => ['users', q] as const,
  runs: (q?: object) => ['runs', q] as const,
  run: (id: string) => ['runs', id] as const,
  job: (id: string) => ['jobs', id] as const,
  reproducibility: (runId: string) => ['runs', runId, 'reproducibility'] as const,
  list: (runId: string, resource: string, q?: object) => ['runs', runId, resource, q] as const,
  detail: (runId: string, resource: string, id: string) => ['runs', runId, resource, id] as const,
  metrics: (runId: string, name: string, q?: object) => ['runs', runId, 'metrics', name, q] as const,
};
