import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

include(
    "components/apps.py",
    "components/middleware.py",
    "components/database.py",
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

DEBUG = os.getenv("DJANGO_DEBUG") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split()

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "accounts.auth.EmailAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_BASE_URL = os.getenv("AUTH_BASE_URL")
LOGIN_PATH = os.getenv("LOGIN_PATH")
LOGIN_URL = f"{AUTH_BASE_URL}{LOGIN_PATH}"

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGGING = {
    "version": 1,
    # не трогаем логгеры Django/сторонних библиотек
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",  # или "verbose" если нужен таймстамп и имя логгера
        },
    },
    "loggers": {
        # Ваше приложение
        "accounts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        # Django core (по умолчанию WARN+)
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
