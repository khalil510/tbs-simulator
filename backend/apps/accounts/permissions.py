from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Role

STAFF_ROLES = (Role.ADMIN, Role.PLANNER, Role.INSTRUCTOR)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.ADMIN)


class IsPlannerOrAdmin(BasePermission):
    """Write access to scenarios/battlespaces."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role in (Role.ADMIN, Role.PLANNER) or request.user.is_superuser)
        )


class IsInstructorOrStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role in STAFF_ROLES or request.user.is_superuser)
        )


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
