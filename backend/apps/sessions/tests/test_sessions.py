import json

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role
from apps.battlespace.models import Battlespace, Scenario, ScenarioEntity

User = get_user_model()

AOI = GEOSGeometry(json.dumps({"type": "Polygon", "coordinates": [[(35.2, 31.75), (35.35, 31.75), (35.35, 31.9), (35.2, 31.9), (35.2, 31.75)]]}))
AOI.srid = 4326


def _mk_scenario(name="Live Run"):
    planner = User.objects.create_user(username=f"planner-{name}", password="Pl4nnerPass!x", role=Role.PLANNER)
    bs = Battlespace.objects.create(name=f"BS {name}", created_by=planner, aoi=AOI)
    scenario = Scenario.objects.create(battlespace=bs, name=name, environment={"timeOfDay": "09:00"})
    ScenarioEntity.objects.create(
        scenario=scenario, client_id="ent-1", kind="infantry-squad", side="blue",
        position=Point(35.28, 31.81, srid=4326))
    return planner, scenario


class SessionLifecycleTests(APITestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="instructor", password="In5trPass!x", role=Role.INSTRUCTOR)
        self.client.force_authenticate(self.instructor)

    def test_cannot_launch_unpublished(self):
        _, scenario = _mk_scenario("Draft Only")
        resp = self.client.post(reverse("session-list"), {"scenario": scenario.pk}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_lifecycle_and_ticket(self):
        planner, scenario = _mk_scenario("Live One")
        scenario.status = "published"
        scenario.version = 1
        scenario.save()

        resp = self.client.post(reverse("session-list"), {"scenario": scenario.pk}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        sid = resp.data["id"]

        def post(action):
            return self.client.post(reverse(f"session-{action}", args=[sid]))

        self.assertEqual(post("start").data["state"], "running")
        self.assertEqual(post("pause").data["state"], "paused")
        self.assertEqual(post("resume").data["state"], "running")
        # invalid transition: start while running
        self.assertEqual(post("start").status_code, status.HTTP_409_CONFLICT)
        # ticket handoff
        t = self.client.post(reverse("session-ticket", args=[sid]))
        self.assertEqual(t.status_code, status.HTTP_200_OK, t.data)
        self.assertIn("ticket", t.data)
        self.assertEqual(t.data["expiresIn"], 60)
        self.assertIn("export", t.data["scenarioExportUrl"])
        self.assertEqual(post("end").data["state"], "ended")
