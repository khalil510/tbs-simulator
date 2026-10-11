from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AarEventViewSet, AarIngestView, AarMetricsView, AarReplayView

router = DefaultRouter()
router.register("aar-events", AarEventViewSet, basename="aar-event")

urlpatterns = router.urls + [
    path("sessions/<uuid:pk>/aar/ingest/", AarIngestView.as_view(), name="aar-ingest"),
    path("sessions/<uuid:pk>/aar/replay/", AarReplayView.as_view(), name="aar-replay"),
    path("sessions/<uuid:pk>/aar/metrics/", AarMetricsView.as_view(), name="aar-metrics"),
]
