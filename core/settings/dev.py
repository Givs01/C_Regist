# core/settings/dev.py
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Dev only (no HTTPS enforcement)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
