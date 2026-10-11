from django.apps import AppConfig


class SessionsConfig(AppConfig):
    # "sessions" collides with django.contrib.sessions; keep a distinct label.
    name = "apps.sessions"
    label = "sim_sessions"
    default_auto_field = "django.db.models.BigAutoField"
