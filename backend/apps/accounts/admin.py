from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Organization, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("TBS", {"fields": ("role", "organization")}),)
    list_display = ["username", "email", "role", "organization", "is_active"]
    list_filter = ["role", "is_active"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
