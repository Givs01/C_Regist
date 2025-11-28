import os

env = os.environ.get("DJANGO_ENV", "dev")  # default to dev

if env == "prod":
    from .prod import *
else:
    from .dev import *
