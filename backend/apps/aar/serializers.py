from rest_framework import serializers

from .models import AarEvent, AarMetrics, AarReplay


class AarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AarEvent
        fields = ["id", "session", "t", "entity_id", "kind", "position", "payload"]
        # session is bound server-side (batch ingest view), never client input
        read_only_fields = ["id", "session"]


class AarEventBatchSerializer(serializers.Serializer):
    """Batch ingest from the UE5 dedicated server."""

    events = AarEventSerializer(many=True)

    def create(self, validated_data):
        session = self.context["session"]
        events = [AarEvent(session=session, **e) for e in validated_data["events"]]
        return AarEvent.objects.bulk_create(events)


class AarMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AarMetrics
        fields = ["session", "computed_at", "values"]


class AarReplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = AarReplay
        fields = ["id", "session", "storage_key", "format", "uploaded_at", "size_bytes"]
        read_only_fields = ["id", "uploaded_at"]
