"""Base settings shared by all environments."""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = False
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    # Project apps
    "apps.accounts",
    "apps.battlespace",
    "apps.sessions",
    "apps.aar",
    "apps.geo",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database: PostgreSQL + PostGIS -----------------------------------------
# Set TBS_DB_ENGINE=sqlite to run the test suite without a PostGIS instance
# (geo columns are then unvalidated TextFields; production MUST use PostGIS).
if os.environ.get("TBS_DB_ENGINE") == "sqlite":
    DATABASES = {
        "default": {
            # Geo-capable fallback backend (WKT storage, no spatial SQL).
            # See config/gis_sqlite_fallback.py for limitations.
            "ENGINE": "config.gis_sqlite_fallback",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": os.environ.get("POSTGRES_DB", "tbs"),
            "USER": os.environ.get("POSTGRES_USER", "tbs"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "tbs"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

# --- Auth / JWT ---------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# Short-lived tickets handed to UE5 dedicated servers for session handoff.
TBS_SESSION_TICKET_LIFETIME = int(os.environ.get("TBS_SESSION_TICKET_TTL_SECONDS", "60"))

CORS_ALLOWED_ORIGINS = [
    o for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:4200").split(",") if o
]

# --- Static / media -----------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

# --- Celery -------------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# --- TBS-specific -------------------------------------------------------------
# Root of the schemas/ directory shared with the UE5 runtime.
TBS_SCHEMA_DIR = BASE_DIR.parent / "schemas"  # repo-root schemas/ shared with UE5

# --- Optional bundled GEOS/GDAL ------------------------------------------------
# Dev laptops/CI sandboxes without system GIS libraries can set
# TBS_BUNDLED_GIS=1 to load GEOS from the shapely wheel and GDAL from the
# pyogrio wheel (both ship bundled C libraries). Production containers should
# install distro packages instead and leave this off.
if os.environ.get("TBS_BUNDLED_GIS") == "1":
    import ctypes.util
    import glob
    import site

    _sp_dirs = list(site.getsitepackages()) + [site.getusersitepackages()]
    if not ctypes.util.find_library("geos_c"):
        for _sp in _sp_dirs:
            _hits = glob.glob(os.path.join(_sp, "shapely.libs", "libgeos_c*"))
            if _hits:
                GEOS_LIBRARY_PATH = _hits[0]
                break
    if not ctypes.util.find_library("gdal"):
        for _sp in _sp_dirs:
            _hits = glob.glob(os.path.join(_sp, "pyogrio.libs", "libgdal*"))
            if _hits:
                GDAL_LIBRARY_PATH = _hits[0]
                break
