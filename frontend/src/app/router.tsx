import { lazy, Suspense, type ReactNode } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';

import { RequireAuth, RequirePermission } from '@/components/guards';
import { Spinner } from '@/components/ui';
import { P, type Permission } from '@/constants/permissions';
import AppLayout from '@/layouts/AppLayout';
import AuthLayout from '@/layouts/AuthLayout';

// Route-level code splitting: one chunk per page.
const LandingPage = lazy(() => import('@/features/landing/pages/LandingPage'));
const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'));
const DashboardPage = lazy(() => import('@/features/metrics/pages/DashboardPage'));
const RunsListPage = lazy(() => import('@/features/runs/pages/RunsListPage'));
const NewRunPage = lazy(() => import('@/features/runs/pages/NewRunPage'));
const RunDetailPage = lazy(() => import('@/features/runs/pages/RunDetailPage'));
const SitesPage = lazy(() => import('@/features/master-data/pages/SitesPage'));
const VehiclesPage = lazy(() => import('@/features/master-data/pages/VehiclesPage'));
const DriversPage = lazy(() => import('@/features/master-data/pages/DriversPage'));
const OrdersPage = lazy(() => import('@/features/demand/pages/OrdersPage'));
const OrderDetailPage = lazy(() => import('@/features/demand/pages/OrderDetailPage'));
const DeliveriesPage = lazy(() => import('@/features/demand/pages/DeliveriesPage'));
const RoutesPage = lazy(() => import('@/features/planning/pages/RoutesPage'));
const RouteDetailPage = lazy(() => import('@/features/planning/pages/RouteDetailPage'));
const ManifestPage = lazy(() => import('@/features/planning/pages/ManifestPage'));
const UnservedPage = lazy(() => import('@/features/planning/pages/UnservedPage'));
const OutcomesPage = lazy(() => import('@/features/outcomes/pages/OutcomesPage'));
const ValidationSummaryPage = lazy(() => import('@/features/validation/pages/ValidationSummaryPage'));
const AnomaliesPage = lazy(() => import('@/features/anomalies/pages/AnomaliesPage'));
const ExportsPage = lazy(() => import('@/features/exports/pages/ExportsPage'));
const UsersPage = lazy(() => import('@/features/users/pages/UsersPage'));

const page = (el: ReactNode, perm?: Permission) => (
  <Suspense fallback={<Spinner />}>{perm ? <RequirePermission perm={perm}>{el}</RequirePermission> : el}</Suspense>
);

export const router = createBrowserRouter([
  { path: '/', element: page(<LandingPage />) },
  { element: <AuthLayout />, children: [{ path: '/login', element: page(<LoginPage />) }] },
  {
    element: <RequireAuth />,
    children: [{
      element: <AppLayout />,
      children: [
        { path: '/dashboard', element: page(<DashboardPage />, P.METRICS_READ) },
        { path: '/runs', element: page(<RunsListPage />, P.RUNS_READ) },
        { path: '/runs/new', element: page(<NewRunPage />, P.RUNS_CREATE) },
        { path: '/runs/:runId', element: page(<RunDetailPage />, P.RUNS_READ) },
        { path: '/admin/users', element: page(<UsersPage />, P.USERS_MANAGE) },
        {
          path: '/r/:runId',
          children: [
            { path: 'sites', element: page(<SitesPage />, P.MASTER_READ) },
            { path: 'vehicles', element: page(<VehiclesPage />, P.MASTER_READ) },
            { path: 'drivers', element: page(<DriversPage />, P.MASTER_READ) },
            { path: 'orders', element: page(<OrdersPage />, P.ORDERS_READ) },
            { path: 'orders/:orderId', element: page(<OrderDetailPage />, P.ORDERS_READ) },
            { path: 'deliveries', element: page(<DeliveriesPage />, P.ORDERS_READ) },
            { path: 'routes', element: page(<RoutesPage />, P.ROUTES_READ) },
            { path: 'routes/:routeId', element: page(<RouteDetailPage />, P.ROUTES_READ) },
            { path: 'routes/:routeId/manifest', element: page(<ManifestPage />, P.ROUTES_READ) },
            { path: 'unserved', element: page(<UnservedPage />, P.ROUTES_READ) },
            { path: 'outcomes', element: page(<OutcomesPage />, P.OUTCOMES_READ) },
            { path: 'validation', element: page(<ValidationSummaryPage />, P.VALIDATION_READ) },
            { path: 'anomalies', element: page(<AnomaliesPage />, P.ANOMALIES_READ) },
            { path: 'exports', element: page(<ExportsPage />, P.EXPORTS_DOWNLOAD) },
          ],
        },
      ],
    }],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]);
