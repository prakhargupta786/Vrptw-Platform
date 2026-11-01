import { clean } from '@/lib/resource';
import { http } from '@/lib/http';
import type { Paginated, PageQuery } from '@/types/api';
import type { User } from '@/types/entities';
import type { Role } from '@/types/enums';

export interface UserCreate { email: string; name: string; password: string; role: Role; supplier_id?: string | null }
export type UserUpdate = Partial<Pick<User, 'name' | 'role' | 'is_active' | 'supplier_id'>>;

export const usersApi = {
  list: async (q: PageQuery & { role?: Role; is_active?: boolean } = {}) =>
    (await http.get<Paginated<User>>('/users', { params: clean(q) })).data,
  create: async (body: UserCreate) => (await http.post<User>('/users', body)).data,
  update: async (id: string, body: UserUpdate) => (await http.patch<User>(`/users/${id}`, body)).data,
  deactivate: async (id: string) => { await http.delete(`/users/${id}`); },
};
