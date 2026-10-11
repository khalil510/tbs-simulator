from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User


class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.token_url = reverse("token_obtain_pair")
        self.me_url = reverse("me")

    def _register(self, username="trainee1", password="Str0ngPass!x1"):
        return self.client.post(
            self.register_url,
            {"username": username, "email": f"{username}@example.com", "password": password},
            format="json",
        )

    def _token(self, username, password="Str0ngPass!x1"):
        return self.client.post(self.token_url, {"username": username, "password": password}, format="json")

    def _auth(self, username, password="Str0ngPass!x1"):
        token = self._token(username, password).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_register_creates_trainee(self):
        resp = self._register()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="trainee1")
        self.assertEqual(user.role, Role.TRAINEE)

    def test_login_and_me(self):
        self._register()
        self._auth("trainee1")
        resp = self.client.get(self.me_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "trainee1")
        self.assertEqual(resp.data["role"], Role.TRAINEE)

    def test_me_requires_auth(self):
        resp = self.client.get(self.me_url)
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_promote_requires_admin(self):
        self._register()
        self._auth("trainee1")
        other = User.objects.create_user(username="victim", password="x", role=Role.TRAINEE)
        url = reverse("user-promote", args=[other.pk])
        resp = self.client.post(url, {"role": Role.INSTRUCTOR}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_promote(self):
        User.objects.create_user(username="root", password="Adm1nPass!x", role=Role.ADMIN)
        self._auth("root", "Adm1nPass!x")
        other = User.objects.create_user(username="victim", password="x", role=Role.TRAINEE)
        url = reverse("user-promote", args=[other.pk])
        resp = self.client.post(url, {"role": Role.INSTRUCTOR}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        other.refresh_from_db()
        self.assertEqual(other.role, Role.INSTRUCTOR)
