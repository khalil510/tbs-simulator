import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role
from apps.battlespace.models import Battlespace, Scenario
from apps.sessions.models import SimSession

User = get_user_model()

AOI = GEOSGeometry(json.dumps({"type": "Polygon", "coordinates": [[(35.2, 31.75), (35.35, 31.75), (35.35, 31.9), (35.2, 31.9), (35.2, 31.75)]]}))
AOI.srid = 4326


class AarIngestTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="simserver", password="S3rvPass!x", role=Role.INSTRUCTOR)
        self.client.force_authenticate(self.user)
        planner = User.objects.create_user(username="pl", password="Pl4nnerPass!x", role=Role.PLANNER)
        bs = Battlespace.objects.create(name="A", created_by=planner, aoi=AOI)
        scenario = Scenario.objects.create(battlespace=bs, name="S")
        self.session = SimSession.objects.create(scenario=scenario)

    def test_ingest_and_read_back(self):
        url = reverse("aar-ingest", args=[self.session.pk])
        events = [
            {"t": 0.0, "entity_id": "ent-1", "kind": "position", "payload": {}},
            {"t": 0.1, "entity_id": "ent-1", "kind": "position", "payload": {}},
            {"t": 1.5, "entity_id": "ent-1", "kind": "shot-fired",
             "payload": {"weapon": "rifle", "target": None}},
        ]
        resp = self.client.post(url, {"events": events}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(resp.data["accepted"], 3)

        list_url = reverse("aar-event-list") + f"?session={self.session.pk}"
        listing = self.client.get(list_url)
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(listing.data["count"], 3)
        first = listing.data["results"][0]
        self.assertEqual(first["kind"], "position")

    def test_events_validate_against_schema(self):
        """Every ingested event must satisfy schemas/aar-event.schema.json."""
        import jsonschema
        schema = json.loads(
            (Path(__file__).resolve().parents[4] / "schemas" / "aar-event.schema.json").read_text())
        url = reverse("aar-ingest", args=[self.session.pk])
        good = {"t": 2.0, "entity_id": "ent-2", "kind": "kill", "payload": {"killer": "ent-1"}}
        jsonschema.validate(good, schema)
        resp = self.client.post(url, {"events": [good]}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
