from celery import shared_task
from django.utils import timezone


@shared_task(bind=True)
def build_terrain_tiles(self, terrain_build_id: int):
    """Placeholder terrain build: records a manifest describing the tile grid.

    Replace the body of this task with the real pipeline (GDAL mosaic /
    Cesium ion asset creation) in milestone M2. Keeping the task signature
    stable means the API does not change when the implementation does.
    """
    from .models import TerrainBuild

    try:
        build = TerrainBuild.objects.select_related("battlespace").get(pk=terrain_build_id)
    except TerrainBuild.DoesNotExist:
        return {"error": "not found"}

    build.status = TerrainBuild.Status.RUNNING
    build.save(update_fields=["status"])

    try:
        min_lon, min_lat, max_lon, max_lat = build.bbox
        deg_per_tile = 0.01  # ~1.1 km tiles at the equator; placeholder sizing
        tiles_x = max(1, int((max_lon - min_lon) / deg_per_tile) + 1)
        tiles_y = max(1, int((max_lat - min_lat) / deg_per_tile) + 1)
        build.manifest = {
            "provider": "placeholder",
            "grid": {"tilesX": tiles_x, "tilesY": tiles_y},
            "resolutionMeters": build.resolution_meters,
            "bbox": build.bbox,
        }
        build.status = TerrainBuild.Status.DONE
        build.finished_at = timezone.now()
        build.save(update_fields=["manifest", "status", "finished_at"])
        return {"build": build.pk, "tiles": tiles_x * tiles_y}
    except Exception as exc:  # noqa: BLE001 - task must record failure, not crash worker silently
        build.status = TerrainBuild.Status.FAILED
        build.error = str(exc)
        build.save(update_fields=["status", "error"])
        raise
