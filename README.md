# TBS — Tactical Battlespace Simulator

A VBS4-style military training platform:

- **Web app (Angular)** — scenario planning on a 2D map, instructor control, after-action review
- **API (Django + PostGIS)** — system of record: users/roles, battlespaces, scenarios, sessions, AAR telemetry
- **Runtime (Unreal Engine 5)** — the real-time simulation on a dedicated server

See [`docs/architecture.md`](docs/architecture.md) for the full architecture,
the milestone plan (M0–M6), and the scenario JSON contract shared with UE5.

## Repository layout

| Path | What it is |
|---|---|
| `backend/` | Django 5 + DRF + GeoDjango project (accounts, battlespace, sessions, aar, geo) |
| `frontend/` | Angular 22 SPA (login, planner with MapLibre map, instructor, AAR) |
| `sim/` | Unreal Engine 5.4 project skeleton (C++ module, session handoff client) |
| `schemas/` | Canonical JSON Schemas — the contract between backend and UE5 |
| `infra/` | Deployment notes; `docker-compose.yml` at the root for local dev |
| `docs/` | Architecture and plan documents |

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
# backend   → http://localhost:8000  (API + /admin/)
# frontend  → http://localhost:4200  (proxies /api to backend)
```

Create an admin user:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Quick start (bare metal)

```bash
# Backend (needs Python 3.12; PostGIS for real geo, or use the sqlite test fallback)
cd backend
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
TBS_DB_ENGINE=sqlite TBS_BUNDLED_GIS=1 python manage.py migrate
TBS_DB_ENGINE=sqlite TBS_BUNDLED_GIS=1 python manage.py runserver

# Frontend
cd frontend
npm ci
npm start   # http://localhost:4200
```

> `TBS_DB_ENGINE=sqlite TBS_BUNDLED_GIS=1` runs the backend **without any system
> GIS libraries** (geometry stored as WKT via GEOS from the shapely wheel).
> It is intended for tests/CI only — `contains()`-style spatial queries will not
> work there. Use PostGIS (docker compose) for real development.

## Tests

```bash
# Backend: 14 tests (auth, battlespace CRUD, scenario publish/export validation,
# session lifecycle + UE5 ticket handoff, AAR ingest)
cd backend && TBS_DB_ENGINE=sqlite TBS_BUNDLED_GIS=1 python -m pytest -q

# Frontend
cd frontend && npm run build
```

CI (`.github/workflows/ci.yml`) runs backend lint + tests twice (sqlite fallback
**and** real PostGIS service), the Angular production build, and schema validation.

## UE5 runtime

The `sim/` project is a scaffold: scenario types mirroring `schemas/scenario.schema.json`,
a JSON parser, the session-handoff HTTP client, and a game mode. It has **not been
compiled** here (requires Unreal Engine 5.4 + the Cesium for Unreal plugin).
Build steps and the handoff contract are documented in [`sim/README.md`](sim/README.md).

## Status

Milestone **M0 complete** (verified: backend lint+tests green, frontend builds),
with M1 planning UI mostly in place. Roadmap, team sizing, and risks:
see [`docs/architecture.md`](docs/architecture.md).
