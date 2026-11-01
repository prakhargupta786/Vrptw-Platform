import { http } from '@/lib/http';
import type { JobAccepted, Paginated } from '@/types/api';
import type { ValidationSummary } from '@/types/entities';
import type { ValidationCheck } from '@/types/enums';

export const validationApi = {
  run: async (runId: string, checks?: ValidationCheck[]) =>
    (await http.post<JobAccepted>(`/runs/${runId}/validation/run`, checks ? { checks } : {})).data,
  summary: async (runId: string) => (await http.get<ValidationSummary>(`/runs/${runId}/validation/summary`)).data,
  failures: async (runId: string, check: ValidationCheck, page = 1) =>
    (await http.get<Paginated<string>>(`/runs/${runId}/validation/checks/${check}/failures`, { params: { page } })).data,
};
