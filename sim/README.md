# TBS Simulator Runtime (Unreal Engine 5)

The real-time simulation runtime of the Tactical Battlespace Simulator.
Receives a session handoff from the Django backend, loads the canonical
scenario JSON, and runs the training simulation on a dedicated server with
connected clients.

## Status

This is the **M0/M1 scaffold**: module structure, scenario types mirroring
`schemas/scenario.schema.json`, the session handoff client, and a game mode
that parses a fetched scenario. Entity spawning, Cesium georeferenced
terrain, and AI are milestone M2-M3 work (tracked in the repo plan).

> The C++ in this directory was authored against UE 5.4 APIs but has **not
> been compiled** in the scaffold pipeline. Expect the usual first-compile
> fixups (include paths, deprecation warnings) when you open it in the editor.

## Prerequisites

- Unreal Engine 5.4+ (Epic Games Launcher)
- **Cesium for Unreal** plugin (Marketplace, free) - geospatial terrain
- (M4) Agones plugin for Kubernetes game-server hosting

## Running a session locally

The dedicated server expects handoff arguments:

```
UnrealEditor-Cmd TBS.uproject -game -server \
  -TBSSessionTicket=<jwt from POST /api/sessions/{id}/ticket/> \
  -TBSSessionId=<session uuid> \
  -TBSApiBase=http://localhost:8000
```

## Layout

| Path | Purpose |
|---|---|
| `Source/TBS/TBSScenarioTypes.h` | Structs mirroring the scenario schema contract |
| `Source/TBS/TBSScenarioParser.*` | JSON -> scenario structs |
| `Source/TBS/TBSSessionClient.*` | Ticket exchange, scenario fetch, AAR ingest |
| `Source/TBS/TBSGameMode.*` | Server-authoritative session lifecycle |
| `Config/` | Engine/game/input defaults |

**Coordinate systems:** the backend speaks WGS84 (EPSG:4326); UE uses a local
flat frame. All conversion happens through the Cesium georeference - never
scatter manual lat/lon math through gameplay code.
