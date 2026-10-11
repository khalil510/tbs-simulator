from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsInstructorOrStaff, IsPlannerOrAdmin

from .export import export_and_validate
from .models import Battlespace, Objective, Scenario, ScenarioEntity, ScenarioStatus
from .serializers import (
    BattlespaceSerializer,
    ObjectiveSerializer,
    ScenarioEntitySerializer,
    ScenarioListSerializer,
    ScenarioSerializer,
)


class BattlespaceViewSet(viewsets.ModelViewSet):
    serializer_class = BattlespaceSerializer
    permission_classes = [IsInstructorOrStaff]
    filterset_fields = ["organization"]

    def get_queryset(self):
        qs = Battlespace.objects.select_related("organization", "created_by")
        # Keep tenants isolated: org members see their org's + org-less spaces.
        user = self.request.user
        if not user.is_superuser and user.organization_id:
            qs = qs.filter(organization_id=user.organization_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ScenarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsInstructorOrStaff]
    filterset_fields = ["battlespace", "status"]

    def get_serializer_class(self):
        if self.action == "list":
            return ScenarioListSerializer
        return ScenarioSerializer

    def get_queryset(self):
        qs = Scenario.objects.select_related("battlespace", "battlespace__created_by")
        user = self.request.user
        if not user.is_superuser and user.organization_id:
            qs = qs.filter(battlespace__organization_id=user.organization_id)
        return qs

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsPlannerOrAdmin])
    def publish(self, request, pk=None):
        """Validate against the shared schema, then freeze + version."""
        scenario = self.get_object()
        if scenario.status == ScenarioStatus.PUBLISHED:
            return Response({"detail": "Scenario already published."},
                            status=status.HTTP_409_CONFLICT)
        doc, errors = export_and_validate(scenario)
        if errors:
            return Response({"detail": "Schema validation failed.", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)
        scenario.status = ScenarioStatus.PUBLISHED
        scenario.version += 1
        scenario.published_at = timezone.now()
        scenario.save(update_fields=["status", "version", "published_at", "updated_at"])
        return Response(ScenarioSerializer(scenario).data)

    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        """Dry-run schema validation without publishing."""
        scenario = self.get_object()
        _, errors = export_and_validate(scenario)
        if errors:
            return Response({"valid": False, "errors": errors}, status=status.HTTP_200_OK)
        return Response({"valid": True, "errors": []})

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        """Download the canonical scenario JSON (what UE5 consumes)."""
        scenario = self.get_object()
        doc, errors = export_and_validate(scenario)
        return Response({"scenario": doc, "validationErrors": errors})


class ScenarioEntityViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioEntitySerializer
    permission_classes = [IsInstructorOrStaff]
    filterset_fields = ["scenario", "side", "kind"]

    def get_queryset(self):
        return ScenarioEntity.objects.filter(scenario__battlespace__isnull=False)

    def perform_create(self, serializer):
        serializer.save(scenario=self._get_scenario())

    def _get_scenario(self):
        from django.shortcuts import get_object_or_404
        scenario_id = self.request.data.get("scenario")
        return get_object_or_404(Scenario, pk=scenario_id)


class ObjectiveViewSet(viewsets.ModelViewSet):
    serializer_class = ObjectiveSerializer
    permission_classes = [IsInstructorOrStaff]
    filterset_fields = ["scenario"]

    def get_queryset(self):
        return Objective.objects.all()

    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        scenario_id = self.request.data.get("scenario")
        serializer.save(scenario=get_object_or_404(Scenario, pk=scenario_id))
