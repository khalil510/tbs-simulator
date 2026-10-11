from django.contrib import admin

from .models import SessionParticipant, SimSession


@admin.register(SimSession)
class SimSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "scenario", "state", "instructor", "started_at", "ended_at"]
    list_filter = ["state"]


@admin.register(SessionParticipant)
class SessionParticipantAdmin(admin.ModelAdmin):
    list_display = ["session", "user", "entity_client_id", "joined_at"]
