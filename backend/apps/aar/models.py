import uuid

from django.db import models


class AarReplay(models.Model):
    """Raw replay file (NDJSON of aar-event.schema.json) stored in media/object storage."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.OneToOneField("sim_sessions.SimSession", on_delete=models.CASCADE, related_name="replay")
    storage_key = models.CharField(max_length=500)
    format = models.CharField(max_length=20, default="ndjson")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size_bytes = models.BigIntegerField(default=0)

    def __str__(self):
        return f"replay {self.session_id}"


class AarEvent(models.Model):
    """One telemetry/event record emitted by the UE5 server.

    High-volume: in production this table is a TimescaleDB hypertable
    (see infra/README) partitioned on `t`.
    """

    session = models.ForeignKey("sim_sessions.SimSession", on_delete=models.CASCADE, related_name="aar_events")
    t = models.FloatField(help_text="Seconds since session start")
    entity_id = models.CharField(max_length=64)
    kind = models.CharField(max_length=32)
    position = models.CharField(max_length=128, blank=True, help_text="Optional WKT point")
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["session", "t"]),
            models.Index(fields=["session", "entity_id", "kind"]),
        ]
        ordering = ["t"]


class AarMetrics(models.Model):
    """Aggregate results computed at session end (by a Celery task)."""

    session = models.OneToOneField("sim_sessions.SimSession", on_delete=models.CASCADE, related_name="metrics")
    computed_at = models.DateTimeField(auto_now_add=True)
    values = models.JSONField(default=dict)  # e.g. {"timeToObjectiveS": 812, "casualties": {"blue": 2, "red": 7}}

    def __str__(self):
        return f"metrics {self.session_id}"
