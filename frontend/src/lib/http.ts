import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

import { env } from '@/config/env';
import { useAuthStore } from '@/store/auth.store';
import type { ApiError } from '@/types/api';
import type { Me } from '@/types/entities';

export const http = axios.create({ baseURL: env.apiBaseUrl, withCredentials: true });

http.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Single in-flight refresh shared by all requests that 401 at the same time.
let refreshing: Promise<string | null> | null = null;

export async function refreshAccessToken(): Promise<string | null> {
  refreshing ??= axios
    .post<{ access_token: string; user: Me }>(`${env.apiBaseUrl}/auth/refresh`, null, { withCredentials: true })
    .then(({ data }) => {
      useAuthStore.getState().setSession(data.access_token, data.user);
      return data.access_token;
    })
    .catch(() => {
      useAuthStore.getState().clear();
      return null;
    })
    .finally(() => {
      refreshing = null;
    });
  return refreshing;
}

http.interceptors.response.use(
  (res) => res,
  async (error: AxiosError<ApiError>) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined;
    const isAuthCall = original?.url?.startsWith('/auth/');
    if (error.response?.status === 401 && original && !original._retried && !isAuthCall) {
      original._retried = true;
      const token = await refreshAccessToken();
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return http(original);
      }
    }
    return Promise.reject(error);
  },
);

export function errorMessage(err: unknown): string {
  const e = err as AxiosError<ApiError>;
  return e.response?.data?.error?.message ?? e.message ?? 'Something went wrong';
}
