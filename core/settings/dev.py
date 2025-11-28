from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Add livereload for local dev only
INSTALLED_APPS += ["livereload"]
MIDDLEWARE += ["livereload.middleware.LiveReloadScript"]

# Use sqlite by default if DATABASE_URL not provided via .env
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}
