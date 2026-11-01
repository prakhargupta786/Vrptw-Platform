import type { ReactNode } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';

import type { Permission } from '@/constants/permissions';
import { ROUTES } from '@/constants/routes';
import { usePermission } from '@/hooks/usePermission';
import { useAuthStore } from '@/store/auth.store';

export function RequireAuth() {
  const user = useAuthStore((s) => s.user);
  const location = useLocation();
  return user ? <Outlet /> : <Navigate to={ROUTES.login} replace state={{ from: location }} />;
}

export function RequirePermission({ perm, children }: { perm: Permission; children: ReactNode }) {
  return usePermission(perm) ? <>{children}</> : <p className="p-6 text-sm text-gray-500">You don't have access to this page.</p>;
}

/** Hides children without the permission. Cosmetic only. */
export function Can({ perm, children }: { perm: Permission; children: ReactNode }) {
  return usePermission(perm) ? <>{children}</> : null;
}
