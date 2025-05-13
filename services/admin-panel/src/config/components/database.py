import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "django"),
        "USER": os.getenv("POSTGRES_USER", "django"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("POSTGRES_HOST", ""),
        "PORT": os.getenv("POSTGRES_PORT", 5432),
        "OPTIONS": {"options": "-c search_path=public,profile"},
    }
}
