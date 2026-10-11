from django.contrib import admin

from .models import AarEvent, AarMetrics, AarReplay


@admin.register(AarEvent)
class AarEventAdmin(admin.ModelAdmin):
    list_display = ["session", "t", "entity_id", "kind"]
    list_filter = ["kind"]


@admin.register(AarReplay)
class AarReplayAdmin(admin.ModelAdmin):
    list_display = ["session", "storage_key", "size_bytes", "uploaded_at"]


@admin.register(AarMetrics)
class AarMetricsAdmin(admin.ModelAdmin):
    list_display = ["session", "computed_at"]
