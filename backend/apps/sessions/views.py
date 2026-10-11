import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.permissions import IsInstructorOrStaff

from .models import SessionParticipant, SessionState, SimSession
from .serializers import CreateSessionSerializer, SimSessionSerializer


class SimSessionViewSet(viewsets.ModelViewSet):
    serializer_class = SimSessionSerializer
    permission_classes = [IsInstructorOrStaff]
    filterset_fields = ["state", "scenario"]

    def get_queryset(self):
        return SimSession.objects.select_related("scenario", "instructor").prefetch_related(
            "participants__user")

    def create(self, request, *args, **kwargs):
        serializer = CreateSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = SimSession.objects.create(
            scenario=serializer.validated_data["scenario"], instructor=request.user
        )
        return Response(SimSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    def _transition(self, request, pk, allowed_from, to, extra_fields=None):
        try:
            session = SimSession.objects.get(pk=pk)
        except SimSession.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if session.state not in allowed_from:
            return Response(
                {"detail": f"Cannot transition from {session.state} to {to}."},
                status=status.HTTP_409_CONFLICT)
        session.state = to
        fields = ["state"]
        if extra_fields:
            for f, v in extra_fields.items():
                setattr(session, f, v)
                fields.append(f)
        session.save(update_fields=fields)
        return Response(SimSessionSerializer(session).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        return self._transition(request, pk, [SessionState.LOBBY], SessionState.RUNNING,
                                {"started_at": timezone.now()})

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        return self._transition(request, pk, [SessionState.RUNNING], SessionState.PAUSED)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        return self._transition(request, pk, [SessionState.PAUSED], SessionState.RUNNING)

    @action(detail=True, methods=["post"])
    def end(self, request, pk=None):
        return self._transition(request, pk, [SessionState.RUNNING, SessionState.PAUSED, SessionState.LOBBY],
                                SessionState.ENDED, {"ended_at": timezone.now()})

    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        session = self.get_object()
        if session.state == SessionState.ENDED:
            return Response({"detail": "Session has ended."}, status=status.HTTP_409_CONFLICT)
        participant, created = SessionParticipant.objects.get_or_create(
            session=session, user=request.user)
        return Response({"participantId": participant.pk, "created": created},
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class IssueTicketView(APIView):
    """Issue a short-lived JWT the UE5 dedicated server uses to fetch the
    scenario and register itself. This is the session handoff seam.

    In production this endpoint is protected by a service credential, not a
    user JWT; the placeholder below requires instructor role.
    """

    permission_classes = [IsInstructorOrStaff]

    def post(self, request, pk):
        try:
            session = SimSession.objects.select_related("scenario").get(pk=pk)
        except SimSession.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        jti = str(uuid.uuid4())
        refresh = RefreshToken.for_user(request.user)
        refresh["tbs_session_id"] = str(session.pk)
        refresh["tbs_role"] = "sim-server"
        refresh["jti"] = jti
        ttl = settings.TBS_SESSION_TICKET_LIFETIME
        return Response({
            "ticket": str(refresh.access_token),
            "expiresIn": ttl,
            "sessionId": str(session.pk),
            "scenarioExportUrl": f"/api/scenarios/{session.scenario_id}/export/",
        })
