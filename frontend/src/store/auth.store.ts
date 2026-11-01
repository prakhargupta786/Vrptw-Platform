import { create } from 'zustand';

import type { Me } from '@/types/entities';

interface AuthState {
  accessToken: string | null; // memory only: never persisted to localStorage (XSS exposure)
  user: Me | null;
  setSession: (token: string, user: Me) => void;
  setToken: (token: string) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setSession: (accessToken, user) => set({ accessToken, user }),
  setToken: (accessToken) => set({ accessToken }),
  clear: () => set({ accessToken: null, user: null }),
}));
