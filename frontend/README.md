# VRPTW Platform: Frontend

React + TypeScript single-page app for the VRPTW delivery-planning platform. Users log in, pick a generated run, and
browse its master data, orders, routes, outcomes, validation and anomalies. Every screen is permission-guarded
by role.

It talks to the FastAPI backend in [`../backend`](../backend/README.md). For what the data means, see the
[project README](../README.md).

---

## Stack

| Concern | Library |
|---|---|
| UI | React 18, Tailwind CSS 3 |
| Build / dev server | Vite 5, TypeScript 5 (strict) |
| Routing | React Router 6 |
| Server state | TanStack Query 5 |
| Tables | TanStack Table 8 |
| Client state | Zustand (auth session, selected run) |
| Forms | React Hook Form + Zod |
| HTTP | Axios (token injection + automatic refresh) |
| Charts / maps | Recharts, Leaflet + React Leaflet |

Requires **Node.js 18+**.

---

## Setup and run

The backend must be running on `http://localhost:8000` (see the [backend README](../backend/README.md)).

```bash
cd frontend
cp .env.example .env          # Windows: copy .env.example .env
npm install
npm run dev                   # http://localhost:5173
```

Log in with a seeded user, for example `admin@vrptw.com` / `Password@123` (created by `python -m app.seed` in the
backend).

### Environment variables

| Variable | Default | Notes |
|---|---|---|
| `VITE_API_BASE_URL` | `/api/v1` | In development, keep `/api/v1`: the Vite dev server proxies `/api` to `http://localhost:8000` (`vite.config.ts`). For a production build, set the full API URL, e.g. `https://api.example.com/api/v1`. |

`VITE_*` variables are compiled into the bundle at build time, so changing them needs a rebuild. Never put secrets
in them.

### Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Dev server with hot reload on port 5173 |
| `npm run build` | Type-check, then build to `dist/` |
| `npm run preview` | Serve the `dist/` build locally |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run lint` | `eslint src`. **ESLint isn't in `devDependencies` yet**, so install it and add a config before using this script. |

---

## Project structure

```
src/
├── main.tsx              Entry point
├── app/
│   ├── providers.tsx     QueryClient + Router providers
│   └── router.tsx        All routes, wrapped in auth/permission guards
├── layouts/              AppLayout (sidebar + run context), AuthLayout (login)
├── features/             One folder per domain area:
│   ├── auth/             Login, session bootstrap
│   ├── landing/          Public landing page
│   ├── runs/             Runs list, new run, run detail, job progress
│   ├── master-data/      Sites, vehicles, drivers
│   ├── demand/           Orders (+ detail), deliveries
│   ├── planning/         Routes (+ detail, map, printable manifest), unserved deliveries
│   ├── outcomes/         Delivery outcomes
│   ├── validation/       Validation summary and failing rows
│   ├── anomalies/        Detected anomalies vs ground truth
│   ├── metrics/          KPI cards and charts (dashboard)
│   ├── exports/          Export bundles and downloads
│   └── users/            Admin user management
├── components/
│   ├── ui/               Button, Card, Input, Modal, Badge, Spinner
│   ├── data/             DataTable, FilterBar, Pagination, EmptyState
│   ├── charts/           KpiCard, TimeseriesChart
│   ├── map/              RouteMap (Leaflet)
│   └── guards/           RequireAuth, RequirePermission, Can
├── hooks/                usePermission, useJobPolling, usePagination, useRunId
├── lib/                  http (Axios client), queryClient, format helpers
├── store/                auth.store (token + user), run.store (selected run)
├── constants/            ROUTES, permission names, query keys
├── types/                API, entity and enum types matching the backend schemas
└── styles/               Tailwind entry
```

Each feature folder follows the same pattern: `api.ts` (typed endpoint calls), `hooks.ts` (TanStack Query
hooks), `components/`, `pages/`, and an `index.ts` that re-exports the public parts. Import from `src` with the `@/`
alias (for example `@/components/ui`).

---

## Screens

| Path | Screen |
|---|---|
| `/` | Landing |
| `/login` | Login |
| `/dashboard` | KPIs and charts |
| `/runs`, `/runs/new`, `/runs/:runId` | Runs list, create run, run detail and job progress |
| `/r/:runId/sites` · `vehicles` · `drivers` | Master data |
| `/r/:runId/orders` · `orders/:orderId` · `deliveries` | Demand |
| `/r/:runId/routes` · `routes/:routeId` · `routes/:routeId/manifest` · `unserved` | Planning |
| `/r/:runId/outcomes` | Delivery outcomes |
| `/r/:runId/validation` · `anomalies` | Data quality |
| `/r/:runId/exports` | Exports |
| `/admin/users` | User management (ADMIN) |

Run-scoped screens live under `/r/:runId/`, and the selected run is kept in `run.store`.

---

## Auth and permissions

- **Login:** `POST /auth/login` returns an access token, which is kept **in memory** (Zustand), plus an HTTP-only
  refresh cookie.
- **Requests:** the Axios client in `lib/http.ts` adds `Authorization: Bearer <token>` to every request.
- **Refresh:** on a 401, the client calls `/auth/refresh` once, even when several requests fail at the same time,
  then retries the requests. If the refresh fails, the session is cleared and the user goes back to login.
- **After a page reload:** the session is restored from the refresh cookie.
- **Guards:**
  - `RequireAuth` protects all app routes.
  - `RequirePermission` protects whole pages.
  - `<Can perm="...">` hides individual buttons and links.
  - In code, `usePermission(...)` returns whether the user has a permission.
  - Permission names in `constants/permissions.ts` match the backend's `app/core/permissions.py`.

The guards only shape the UI. The backend enforces every permission on its own.

### Roles at a glance

| Role | Sees |
|---|---|
| ADMIN | Everything, including user management |
| PLANNER | Master data and orders (editable), route planning, validation, anomalies, metrics |
| WAREHOUSE | Read-only routes and manifests (load and stop sequence) |
| ANALYST | Runs (create), validation (run), anomalies, ground truth, metrics, exports |
| OPS_MANAGER | KPIs, validation, anomalies, exports |
| SUPPLIER | Only their own orders and outcomes |

---

## Long-running jobs

Creating a run, validating, re-planning, simulating and exporting return a **job ID**. `useJobPolling(jobId)`
polls `GET /jobs/{id}` until the job succeeds or fails. These jobs run on the backend's Celery worker, so the worker
must be running for them to complete.

---

## Production build

```bash
VITE_API_BASE_URL=https://your-api-host/api/v1 npm run build
```

Serve `dist/` from any static host, and route unknown paths to `index.html` (SPA fallback) so deep links work.
On the backend, add the frontend's origin to `CORS_ORIGINS`. The refresh cookie is sent with `withCredentials`,
so the API must allow credentials for that origin.

---

## Known limitations

The UI depends on backend endpoints, and several of them are still stubs that return HTTP 500. The screens that
call them will show an error until the backend logic exists: metrics/KPIs, validation, anomalies, exports, route
manifest, order trace, and stop editing. See the backend README's
[implementation status](../backend/README.md#implementation-status).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Network errors or 404 on `/api/...` in dev | The backend isn't running on port 8000, or `VITE_API_BASE_URL` isn't `/api/v1`. |
| CORS error | Add the frontend's origin to `CORS_ORIGINS` in `backend/.env`, then restart the API. |
| Logged out after every reload | The refresh cookie isn't being set or sent: check that the API and frontend origins are allowed and that you're using the dev proxy. |
| Job stuck in "queued" | The Celery worker isn't running (`--pool=solo` on Windows). |
| Empty lists | No run is seeded yet: run `python -m app.seed_data --scale starter` in the backend. |
