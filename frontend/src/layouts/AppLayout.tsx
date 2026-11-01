import { useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useParams } from 'react-router-dom';

import { P, type Permission } from '@/constants/permissions';
import { ROUTES } from '@/constants/routes';
import { useLogout } from '@/features/auth';
import { useRuns } from '@/features/runs';
import { usePermission } from '@/hooks/usePermission';
import { useAuthStore } from '@/store/auth.store';
import { useRunStore } from '@/store/run.store';

interface NavItem { label: string; to: (runId: string) => string; perm: Permission; runScoped: boolean }
const NAV: NavItem[] = [
  { label: 'Dashboard', to: () => ROUTES.dashboard, perm: P.METRICS_READ, runScoped: false },
  { label: 'Runs', to: () => ROUTES.runs, perm: P.RUNS_READ, runScoped: false },
  { label: 'Sites', to: ROUTES.sites, perm: P.MASTER_READ, runScoped: true },
  { label: 'Vehicles', to: ROUTES.vehicles, perm: P.MASTER_READ, runScoped: true },
  { label: 'Drivers', to: ROUTES.drivers, perm: P.MASTER_READ, runScoped: true },
  { label: 'Orders', to: ROUTES.orders, perm: P.ORDERS_READ, runScoped: true },
  { label: 'Deliveries', to: ROUTES.deliveries, perm: P.ORDERS_READ, runScoped: true },
  { label: 'Routes', to: ROUTES.routes, perm: P.ROUTES_READ, runScoped: true },
  { label: 'Unserved', to: ROUTES.unserved, perm: P.ROUTES_READ, runScoped: true },
  { label: 'Outcomes', to: ROUTES.outcomes, perm: P.OUTCOMES_READ, runScoped: true },
  { label: 'Validation', to: ROUTES.validation, perm: P.VALIDATION_READ, runScoped: true },
  { label: 'Anomalies', to: ROUTES.anomalies, perm: P.ANOMALIES_READ, runScoped: true },
  { label: 'Exports', to: ROUTES.exports, perm: P.EXPORTS_DOWNLOAD, runScoped: true },
  { label: 'Users', to: () => ROUTES.users, perm: P.USERS_MANAGE, runScoped: false },
];

function NavEntry({ item, runId }: { item: NavItem; runId: string | null }) {
  const allowed = usePermission(item.perm);
  if (!allowed || (item.runScoped && !runId)) return null;
  return (
    <NavLink to={item.to(runId ?? '')} end className={({ isActive }) => `block rounded px-3 py-1.5 text-sm ${isActive ? 'bg-blue-50 font-medium text-blue-700' : 'hover:bg-gray-100'}`}>
      {item.label}
    </NavLink>
  );
}

function RunSwitcher() {
  const { runId, setRunId } = useRunStore();
  const navigate = useNavigate();
  const canRead = usePermission(P.RUNS_READ);
  const runs = useRuns({ page_size: 50, sort: '-created_at' });
  if (!canRead) return null;
  return (
    <select className="w-full rounded border px-2 py-1 text-sm" value={runId ?? ''}
      onChange={(e) => { setRunId(e.target.value || null); if (e.target.value) navigate(ROUTES.routes(e.target.value)); }}>
      <option value="">Select run…</option>
      {runs.data?.items.map((r) => <option key={r.id} value={r.id}>{r.name} ({r.status})</option>)}
    </select>
  );
}

export default function AppLayout() {
  const params = useParams();
  const { runId, setRunId } = useRunStore();
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  // URL is the source of truth: /r/:runId/... keeps the switcher in sync on deep links.
  useEffect(() => { if (params.runId && params.runId !== runId) setRunId(params.runId); }, [params.runId, runId, setRunId]);

  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-56 shrink-0 space-y-4 border-r bg-white p-3">
        <p className="px-3 font-semibold">VRPTW Planner</p>
        <RunSwitcher />
        <nav className="space-y-0.5">{NAV.map((n) => <NavEntry key={n.label} item={n} runId={runId} />)}</nav>
        <div className="border-t pt-3 text-xs text-gray-500">
          <p>{user?.name} · {user?.role}</p>
          <button className="mt-1 underline" onClick={() => logout.mutate()}>Sign out</button>
        </div>
      </aside>
      <main className="min-w-0 flex-1 p-6"><Outlet /></main>
    </div>
  );
}
