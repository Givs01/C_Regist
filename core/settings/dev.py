# core/settings/dev.py

from .base import *

# Development settings
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # Enable template debugging

# SQLite database for development
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',  # This creates the SQLite file in the base directory
}

# Static and media files for development
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # Add the "static" directory to be included during collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # This is for user-uploaded files

# Other settings for development
ALLOWED_HOSTS = ['*']  # Allow all hosts during development (change this in production)
SECRET_KEY = env("3y4y5nmgjfkfndb")
