from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import IssueTicketView, SimSessionViewSet

router = DefaultRouter()
router.register("sessions", SimSessionViewSet, basename="session")

urlpatterns = router.urls + [
    path("sessions/<uuid:pk>/ticket/", IssueTicketView.as_view(), name="session-ticket"),
]
