"""Assemble the canonical scenario export (schemas/scenario.schema.json)."""
import json
from datetime import UTC, datetime
from pathlib import Path

import jsonschema
from django.conf import settings


def _point_ll(lon, lat, alt=0.0):
    return {"lat": lat, "lon": lon, "alt": alt}


def scenario_to_dict(scenario) -> dict:
    bs = scenario.battlespace
    env = scenario.environment or {}
    entities = []
    for e in scenario.entities.all():
        entities.append({
            "id": e.client_id,
            "kind": e.kind,
            "side": e.side,
            "position": {
                "lat": e.position.y, "lon": e.position.x,
                "alt": e.position.z or 0.0,
            },
            "headingDeg": e.heading_deg,
            "composition": e.composition or {},
            "waypoints": e.waypoints or [],
        })
    objectives = []
    for o in scenario.objectives.all():
        objectives.append({
            "id": o.client_id,
            "description": o.description,
            "points": o.points,
            "trigger": o.trigger,
        })
    minx, miny, maxx, maxy = bs.aoi.extent  # (xmin, ymin, xmax, ymax)
    doc = {
        "schemaVersion": "0.1.0",
        "meta": {
            "name": scenario.name,
            "author": bs.created_by.username if bs.created_by_id else "system",
            "createdAt": datetime.now(UTC).isoformat(),
            "description": bs.description,
        },
        "terrain": {
            "bbox": [minx, miny, maxx, maxy],
            "epsg": 4326,
            "source": bs.terrain_source or {"provider": "local-tiles"},
        },
        "environment": {
            "timeOfDay": env.get("timeOfDay", "12:00"),
            "weather": env.get("weather", "clear"),
            "fogDensity": env.get("fogDensity", 0.0),
            "windSpeedMs": env.get("windSpeedMs", 0.0),
            "windDirectionDeg": env.get("windDirectionDeg", 0.0),
        },
        "entities": entities,
        "objectives": objectives,
    }
    return doc


def validate_scenario_dict(doc: dict) -> list[str]:
    """Validate against the shared schema; returns a list of error strings."""
    schema_path = Path(settings.TBS_SCHEMA_DIR) / "scenario.schema.json"
    if not schema_path.exists():
        return [f"schema file missing: {schema_path}"]
    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in validator.iter_errors(doc)]


def export_and_validate(scenario) -> tuple[dict, list[str]]:
    doc = scenario_to_dict(scenario)
    errors = validate_scenario_dict(doc)
    return doc, errors
