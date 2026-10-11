from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.sessions.models import SimSession

from .models import AarEvent, AarMetrics, AarReplay
from .serializers import (
    AarEventBatchSerializer,
    AarEventSerializer,
    AarMetricsSerializer,
    AarReplaySerializer,
)


class AarEventViewSet(viewsets.ReadOnlyModelViewSet):
    filterset_fields = ["session", "entity_id", "kind"]

    def get_queryset(self):
        return AarEvent.objects.select_related("session")

    def get_serializer_class(self):
        return AarEventSerializer


class AarIngestView(APIView):
    """Batched AAR event upload from the sim server (session ticket auth)."""

    def post(self, request, pk):
        session = get_object_or_404(SimSession, pk=pk)
        serializer = AarEventBatchSerializer(data=request.data, context={"session": session})
        serializer.is_valid(raise_exception=True)
        created = serializer.save()
        return Response({"accepted": len(created)}, status=status.HTTP_201_CREATED)


class AarReplayView(APIView):
    """Register the replay file for a session (upload happens via object storage)."""

    def post(self, request, pk):
        session = get_object_or_404(SimSession, pk=pk)
        serializer = AarReplaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        replay, _ = AarReplay.objects.update_or_create(session=session, defaults=serializer.validated_data)
        return Response(AarReplaySerializer(replay).data)

    def get(self, request, pk):
        session = get_object_or_404(SimSession, pk=pk)
        try:
            return Response(AarReplaySerializer(session.replay).data)
        except AarReplay.DoesNotExist:
            return Response({"detail": "No replay for this session."}, status=status.HTTP_404_NOT_FOUND)


class AarMetricsView(APIView):
    def get(self, request, pk):
        session = get_object_or_404(SimSession, pk=pk)
        try:
            return Response(AarMetricsSerializer(session.metrics).data)
        except AarMetrics.DoesNotExist:
            return Response({"detail": "Metrics not computed yet."}, status=status.HTTP_404_NOT_FOUND)
