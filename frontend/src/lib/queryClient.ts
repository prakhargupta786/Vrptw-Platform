import { QueryClient } from '@tanstack/react-query';
import type { AxiosError } from 'axios';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (count, err) => {
        const status = (err as AxiosError).response?.status ?? 0;
        return status >= 500 && count < 2; // never retry 4xx
      },
    },
  },
});
