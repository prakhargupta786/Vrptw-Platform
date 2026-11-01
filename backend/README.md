# VRPTW Platform: Backend

FastAPI + SQLAlchemy 2 + Celery API for the VRPTW synthetic-dataset platform. It generates delivery-planning datasets
into PostgreSQL and serves them, scoped by run and filtered by role.

For what the dataset contains and why (entities, business rules, anomalies, validation, metrics), see the
[project README](../README.md) and `VRPTW_Dataset_Overview.pdf`.

---

## Stack

| Concern | Library |
|---|---|
| API | FastAPI, Uvicorn |
| ORM / migrations | SQLAlchemy 2, Alembic |
| Database driver | psycopg 3 (`postgresql+psycopg://`) |
| Validation / settings | Pydantic 2, pydantic-settings |
| Auth | PyJWT (access token), HTTP-only refresh cookie, passlib + bcrypt |
| Background jobs | Celery with Redis as broker and result backend |
| Data generation | pandas, numpy |
| Tests / lint | pytest, httpx, ruff |

Requires **Python 3.11+**, **PostgreSQL 16** and **Redis 7**.

---

## Layout

```
backend/
├── alembic/versions/      Migrations (run `alembic upgrade head`)
├── app/
│   ├── main.py            FastAPI app factory, CORS, error handlers
│   ├── api/
│   │   ├── deps.py        DB session, current user, require_permission(), get_run / writable_run, paging, supplier_scope
│   │   └── v1/endpoints/  auth, users, runs, master_data, demand, planning, outcomes, quality, metrics, exports, health
│   ├── core/
│   │   ├── config.py      Settings read from .env
│   │   ├── security.py    Password hashing, JWT encode/decode
│   │   └── permissions.py Role → permission map (endpoints check permissions, never role names)
│   ├── db/                Declarative base (constraint naming convention), session factory
│   ├── models/            21 tables; run-scoped tables use composite keys (run_id, <id>)
│   ├── schemas/           Pydantic request/response models
│   ├── repositories/      Shared query helpers (pagination, filters)
│   ├── services/          Business logic: generation, runs, orders, planning, metrics
│   ├── workers/           Celery app + tasks (generate, validate, plan, simulate, reproduce, export)
│   ├── seed.py            One login user per role
│   └── seed_data.py       Full dataset generation straight into the DB
├── vrptw_core/            Framework-free pipeline (no FastAPI/SQLAlchemy imports)
│   ├── config.py          RunConfig (seed, scale, anomaly rate, region polygon)
│   ├── rng.py             Seeded RNG streams, so output is reproducible
│   ├── generators/        Master data and demand
│   ├── planning/          Route planner + rule checks (capacity, time windows, shifts, restrictions)
│   ├── simulation/        Rule-based outcomes (delivered / late / failed / skipped)
│   ├── anomalies/         Labelled anomaly injection (stub)
│   ├── validation/        The 8 validation checks (stub)
│   ├── metrics/           KPI computation (stub)
│   ├── export/            Writers, SHA-256 checksums, data dictionary
│   ├── pipeline.py        generate(cfg) -> {"tables": {...}, "ground_truth": df}
│   └── cli.py             `python -m vrptw_core.cli ...` (stub)
├── tests/                 unit/ (geo, rules) and api/ tests
├── storage/runs/          Export output (git-ignored)
├── Dockerfile
└── pyproject.toml
```

### How the layers fit together

- **`vrptw_core`** builds pandas DataFrames from a `RunConfig` and knows nothing about the web app or the database.
- **`services/generation_service.generate_into()`** runs the pipeline and bulk-inserts each table tagged with the run's
  `run_id`, in parent-before-child order (`LOAD_ORDER`) so composite foreign keys resolve.
- **Endpoints** stay thin: they check permissions, load the run, and call a service or repository.

---

## Setup

Run these from `backend/`. Postgres and Redis come from the repo-root `docker-compose.yml`.

```bash
# from the repo root
docker compose up -d db redis
cd backend
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -e ".[dev]"
copy .env.example .env
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### Environment variables (`.env`)

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://vrptw:vrptw@localhost:5432/vrptw` | Must use the `postgresql+psycopg://` prefix. Add `?sslmode=require` for cloud databases. |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker and result backend. |
| `JWT_SECRET` | `change-me` | **Set a long random value:** `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ACCESS_TOKEN_MINUTES` | `15` | Access-token lifetime. |
| `REFRESH_TOKEN_DAYS` | `7` | Refresh-cookie lifetime. |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | JSON list of allowed frontend origins. |
| `STORAGE_DIR` | `storage/runs` | Where exports are written. |

`.env` is git-ignored; never commit it.

### Database

```bash
alembic upgrade head
```

Run this again after every `git pull`: migrations are committed in `alembic/versions/`.

When you change a model, create a new migration, review the generated file, and apply it:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
alembic check            # passes when the models and the database match
```

---

## Seeding

Run the two scripts in this order.

```bash
python -m app.seed                               # 6 users, one per role, password Password@123
python -m app.seed --password "MyStr0ngPass"     # or choose the password (min. 8 chars)

python -m app.seed_data --scale starter          # 50 sites, 200 deliveries, 10 vehicles, 3 days (seconds)
python -m app.seed_data                          # 500 sites, 2,000 deliveries, 100 vehicles, 30 days
python -m app.seed_data --name "My run" --seed 42
```

| Email | Role |
|---|---|
| admin@vrptw.com | ADMIN |
| planner@vrptw.com | PLANNER |
| warehouse@vrptw.com | WAREHOUSE |
| analyst@vrptw.com | ANALYST |
| ops@vrptw.com | OPS_MANAGER |
| supplier@vrptw.com | SUPPLIER (`SUP-001`) |

- `app.seed` is idempotent: it skips existing emails and never resets their passwords.
- `app.seed_data` writes directly to the database (no Redis or Celery needed) and requires an active ADMIN user.
  **Each invocation creates a new run**, and several runs can coexist because every key includes `run_id`.

On a full-scale run, the largest table is `travel_time_matrix` (~250k rows). Over a remote cloud database the seed
takes about 3 minutes; locally it is much faster.

---

## Running

```bash
uvicorn app.main:app --reload                    # http://localhost:8000/docs
```

The Celery worker is only needed for jobs started through the API (`POST /runs`, validate, export, ...):

```bash
celery -A app.workers.celery_app worker -l info --pool=solo          # Windows
celery -A app.workers.celery_app worker -l info --concurrency=1      # macOS / Linux
```

### Docker (optional)

`docker compose up -d` from the repo root also builds and starts the `api` and `worker` containers. They read
`backend/.env`, with `DATABASE_URL` and `REDIS_URL` overridden to point at the compose services. Run migrations
inside the container:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m app.seed
```

---

## API conventions

- **Base path:** `/api/v1`. OpenAPI JSON is served at `/api/v1/openapi.json`, Swagger UI at `/docs`.
- **Auth:** `POST /auth/login` returns an access token in the response body and sets an HTTP-only refresh cookie.
  Send `Authorization: Bearer <token>`; call `POST /auth/refresh` to get a new token.
- **Run scoping:** dataset endpoints live under `/runs/{run_id}/...`.
- **Permissions:** every endpoint declares `Depends(require_permission(P.X))`. To change access, edit
  `ROLE_PERMISSIONS` in `app/core/permissions.py`; do not check role names in endpoints.
- **Supplier scoping:** SUPPLIER users only see rows for their own `supplier_id`. Endpoints that return orders or
  outcomes must filter with `supplier_scope(user)` from `deps.py`; it returns `None` for every other role.
- **Locked runs:** write endpoints take the `writable_run` dependency, which returns 409 `RUN_LOCKED` on a locked run.
- **Errors** share one shape: `{"error": {"code": "...", "message": "..."}}`.
- **Events:** state changes append `entity_events` rows; existing rows are never updated.

---

## Tests

```bash
pytest
ruff check .
```

---

## Implementation status

| Done | Still a stub (`NotImplementedError`) |
|---|---|
| Auth, RBAC, supplier scoping, users CRUD | Anomaly injector (`vrptw_core/anomalies`): ground truth is empty |
| Runs, jobs, run locking, order lifecycle transitions | 8 validation checks + `validate_run` task |
| Generator: master data, demand, planning, simulation | KPI queries (`metrics_service`, `vrptw_core/metrics`) |
| `generate_run` Celery task, seed scripts | Celery tasks: re-plan, simulate, reproducibility check, export |
| List endpoints with pagination and filters | `vrptw_core.cli` commands, data dictionary |
| | Write/detail endpoints: order trace, create order, delivery detail, add delivery, update time window, add capacity, add shift, travel-matrix lookup, route manifest, stop add/reorder/remove, mark unserved |

Search for `NotImplementedError` and `TODO` to find each one. An endpoint that is still a stub returns HTTP 500.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `No module named 'psycopg2'` | `DATABASE_URL` must start with `postgresql+psycopg://`. |
| `connection refused` on port 5432 | Start Postgres (`docker compose up -d db`). For a cloud database, check that the service is running and your IP is allowed. |
| `relation "..." does not exist` | Run `alembic upgrade head`. |
| `duplicate key value violates unique constraint "pk_entity_events"` | The database is missing migration `a3c1e5f0b7d2`. Run `alembic upgrade head`. |
| `No active ADMIN user` | Run `python -m app.seed` first. |
| Celery worker hangs on Windows | Add `--pool=solo`. |
| `ValueError` from bcrypt when hashing | Keep `bcrypt<4.1` (pinned in `pyproject.toml`; passlib 1.7.4 breaks on newer versions). |
