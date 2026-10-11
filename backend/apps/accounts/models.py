from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Administrator"
    PLANNER = "planner", "Scenario Planner"
    INSTRUCTOR = "instructor", "Instructor"
    TRAINEE = "trainee", "Trainee"


class User(AbstractUser):
    """Platform user. Roles drive API permissions across the whole system."""

    class Meta:
        ordering = ["username"]

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TRAINEE)
    organization = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL, related_name="members"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


class Organization(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
