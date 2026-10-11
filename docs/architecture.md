# Architecture

## System diagram

```
 Angular SPA ──HTTPS/WSS──► Django (DRF + Channels) ──► PostgreSQL + PostGIS
 planner / instructor / AAR      │ scenario service      TimescaleDB (telemetry)
                                 │ session service       Redis (cache/broker/celery)
                                 │ AAR service           MinIO (assets/replays)
                                 │
                         session handoff (signed JWT ticket, 60s TTL)
                                 │
                                 ▼
                     UE5 dedicated server (Agones on K8s) ◄──► UE5 clients
                     Cesium for Unreal terrain, netcode, AI   (trainees, spectate)
```

**Golden rule:** Django is the *system of record*; UE5 owns *real-time state*.
They meet at exactly two seams:

1. **Handoff** — `POST /api/sessions/{id}/ticket/` returns a short-lived JWT.
   The dedicated server starts with `-TBSSessionTicket=... -TBSApiBase=...`,
   exchanges it, and downloads `GET /api/scenarios/{id}/export/`.
2. **Telemetry** — the server batches AAR events to
   `POST /api/sessions/{id}/aar/ingest/` (schema: `schemas/aar-event.schema.json`).

## Scenario contract

`schemas/scenario.schema.json` (SemVer `schemaVersion`) is the single source of
truth. The backend validates with `jsonschema` on **publish**; the UE5 parser
mirrors it in `sim/Source/TBS/TBSScenarioTypes.h`. Any contract change updates
the schema first, then both sides, then bumps the minor version.

## Coordinate systems

- Storage/API: **WGS84 (EPSG:4326)**, GeoJSON on the wire (`Polygon` AOI, `Point` entities).
- Web map: MapLibre (Web Mercator internally, WGS84 API).
- UE5: flat local frame; conversion **only** through the Cesium georeference.
  Milestone M2 spikes this with a shared test fixture of known lat/lon points.

## Milestones

| # | Deliverable | Exit criteria |
|---|---|---|
| M0 | Foundations | monorepo, CI, auth, schema files — **DONE** |
| M1 | Geo + planning | AOI + entity/waypoint editing, publish flow (UI largely present) |
| M2 | UE5 geo spike | Cesium terrain from same bbox; <1 m coord agreement |
| M3 | Sim runtime | dedicated server loads scenario, squad AI, FP player |
| M4 | Session handoff | launch → Agones → ticket → clients join, zero manual steps |
| M5 | Instructor + AAR | pause/inject/spectate; telemetry replay on the 2D map |
| M6 | Hardening | load tests, security review, packaging |

## API surface (v0.1)

```
POST   /api/auth/token/               JWT obtain            (public)
POST   /api/auth/register/            self-registration     (public, role=trainee)
GET    /api/auth/me/                  profile
GET/POST /api/battlespaces/           CRUD (staff only)
GET/POST /api/scenarios/              CRUD; ?battlespace= filter
POST   /api/scenarios/{id}/publish/   schema-validate + freeze + version
POST   /api/scenarios/{id}/validate/  dry-run validation
GET    /api/scenarios/{id}/export/    canonical JSON for UE5
POST   /api/scenario-entities/        place entities (staff only)
GET/POST /api/sessions/               launch sessions
POST   /api/sessions/{id}/start|pause|resume|end/
POST   /api/sessions/{id}/ticket/     UE5 handoff ticket
POST   /api/sessions/{id}/aar/ingest/ batched telemetry from the sim server
GET    /api/aar-events/?session=      replay timeline
POST   /api/battlespaces/{id}/terrain/ enqueue terrain tile build (placeholder)
```

## Security notes (scaffold → production checklist)

- JWT bearer tokens in localStorage are **scaffold-only**; move to httpOnly
  cookies or short-lived access + rotating refresh before real deployments.
- Ticket endpoint must move to service credentials (not user JWT) in M4.
- Org scoping exists on battlespaces/scenarios; verify every new queryset filters it.
- `isSameOrigin`/CSRF hardening and rate limiting are pending (M6).
