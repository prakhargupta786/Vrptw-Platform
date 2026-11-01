import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { usersApi, type UserCreate } from './api';
import { qk } from '@/constants/queryKeys';

export const useUsers = (q: Parameters<typeof usersApi.list>[0] = {}) =>
  useQuery({ queryKey: qk.users(q), queryFn: () => usersApi.list(q) });

export function useCreateUser() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (b: UserCreate) => usersApi.create(b), onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }) });
}

export function useDeactivateUser() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: usersApi.deactivate, onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }) });
}
