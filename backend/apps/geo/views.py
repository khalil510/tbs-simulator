from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsInstructorOrStaff
from apps.battlespace.models import Battlespace

from .models import TerrainBuild
from .serializers import TerrainBuildSerializer
from .tasks import build_terrain_tiles


class TerrainBuildViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TerrainBuildSerializer
    permission_classes = [IsInstructorOrStaff]
    filterset_fields = ["battlespace", "status"]

    def get_queryset(self):
        return TerrainBuild.objects.select_related("battlespace")


class RequestTerrainBuildView(APIView):
    """Enqueue a terrain tile build for a battlespace AOI."""

    permission_classes = [IsInstructorOrStaff]

    def post(self, request, pk):
        battlespace = get_object_or_404(Battlespace, pk=pk)
        minx, miny, maxx, maxy = battlespace.aoi.extent
        build = TerrainBuild.objects.create(
            battlespace=battlespace,
            bbox=[minx, miny, maxx, maxy],
            resolution_meters=float(request.data.get("resolutionMeters", 1.0)),
        )
        build_terrain_tiles.delay(build.pk)
        return Response(TerrainBuildSerializer(build).data, status=status.HTTP_202_ACCEPTED)
