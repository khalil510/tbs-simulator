from django.contrib import admin

from .models import Battlespace, Objective, Scenario, ScenarioEntity


@admin.register(Battlespace)
class BattlespaceAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "created_by", "updated_at"]
    search_fields = ["name"]


class ScenarioEntityInline(admin.TabularInline):
    model = ScenarioEntity
    extra = 0


class ObjectiveInline(admin.TabularInline):
    model = Objective
    extra = 0


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ["name", "battlespace", "version", "status", "updated_at"]
    list_filter = ["status"]
    inlines = [ScenarioEntityInline, ObjectiveInline]
