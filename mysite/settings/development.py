# flake8: noqa
from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]

if "debug_toolbar" not in INSTALLED_APPS:
    INSTALLED_APPS += ["debug_toolbar"]

if "debug_toolbar.middleware.DebugToolbarMiddleware" not in MIDDLEWARE:
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1", "172.18.0.1", "172.17.0.1"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/0"),
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
