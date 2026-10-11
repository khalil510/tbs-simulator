from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

if os.environ.get("TBS_DB_ENGINE") == "sqlite":  # noqa: F405
    pass
