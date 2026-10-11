import json

from django.contrib.gis.geos import Polygon
from rest_framework import serializers

from .models import Battlespace, EntitySide, Objective, Scenario, ScenarioEntity

ENTITY_KINDS = {"infantry-soldier", "infantry-squad", "team", "spawn-point", "marker"}
WAYPOINT_ACTIONS = {"move", "jog", "overwatch", "hold", "engage"}
TRIGGER_TYPES = {"area-clear", "reach-area", "time-limit", "eliminate-entity"}


def geojson_to_geom(value):
    """Accept either a GeoJSON geometry dict or a WKT string -> GEOS geometry."""
    if isinstance(value, str):
        from django.contrib.gis.geos import GEOSGeometry
        return GEOSGeometry(value)
    if isinstance(value, dict) and value.get("type"):
        import json as _json

        from django.contrib.gis.geos import GEOSGeometry
        return GEOSGeometry(_json.dumps(value))
    raise serializers.ValidationError("Expected a GeoJSON geometry object or WKT string.")


class BattlespaceSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.username")
    aoi = serializers.JSONField()  # GeoJSON polygon in, GeoJSON out

    class Meta:
        model = Battlespace
        fields = ["id", "name", "description", "organization", "created_by",
                  "aoi", "terrain_source", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_aoi(self, value):
        geom = geojson_to_geom(value)
        if not isinstance(geom, Polygon):
            raise serializers.ValidationError("AOI must be a Polygon.")
        if geom.srid is None:
            geom.srid = 4326
        return geom

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["aoi"] = json.loads(instance.aoi.geojson) if instance.aoi else None
        return rep


class ScenarioEntitySerializer(serializers.ModelSerializer):
    position = serializers.JSONField()

    class Meta:
        model = ScenarioEntity
        fields = ["id", "client_id", "kind", "side", "position",
                  "heading_deg", "composition", "waypoints"]
        read_only_fields = ["id"]

    def validate_kind(self, value):
        if value not in ENTITY_KINDS:
            raise serializers.ValidationError(f"kind must be one of {sorted(ENTITY_KINDS)}")
        return value

    def validate_side(self, value):
        if value not in EntitySide.values:
            raise serializers.ValidationError(f"side must be one of {EntitySide.values}")
        return value

    def validate_position(self, value):
        geom = geojson_to_geom(value)
        if geom.srid is None:
            geom.srid = 4326
        return geom

    def validate_waypoints(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("waypoints must be a list.")
        for i, wp in enumerate(value):
            if not isinstance(wp, dict) or "lat" not in wp or "lon" not in wp:
                raise serializers.ValidationError(f"waypoints[{i}] needs lat and lon.")
            action = wp.get("action")
            if action is not None and action not in WAYPOINT_ACTIONS:
                raise serializers.ValidationError(
                    f"waypoints[{i}].action must be one of {sorted(WAYPOINT_ACTIONS)}")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["position"] = json.loads(instance.position.geojson) if instance.position else None
        return rep

    def create(self, validated_data):
        if "client_id" not in validated_data:
            scenario = validated_data["scenario"]
            n = scenario.entities.count() + 1
            validated_data["client_id"] = f"ent-{n}"
        return super().create(validated_data)


class ObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objective
        fields = ["id", "client_id", "description", "points", "trigger"]
        read_only_fields = ["id"]

    def validate_trigger(self, value):
        if not isinstance(value, dict) or value.get("type") not in TRIGGER_TYPES:
            raise serializers.ValidationError(f"trigger.type must be one of {sorted(TRIGGER_TYPES)}")
        return value

    def create(self, validated_data):
        if "client_id" not in validated_data:
            scenario = validated_data["scenario"]
            n = scenario.objectives.count() + 1
            validated_data["client_id"] = f"obj-{n}"
        return super().create(validated_data)


class ScenarioSerializer(serializers.ModelSerializer):
    entities = ScenarioEntitySerializer(many=True, read_only=True)
    objectives = ObjectiveSerializer(many=True, read_only=True)
    battlespace_name = serializers.CharField(source="battlespace.name", read_only=True)

    class Meta:
        model = Scenario
        fields = ["id", "battlespace", "battlespace_name", "name", "version", "status",
                  "environment", "published_at", "entities", "objectives", "created_at", "updated_at"]
        read_only_fields = ["id", "version", "status", "published_at", "created_at", "updated_at"]


class ScenarioListSerializer(serializers.ModelSerializer):
    battlespace_name = serializers.CharField(source="battlespace.name", read_only=True)

    class Meta:
        model = Scenario
        fields = ["id", "battlespace", "battlespace_name", "name", "version",
                  "status", "updated_at"]
