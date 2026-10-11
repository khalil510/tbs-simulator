from rest_framework import serializers

from .models import TerrainBuild


class TerrainBuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerrainBuild
        fields = ["id", "battlespace", "status", "bbox", "resolution_meters",
                  "manifest", "error", "created_at", "finished_at"]
        read_only_fields = ["id", "status", "manifest", "error", "created_at", "finished_at"]
