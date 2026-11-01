export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  error: { code: string; message: string; details: Record<string, unknown> };
}

export interface JobAccepted {
  job_id: string;
  run_id?: string;
  status: 'queued';
}

export interface PageQuery {
  page?: number;
  page_size?: number;
  sort?: string;
}
