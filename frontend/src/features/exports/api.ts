import { env } from '@/config/env';
import { http } from '@/lib/http';
import type { JobAccepted } from '@/types/api';
import type { Export } from '@/types/entities';

export type ExportPart = 'data' | 'ground_truth' | 'docs' | 'validation' | 'generator';

export const exportsApi = {
  list: async (runId: string) => (await http.get<Export[]>(`/runs/${runId}/exports`)).data,
  create: async (runId: string, formats: string[] = ['csv', 'json', 'sql'], include?: ExportPart[]) =>
    (await http.post<JobAccepted>(`/runs/${runId}/exports`, { formats, ...(include ? { include } : {}) })).data,
  /** Fetch as blob so the bearer header is sent (a plain <a href> would not carry it). */
  download: async (runId: string, exportId: string) => {
    const res = await http.get<Blob>(`/runs/${runId}/exports/${exportId}/download`, { responseType: 'blob' });
    const url = URL.createObjectURL(res.data);
    const a = Object.assign(document.createElement('a'), { href: url, download: `vrptw_${runId}_${exportId}.zip` });
    a.click();
    URL.revokeObjectURL(url);
  },
  dataDictionary: async (runId: string) => (await http.get(`/runs/${runId}/docs/data-dictionary`)).data,
  baseUrl: env.apiBaseUrl,
};
