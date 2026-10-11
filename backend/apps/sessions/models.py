import uuid

from django.conf import settings
from django.db import models


class SessionState(models.TextChoices):
    LOBBY = "lobby", "Lobby"
    RUNNING = "running", "Running"
    PAUSED = "paused", "Paused"
    ENDED = "ended", "Ended"


class SimSession(models.Model):
    """A live training session launched from a published scenario.

    The UE5 dedicated server authenticates with a short-lived signed ticket
    (see views.IssueTicketView) instead of a user login.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey("battlespace.Scenario", on_delete=models.PROTECT, related_name="sessions")
    state = models.CharField(max_length=10, choices=SessionState.choices, default=SessionState.LOBBY)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name="led_sessions", null=True, blank=True)
    server_allocation = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"session {self.pk} [{self.state}]"


class SessionParticipant(models.Model):
    session = models.ForeignKey(SimSession, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions_joined")
    entity_client_id = models.CharField(max_length=64, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "user"], name="unique_session_user")
        ]
