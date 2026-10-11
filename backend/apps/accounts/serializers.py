from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Organization, Role, User


class UserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role",
                  "organization", "organization_name"]
        read_only_fields = ["id", "role", "organization"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        # Self-registration always starts as a trainee; admins promote users.
        return User.objects.create_user(role=Role.TRAINEE, **validated_data)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]
