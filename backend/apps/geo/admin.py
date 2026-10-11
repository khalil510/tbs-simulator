from django.contrib import admin

from .models import TerrainBuild


@admin.register(TerrainBuild)
class TerrainBuildAdmin(admin.ModelAdmin):
    list_display = ["id", "battlespace", "status", "created_at", "finished_at"]
    list_filter = ["status"]
