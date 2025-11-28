from .base import *  # noqa: F401,F403
import dj_database_url
import os

# Keep base DEBUG False by default (base.py should set DEBUG=False)
DEBUG = False

# Use env ALLOWED_HOSTS or fallback (must set ALLOWED_HOSTS in Render)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["c-regist.onrender.com"])

# Database: prefer DATABASE_URL from env (Render provides this)
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL", default=None),
        conn_max_age=600,
        ssl_require=True,
    )
}

# WhiteNoise - efficient static file serving
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Ensure collectstatic works with ManifestStaticFilesStorage
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"

# Security recommendations
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60  # set higher (e.g. 3600 or 31536000) after testing
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Trust Render's HTTPS termination - configure CSRF trusted origins from ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# Logging (basic)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
