// Mirrors backend app/core/permissions.py. UI hiding only; the API enforces.
export const P = {
  USERS_MANAGE: 'users:manage',
  RUNS_CREATE: 'runs:create',
  RUNS_RERUN: 'runs:rerun',
  RUNS_DELETE: 'runs:delete',
  RUNS_LOCK: 'runs:lock',
  RUNS_READ: 'runs:read',
  MASTER_READ: 'master:read',
  MASTER_WRITE: 'master:write',
  ORDERS_READ: 'orders:read',
  ORDERS_WRITE: 'orders:write',
  ROUTES_READ: 'routes:read',
  ROUTES_PLAN: 'routes:plan',
  OUTCOMES_READ: 'outcomes:read',
  ANOMALIES_READ: 'anomalies:read',
  VALIDATION_READ: 'validation:read',
  VALIDATION_RUN: 'validation:run',
  METRICS_READ: 'metrics:read',
  EXPORTS_DOWNLOAD: 'exports:download',
  GROUND_TRUTH_READ: 'ground_truth:read',
} as const;
export type Permission = (typeof P)[keyof typeof P];
