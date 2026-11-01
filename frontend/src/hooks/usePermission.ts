import type { Permission } from '@/constants/permissions';
import { useAuthStore } from '@/store/auth.store';

export function usePermission(...perms: Permission[]): boolean {
  const granted = useAuthStore((s) => s.user?.permissions);
  return !!granted && perms.every((p) => granted.includes(p));
}
