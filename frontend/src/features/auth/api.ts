import { http } from '@/lib/http';
import type { Me } from '@/types/entities';

export interface LoginPayload { email: string; password: string }
export interface TokenResponse { access_token: string; token_type: 'bearer'; expires_in: number; user: Me }

export const authApi = {
  login: async (body: LoginPayload) => (await http.post<TokenResponse>('/auth/login', body)).data,
  logout: async () => { await http.post('/auth/logout'); },
  me: async () => (await http.get<Me>('/auth/me')).data,
};
