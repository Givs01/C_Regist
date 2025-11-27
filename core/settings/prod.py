# core/settings/prod.py
from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = ['c-regist.onrender.com']


# These must be provided by hosting
# Example: ALLOWED_HOSTS=mydomain.com
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
