from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsAdmin
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """Return the authenticated user's profile."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserAdminListView(generics.ListAPIView):
    """Admin-only user listing (used for role management UI)."""

    queryset = User.objects.select_related("organization").all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class PromoteView(APIView):
    """Admin-only role assignment."""

    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        role = request.data.get("role")
        valid_roles = {c[0] for c in User._meta.get_field("role").choices}
        if role not in valid_roles:
            return Response({"detail": f"role must be one of {sorted(valid_roles)}"},
                            status=status.HTTP_400_BAD_REQUEST)
        user.role = role
        user.save(update_fields=["role"])
        return Response(UserSerializer(user).data)
