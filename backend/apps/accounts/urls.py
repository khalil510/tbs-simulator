from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeView, PromoteView, RegisterView, UserAdminListView

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", UserAdminListView.as_view(), name="user-list"),
    path("users/<int:pk>/promote/", PromoteView.as_view(), name="user-promote"),
]
