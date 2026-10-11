from django.db import models


class TerrainBuild(models.Model):
    """A queued/exported terrain tile build for a battlespace AOI.

    v0.1 records the request and writes a tile manifest; actual tile
    rendering (e.g. Cesium ion export or GDAL mosaic) is a later milestone.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    battlespace = models.ForeignKey("battlespace.Battlespace", on_delete=models.CASCADE, related_name="terrain_builds")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    bbox = models.JSONField(default=list)  # [minLon, minLat, maxLon, maxLat]
    resolution_meters = models.FloatField(default=1.0)
    manifest = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"terrain-build {self.pk} [{self.status}]"
