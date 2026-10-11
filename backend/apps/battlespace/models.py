import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Battlespace(TimeStamped):
    """A portable container: terrain region + scenarios + assets + AAR references.

    The area of interest (AOI) polygon defines the geographic extent in WGS84.
    `terrain_source` is validated against schemas/scenario.schema.json's
    terrain block by the serializer.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(
        "accounts.Organization", null=True, blank=True, on_delete=models.CASCADE, related_name="battlespaces"
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="battlespaces")
    aoi = models.PolygonField(srid=4326, help_text="Area of interest in WGS84")
    terrain_source = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class ScenarioStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    VALIDATED = "validated", "Validated"
    PUBLISHED = "published", "Published"


class Scenario(TimeStamped):
    """A versioned mission definition inside a battlespace.

    Drafts are freely editable; publish freezes the scenario and increments
    `version`. The canonical export (JSON matching schemas/scenario.schema.json)
    is assembled by ScenarioExportService.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    battlespace = models.ForeignKey(Battlespace, on_delete=models.CASCADE, related_name="scenarios")
    name = models.CharField(max_length=200)
    version = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=12, choices=ScenarioStatus.choices, default=ScenarioStatus.DRAFT)
    environment = models.JSONField(default=dict, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["battlespace", "name", "-version"]
        constraints = [
            models.UniqueConstraint(fields=["battlespace", "name", "version"], name="unique_scenario_version")
        ]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.status})"


class EntitySide(models.TextChoices):
    BLUE = "blue", "Blue"
    RED = "red", "Red"
    GREEN = "green", "Green"
    NEUTRAL = "neutral", "Neutral"


class ScenarioEntity(models.Model):
    """An entity placed on the map: unit, squad, spawn point, or marker.

    `waypoints` is an ordered list of {lat, lon, alt?, speedMs?, action?}
    objects validated against the scenario schema on publish.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="entities")
    client_id = models.CharField(
        max_length=64, help_text="Stable id inside the scenario export, e.g. ent-1"
    )
    kind = models.CharField(max_length=32)  # validated by serializer against schema enums
    side = models.CharField(max_length=10, choices=EntitySide.choices)
    position = models.PointField(srid=4326)
    heading_deg = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(360)])
    composition = models.JSONField(default=dict, blank=True)
    waypoints = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["client_id"]
        constraints = [
            models.UniqueConstraint(fields=["scenario", "client_id"], name="unique_entity_client_id")
        ]

    def __str__(self):
        return f"{self.client_id} ({self.kind}/{self.side})"


class Objective(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="objectives")
    client_id = models.CharField(max_length=64)
    description = models.CharField(max_length=400)
    points = models.PositiveIntegerField(default=0)
    trigger = models.JSONField(default=dict)

    class Meta:
        ordering = ["client_id"]
        constraints = [
            models.UniqueConstraint(fields=["scenario", "client_id"], name="unique_objective_client_id")
        ]

    def __str__(self):
        return f"{self.client_id}: {self.description}"
