import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { authApi } from './api';
import { ROUTES } from '@/constants/routes';
import { queryClient } from '@/lib/queryClient';
import { useAuthStore } from '@/store/auth.store';

export function useLogin(redirectTo: string = ROUTES.dashboard) {
  const navigate = useNavigate();
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      setSession(data.access_token, data.user);
      navigate(redirectTo, { replace: true });
    },
  });
}

export function useLogout() {
  const clear = useAuthStore((s) => s.clear);
  return useMutation({
    mutationFn: authApi.logout,
    onSettled: () => {
      clear();
      queryClient.clear();
    },
  });
}
