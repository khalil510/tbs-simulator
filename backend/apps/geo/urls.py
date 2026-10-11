from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RequestTerrainBuildView, TerrainBuildViewSet

router = DefaultRouter()
router.register("terrain-builds", TerrainBuildViewSet, basename="terrain-build")

urlpatterns = router.urls + [
    path("battlespaces/<uuid:pk>/terrain/", RequestTerrainBuildView.as_view(), name="terrain-build-request"),
]
