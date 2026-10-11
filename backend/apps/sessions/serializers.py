from rest_framework import serializers

from apps.battlespace.models import ScenarioStatus

from .models import SessionParticipant, SimSession


class SessionParticipantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = SessionParticipant
        fields = ["id", "user", "username", "entity_client_id", "joined_at", "left_at"]


class SimSessionSerializer(serializers.ModelSerializer):
    participants = SessionParticipantSerializer(many=True, read_only=True)
    instructor_name = serializers.CharField(source="instructor.username", read_only=True)
    scenario_name = serializers.CharField(source="scenario.name", read_only=True)

    class Meta:
        model = SimSession
        fields = ["id", "scenario", "scenario_name", "state", "instructor", "instructor_name",
                  "server_allocation", "started_at", "ended_at", "created_at", "participants"]
        read_only_fields = ["id", "state", "server_allocation", "started_at", "ended_at", "created_at"]


class CreateSessionSerializer(serializers.Serializer):
    scenario = serializers.UUIDField()

    def validate_scenario(self, value):
        from apps.battlespace.models import Scenario
        try:
            scenario = Scenario.objects.select_related("battlespace").get(pk=value)
        except Scenario.DoesNotExist as err:
            raise serializers.ValidationError("Scenario not found.") from err
        if scenario.status != ScenarioStatus.PUBLISHED:
            raise serializers.ValidationError("Only published scenarios can be launched.")
        return scenario
