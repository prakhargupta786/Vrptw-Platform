import { http } from '@/lib/http';
import type { DetectedAnomaly, DetectionScore } from '@/types/entities';
import type { AnomalyType } from '@/types/enums';

// Ground truth list uses useRunList(runId, 'ground-truth') — ADMIN/ANALYST only.
export const anomaliesApi = {
  detected: async (runId: string, issue_type?: AnomalyType) =>
    (await http.get<DetectedAnomaly[]>(`/runs/${runId}/anomalies/detected`, { params: issue_type ? { issue_type } : {} })).data,
  scores: async (runId: string) => (await http.get<DetectionScore[]>(`/runs/${runId}/metrics/anomaly-detection`)).data,
};
