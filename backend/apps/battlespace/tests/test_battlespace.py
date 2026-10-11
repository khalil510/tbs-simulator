import json

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, Point
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role
from apps.battlespace.models import Battlespace, Scenario, ScenarioEntity

User = get_user_model()

AOI_GEOJSON = {
    "type": "Polygon",
    "coordinates": [[[35.2, 31.75], [35.35, 31.75], [35.35, 31.9], [35.2, 31.9], [35.2, 31.75]]],
}


class BattlespaceApiTests(APITestCase):
    def setUp(self):
        self.planner = User.objects.create_user(username="planner", password="Pl4nnerPass!x", role=Role.PLANNER)
        self.trainee = User.objects.create_user(username="rookie", password="Tr4ineePass!x", role=Role.TRAINEE)
        self.client.force_authenticate(self.planner)

    def _mk_battlespace(self, name="Alpha AOI"):
        aoi = GEOSGeometry(json.dumps(AOI_GEOJSON))
        aoi.srid = 4326
        return Battlespace.objects.create(name=name, created_by=self.planner, aoi=aoi)

    def test_create_battlespace_with_geojson_aoi(self):
        url = reverse("battlespace-list")
        resp = self.client.post(url, {"name": "Test AOI", "aoi": AOI_GEOJSON}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        bs = Battlespace.objects.get(name="Test AOI")
        self.assertEqual(bs.aoi.srid, 4326)
        self.assertEqual(resp.data["aoi"]["type"], "Polygon")

    def test_trainee_cannot_create(self):
        self.client.force_authenticate(self.trainee)
        url = reverse("battlespace-list")
        resp = self.client.post(url, {"name": "Nope", "aoi": AOI_GEOJSON}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class ScenarioPublishTests(APITestCase):
    def setUp(self):
        self.planner = User.objects.create_user(username="planner", password="Pl4nnerPass!x", role=Role.PLANNER)
        self.client.force_authenticate(self.planner)
        aoi = GEOSGeometry(json.dumps(AOI_GEOJSON))
        aoi.srid = 4326
        self.bs = Battlespace.objects.create(
            name="Alpha", created_by=self.planner, aoi=aoi,
            terrain_source={"provider": "cesium-ion", "assetId": 1},
        )
        self.scenario = Scenario.objects.create(battlespace=self.bs, name="Village Clear",
                                                environment={"timeOfDay": "06:30", "weather": "overcast"})
        ScenarioEntity.objects.create(
            scenario=self.scenario, client_id="ent-1", kind="infantry-squad", side="blue",
            position=Point(35.281, 31.812, srid=4326),
            composition={"soldiers": 9, "loadout": "standard-rifle"},
            waypoints=[{"lat": 35.281, "lon": 31.812, "speedMs": 1.4, "action": "move"}],
        )

    def test_publish_validates_and_versions(self):
        url = reverse("scenario-publish", args=[self.scenario.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.scenario.refresh_from_db()
        self.assertEqual(self.scenario.status, "published")
        self.assertEqual(self.scenario.version, 1)
        # double publish -> conflict
        resp2 = self.client.post(url)
        self.assertEqual(resp2.status_code, status.HTTP_409_CONFLICT)

    def test_publish_fails_on_bad_entity(self):
        ScenarioEntity.objects.create(
            scenario=self.scenario, client_id="bad-ent", kind="spaceship", side="purple",
            position=Point(35.3, 31.8, srid=4326),
        )
        url = reverse("scenario-publish", args=[self.scenario.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(resp.data["errors"])

    def test_export_matches_schema(self):
        url = reverse("scenario-export", args=[self.scenario.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        doc = resp.data["scenario"]
        self.assertEqual(doc["schemaVersion"], "0.1.0")
        self.assertEqual(doc["meta"]["name"], "Village Clear")
        self.assertEqual(len(doc["terrain"]["bbox"]), 4)
        self.assertEqual(doc["entities"][0]["id"], "ent-1")
        # Point(x=lon, y=lat) in GeoDjango
        self.assertEqual(doc["entities"][0]["position"]["lon"], 35.281)
        self.assertEqual(doc["entities"][0]["position"]["lat"], 31.812)
        self.assertEqual(resp.data["validationErrors"], [], resp.data["validationErrors"])
        # The document must round-trip through JSON (the UE5 handoff format).
        json.loads(json.dumps(doc))
