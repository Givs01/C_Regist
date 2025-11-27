# core/settings/prod.py

from .base import *

# Production settings
DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["c-regist.onrender.com"])

# Use SQLite for production (same as dev, for simplicity in this case)
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',  # SQLite database in the project directory
}

# Static and media files setup
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"  # Collected static files are stored here

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # User-uploaded files will be stored here

# Security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging setup (optional, can be used for production logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django_error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
