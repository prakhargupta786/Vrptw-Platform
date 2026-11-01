# VRPTW Delivery Planning Platform

A synthetic-data generator and validation framework for a **Vehicle Routing Problem with Time Windows (VRPTW)**
delivery-planning workflow, with a web platform (API + UI) on top of it.

From a single seed and a set of scale parameters it builds a complete, reproducible delivery dataset (master data,
orders, routes, simulated outcomes), injects labelled anomalies, validates the result, and exports it. Analysts and ML
models can then use it to evaluate **route quality, constraint violations and delivery failures**.

| Default scale | Value |
|---|---|
| Seed | `20261022` |
| Customer sites | 500 |
| Deliveries | 2,000 |
| Vehicles | 100 |
| Days | 30 |
| Region | Delhi/NCR bounding box (lon 77.30–77.45, lat 28.50–28.65) |

A `starter` scale (50 sites, 200 deliveries, 10 vehicles, 3 days) uses the same generator for quick runs.

Developer docs for each part: [backend/README.md](backend/README.md) · [frontend/README.md](frontend/README.md)

---

## Contents

1. [How it works](#1-how-it-works)
2. [Data model](#2-data-model)
3. [Business rules](#3-business-rules)
4. [Anomaly injection](#4-anomaly-injection)
5. [Validation](#5-validation)
6. [Metrics](#6-metrics)
7. [Reproducibility and exports](#7-reproducibility-and-exports)
8. [Users, roles and permissions](#8-users-roles-and-permissions)
9. [Tech stack and project structure](#9-tech-stack-and-project-structure)
10. [Setup and run](#10-setup-and-run)
11. [Seeding data](#11-seeding-data)
12. [Using a cloud database](#12-using-a-cloud-database)
13. [API overview](#13-api-overview)
14. [Implementation status](#14-implementation-status)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. How it works

```
Config (seed, scale)
   │
   ▼
Master data   CustomerSite, Vehicle, VehicleCapacity, Driver, Shift, TravelTimeMatrix
   │
   ▼
Demand        Order → Delivery → TimeWindow
   │
   ▼
Planning      Route → RouteStop          (capacity, shift and time-window rules applied)
   │
   ▼
Simulation    actual arrivals → DeliveryOutcome
   │
   ▼
Anomalies     labelled errors injected → ground_truth.csv
   │
   ▼
Validation → Export → Reproducibility check (2 reruns, SHA-256 compare)
```

- **Input:** a seed and scale parameters.
- **Output:** CSV/JSON/SQL files, ground-truth labels, a data dictionary, a README and a validation report.

All randomness comes from seeded RNG streams (`vrptw_core/rng.py`), so the same seed and scale always produce the same
dataset.

---

## 2. Data model

Every generated table is scoped to a **run** (`run_id` is part of the key), so several datasets can live side by side
in one database.

### A. Master data (generated first)

| Entity | Purpose | Key fields / rules |
|---|---|---|
| **CustomerSite** | Delivery location | `site_id`, lat/lon, region, address type, access restrictions (e.g. truck-size limit). Coordinates lie inside the defined region. |
| **Vehicle** | Fleet vehicle | `VEH-000001`, type (van / truck / mini), status, restricted zones, effective dates. |
| **VehicleCapacity** | Capacity limits per vehicle | Weight (kg), volume (m³), max stops. A separate table because capacity can change over time (effective dates). |
| **Driver** | Driver master | `DRV-000001`, license class, home depot, active status. |
| **Shift** | A driver's duty window | Start/end, break duration, max driving hours. Driver 1:N Shift. |
| **TravelTimeMatrix** | Site-to-site distance and time | Haversine distance; time = distance / speed × traffic factor. Traffic factors cover 30 days of peak / off-peak / disruption scenarios. |

### B. Demand

| Entity | Purpose | Key fields / rules |
|---|---|---|
| **Order** | Customer demand | `ORD-2026-000001`, site FK, quantity, weight, volume, priority, lifecycle (created → planned → completed / cancelled). |
| **Delivery** | Executable delivery task | `DEL-2026-000001`, order FK, service duration, required vehicle type. One Order can have many Deliveries (1:N). |
| **TimeWindow** | Allowed arrival slot | Earliest/latest time, hard/soft type, priority. Includes boundary cases. |

### C. Planning

| Entity | Purpose | Key fields / rules |
|---|---|---|
| **Route** | One vehicle + driver + shift's plan for a day | `RTE-2026-000001`, vehicle/driver/shift FK, total load, total distance, planned duration. Totals are computed from the child stops. |
| **RouteStop** | Ordered stops on a route | `STOP-<route-id>-001`, sequence number, planned arrival/departure, delivery FK. Route 1:N RouteStop. |
| **UnservedDelivery** | Deliveries that could not be assigned | Delivery FK and an explicit reason. |

Delivery ↔ Route is effectively **N:M** over time because of re-planning. RouteStop is the bridge table, and removed
stops are kept, so history is preserved.

### D. Simulation / outcomes

| Entity | Purpose | Key fields / rules |
|---|---|---|
| **DeliveryOutcome** | Actual result of a delivery | Actual arrival/departure, status (delivered / late / failed / skipped), reason code, delay minutes. |

Outcomes are **derived from rules, not random**. An arrival outside the time window becomes `late`. An absent customer
or restricted site access becomes `failed` with a reason code.

### E. Platform tables

| Table | Purpose |
|---|---|
| `users` | Login accounts with a role (and a `supplier_id` for supplier users). |
| `runs`, `jobs` | A generated dataset and the background jobs that act on it (status, step, progress). |
| `entity_events` | Append-only state changes (state changes create new rows; old ones are never overwritten). |
| `ground_truth` | Labels for injected anomalies. |
| `validation_results` | Pass/fail results of the validation checks. |
| `exports` | Generated export bundles. |
| `traffic_factors` | Per-day, per-scenario traffic multipliers used by the travel-time matrix. |

---

## 3. Business rules

These rules are enforced during planning (`vrptw_core/planning/rules.py`) and checked again during validation:

- A route's total load ≤ the vehicle's capacity (weight, volume, max stops).
- A stop's arrival ≥ the previous stop's departure + travel time.
- Arrival falls inside the time window, otherwise the stop is flagged late.
- A route stays inside the driver's shift, otherwise it is flagged shift-exceeded.
- A restricted vehicle never visits a restricted site.
- Every delivery is either assigned to a route or explicitly marked unserved with a reason.
- A failed delivery always has a reason code.
- State changes are stored as new event records; old ones are never overwritten.

---

## 4. Anomaly injection

A **clean baseline** is generated first. A small percentage of rows (default `anomaly_rate = 0.02`) then receive
labelled errors:

| Anomaly | What happens |
|---|---|
| `capacity_exceeded` | Route load exceeds the vehicle limit. |
| `stop_omitted` | A delivery is missing from its route. |
| `stop_duplicated` | A delivery appears twice on a route. |
| `arrival_before_departure` | Time sequence is broken: arrival before the previous stop's departure. |
| `shift_exceeded` | Route runs past the driver's shift end. |
| `coordinate_out_of_region` | A site's lat/lon lies outside the defined region. |

For each anomaly, the `issue_type`, affected ID and expected decision go **only** into `ground_truth.csv`. Nothing
leaks into the input tables, and unrelated rows are not corrupted.

---

## 5. Validation

Automated checks, with results stored in `validation_results` and summarised in `validation_summary` (pass/fail
counts):

1. Primary-key uniqueness
2. Foreign-key integrity (all joins valid)
3. Enum values within their allowed sets
4. Date/time ordering
5. Arithmetic reconciliation (route totals = sum of stop totals)
6. Valid lifecycle transitions
7. Duplicate detection
8. Detected anomalies matched against ground truth

---

## 6. Metrics

- On-time delivery rate
- Failed delivery rate (broken down by reason code)
- Capacity utilisation per vehicle
- Total distance and total travel time
- Average delay minutes
- Unserved delivery count
- Shift utilisation and overtime count
- Anomaly detection precision / recall

---

## 7. Reproducibility and exports

**Reproducibility:** the generator runs twice with the same seed and scale. Row counts and per-file SHA-256 checksums
are compared and must match.

**Export bundle:**

```
/data          CSVs (12 entities) + JSON + SQL seed
/ground_truth  ground_truth.csv
/docs          README, data_dictionary, schema (ERD), source_manifest
/validation    validation_summary
/generator     generate.py + command + seed config
```

The source manifest states that the data is **fully synthetic**: no external or personal data is used.

---

## 8. Users, roles and permissions

There are six roles. Endpoints check **permissions**, never role names (`backend/app/core/permissions.py`).

| Role | What they get | Permissions beyond read access to runs, master data, orders, routes and outcomes |
|---|---|---|
| **ADMIN** | Everything, including user management | All permissions |
| **PLANNER** | Routes and the unserved-delivery list | Edit master data and orders, plan routes; read anomalies, validation and metrics |
| **WAREHOUSE** | Load and stop sequence (route manifests) | None (read-only) |
| **ANALYST** | Metrics and anomaly analysis | Create runs, run validation, read anomalies / validation / metrics / ground truth, download exports |
| **OPS_MANAGER** | KPIs (on-time %, failure %, utilisation) | Read anomalies, validation and metrics; download exports |
| **SUPPLIER** | Order-to-delivery traceability | **Only** reads orders and outcomes, filtered to their own `supplier_id` |

Auth uses a JWT access token (15 min) plus a refresh token in an HTTP-only cookie (7 days).

---

## 9. Tech stack and project structure

| Layer | Stack |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2, Celery |
| Data generation | pandas, numpy (in `vrptw_core`, which has no web/DB dependencies) |
| Database / queue | PostgreSQL 16, Redis 7 |
| Frontend | React 18, Vite, TypeScript, TanStack Query + Table, Zustand, React Hook Form + Zod, Tailwind, Recharts, Leaflet |

```
vrptw-platform/
├── docker-compose.yml          Postgres, Redis (+ optional api/worker containers)
├── VRPTW_Dataset_Overview.pdf  Dataset and module design doc
├── backend/
│   ├── .env.example
│   ├── alembic/                DB migrations
│   ├── app/
│   │   ├── api/v1/endpoints/   Route handlers (auth, runs, master data, demand, planning, ...)
│   │   ├── core/               Settings, security (JWT, hashing), permissions
│   │   ├── models/             SQLAlchemy models (21 tables)
│   │   ├── schemas/            Pydantic request/response models
│   │   ├── services/           Business logic used by the endpoints
│   │   ├── workers/            Celery app and background tasks
│   │   ├── seed.py             Seeds one login user per role
│   │   └── seed_data.py        Generates a full dataset straight into the DB
│   ├── vrptw_core/             Framework-free generator / planner / simulator / validator (+ CLI)
│   └── tests/                  unit + api tests
└── frontend/
    └── src/
        ├── features/           One folder per screen area (runs, planning, metrics, ...)
        ├── components/         UI, tables, charts, map, permission guards
        └── lib/, store/, hooks/
```

Frontend screens: login, dashboard, runs list / new run / run detail, sites, vehicles, drivers, orders (+ detail),
deliveries, routes (+ detail and printable manifest), unserved deliveries, outcomes, anomalies, validation, exports,
and admin user management. Every screen is permission-guarded.

---

## 10. Setup and run

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (frontend only)
- **Docker Desktop** for Postgres and Redis. You don't need to install PostgreSQL itself.

### Step 1: Start Postgres and Redis

From the repo root:

```bash
docker compose up -d db redis
docker compose ps            # db and redis should be "running"
```

This only starts the database and Redis. The `api` and `worker` services in the compose file are for running the
backend in containers too; local development runs them directly instead (steps 4 and 5).

### Step 2: Install the backend

**Windows (PowerShell):**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
```

If PowerShell blocks `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

**macOS / Linux:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Then edit `backend/.env`:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg://vrptw:vrptw@localhost:5432/vrptw` (matches docker-compose). Keep the `+psycopg` part. |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `JWT_SECRET` | A long random string. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CORS_ORIGINS` | `["http://localhost:5173"]` |
| `STORAGE_DIR` | `storage/runs` |

### Step 3: Create the database tables

```bash
alembic upgrade head
```

The initial migration is already in `backend/alembic/versions/`. **Don't run `alembic revision --autogenerate`**
during setup. That command is only for when you change the models.

### Step 4: Seed data

See [Seeding data](#11-seeding-data) below. Short version:

```bash
python -m app.seed                          # login users
python -m app.seed_data --scale starter     # a small dataset
```

### Step 5: Start the API

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

### Step 6: Start the Celery worker (second terminal, optional)

Only needed for jobs started from the API or UI (for example, creating a run from the web).
`seed_data` does **not** need it.

```bash
# Windows: Celery's default pool doesn't work on Windows, so --pool=solo is required
celery -A app.workers.celery_app worker -l info --pool=solo

# macOS / Linux
celery -A app.workers.celery_app worker -l info --concurrency=1
```

### Step 7: Start the frontend (third terminal)

```bash
cd frontend
cp .env.example .env         # Windows: copy .env.example .env
npm install
npm run dev
```

Open http://localhost:5173. In development the Vite server proxies `/api` to `http://localhost:8000`, so leave
`VITE_API_BASE_URL=/api/v1`. For a production build, set it to the full API URL.

### Tests

```bash
cd backend && pytest
cd frontend && npm run typecheck
```

---

## 11. Seeding data

Run the two seed scripts **in this order**, from `backend/` with the virtual environment active.

### 1. Users: `python -m app.seed`

Creates one login user per role:

| Email | Role |
|---|---|
| admin@vrptw.com | ADMIN |
| planner@vrptw.com | PLANNER |
| warehouse@vrptw.com | WAREHOUSE |
| analyst@vrptw.com | ANALYST |
| ops@vrptw.com | OPS_MANAGER |
| supplier@vrptw.com | SUPPLIER (`SUP-001`) |

- Default password: `Password@123`.
- Set your own (min. 8 characters): `python -m app.seed --password "MyStr0ngPass"`.
- Safe to re-run: existing users are skipped and their passwords are **not** reset.

Use a strong password for any database that other people can reach.

### 2. Dataset: `python -m app.seed_data`

Generates a whole run (sites, fleet, drivers, shifts, travel matrix, orders, deliveries, time windows, routes, stops,
unserved deliveries, outcomes, events) straight into the database, without Redis or Celery. It needs an active ADMIN
user, so run step 1 first.

```bash
python -m app.seed_data --scale starter              # 50 sites, 200 deliveries, 10 vehicles, 3 days (fast)
python -m app.seed_data                              # full: 500 sites, 2,000 deliveries, 100 vehicles, 30 days
python -m app.seed_data --name "My run" --seed 42    # custom name and seed
```

It prints the row count per table and the new run ID when it finishes.

Each invocation creates a **new, separate run**. Running it twice gives you two runs, not an update of the first.

### Reset everything

```bash
docker compose down -v       # deletes the Postgres volume and all data
docker compose up -d db redis
alembic upgrade head
python -m app.seed
python -m app.seed_data
```

---

## 12. Using a cloud database

To share the database with teammates, point the backend at a hosted Postgres (for example Neon, Supabase or ClickHouse
Cloud Postgres) instead of the local container.

1. Create the database and copy its connection URL.
2. In `backend/.env`, prefix it with the psycopg driver and require SSL:
   ```
   DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<database>?sslmode=require
   ```
   Use the plain `postgresql://` form only in tools such as psql, DBeaver or pgAdmin.
3. Run `alembic upgrade head`, `python -m app.seed` and `python -m app.seed_data` as in sections 10 and 11. They now
   write to the cloud database.
4. Share a **read-only** user, not the owner account. Run this in the provider's SQL editor, replacing `<database>`:
   ```sql
   CREATE ROLE friend_ro LOGIN PASSWORD 'LongAlphanumericPassword';
   GRANT CONNECT ON DATABASE <database> TO friend_ro;
   GRANT USAGE ON SCHEMA public TO friend_ro;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO friend_ro;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO friend_ro;
   ```
   Keep the password to letters and digits: `@ # : / ? %` break the URL unless they are URL-encoded.

Notes:

- A backend running with the read-only user can log in and show data, but every write fails with a permission
  error: creating runs, editing data, planning and seeding. Anyone who needs those actions needs a user with write
  access.
- If the provider has an IP allow-list, either allow the connecting IPs or allow `0.0.0.0/0`.
- Never commit `.env`. It is already in `.gitignore`.

---

## 13. API overview

The base path is `/api/v1`, and the full interactive reference is at `/docs`. All dataset endpoints are scoped to a run:
`/api/v1/runs/{run_id}/...`.

| Area | Endpoints |
|---|---|
| Health | `GET /health` |
| Auth | `POST /auth/login`, `/auth/refresh`, `/auth/logout`, `GET /auth/me` |
| Users (admin) | `GET`/`POST /users`, `PATCH`/`DELETE /users/{id}` |
| Runs and jobs | `POST`/`GET /runs`, `GET`/`DELETE /runs/{id}`, `POST /runs/{id}/lock`, `POST /runs/{id}/reproduce`, `GET /runs/{id}/reproducibility`, `GET /jobs/{id}` |
| Master data | sites, vehicles (+ capacities), drivers (+ shifts), `travel-matrix`, `travel-matrix/lookup` |
| Demand | orders (+ create, lifecycle `transition`), deliveries, `time-window` update |
| Planning | routes (+ detail, `manifest`), `routes/plan`, add / reorder / remove stops, `unserved`, `deliveries/{id}/unserve` |
| Outcomes | `outcomes` (+ detail), `simulate` |
| Quality | `anomalies/detected`, `ground-truth`, `validation/run`, `validation/summary`, `validation/checks/{name}/failures` |
| Metrics | `metrics/kpis`, `failures-by-reason`, `capacity-utilization`, `shift-utilization`, `anomaly-detection`, `timeseries` |
| Exports and docs | `exports` (create, list, download), `docs/data-dictionary`, `docs/source-manifest`, `events` |

List endpoints are paginated and filterable. For SUPPLIER users, results are automatically limited to their own
supplier's rows.

---

## 14. Implementation status

The platform is a working scaffold. The data pipeline runs end-to-end up to simulation; several later modules are
still stubs that raise `NotImplementedError` (search the code for `NotImplementedError` and `TODO`).

| Area | Status |
|---|---|
| Auth (JWT + refresh cookie), RBAC (6 roles), supplier row-level scoping | ✅ Done |
| 21 DB tables, migration, seed scripts | ✅ Done |
| All 67 API routes registered, with schemas, pagination and filters | ✅ Done |
| Run creation, locking, job tracking, order lifecycle transitions | ✅ Done |
| Generator: master data, demand, route planning, outcome simulation | ✅ Done (`seed_data` and the `generate_run` task work) |
| Frontend: all screens routed and permission-guarded, typed API layer, token refresh, job polling | ✅ Done |
| Anomaly injection (6 types) | ❌ Not implemented: datasets are currently the clean baseline and `ground_truth` is empty |
| Validation checks (all 8) and the `validate_run` task | ❌ Not implemented |
| KPI / metrics queries | ❌ Not implemented: metrics endpoints return 500 |
| Re-planning, re-simulation, reproducibility check, export bundle (Celery tasks) | ❌ Not implemented |
| `vrptw_core.cli` commands (`generate`, `validate`, `reproduce`) | ❌ Not implemented: prints the config, then raises |
| Detail/write endpoints: order trace, create order, delivery detail and stop history, add delivery, update time window, add vehicle capacity, add shift, travel-matrix lookup, route manifest, add/reorder/remove stops, mark unserved | ❌ Not implemented: return 500 |
| Data dictionary generation | ❌ Not implemented |
| Open questions | The real delivery region (currently a Delhi/NCR bounding box) and the full list of failure reason codes still need confirming with the business |

---

## 15. Troubleshooting

| Problem | Cause and fix |
|---|---|
| `connection refused` on port 5432 | Postgres isn't running: run `docker compose up -d db`. For a cloud database, check that the service is running and that your IP is allowed. |
| `No module named 'psycopg2'` | `DATABASE_URL` starts with `postgresql://`. Change it to `postgresql+psycopg://`. |
| `password authentication failed` | Wrong password in the URL, or it contains special characters (`@ # : / ? %`) that need URL-encoding. |
| `relation "users" does not exist` | The migration hasn't run against this database: `alembic upgrade head`. |
| `duplicate key ... "pk_entity_events"` when seeding a second run | The database is missing migration `a3c1e5f0b7d2`: `alembic upgrade head`. |
| `No active ADMIN user` from `seed_data` | Run `python -m app.seed` first. |
| `port is already allocated` on 6379 or 5432 | Another container or local service is using that port. Stop it, or change the host port in `docker-compose.yml` and update `.env` to match. |
| Celery worker hangs or crashes on Windows | Add `--pool=solo`. |
| 500 error from an endpoint | Probably a stub. See [Implementation status](#14-implementation-status). |
| Frontend can't reach the API | Check that the API is on port 8000, `VITE_API_BASE_URL=/api/v1`, and `CORS_ORIGINS` includes the frontend URL. |
