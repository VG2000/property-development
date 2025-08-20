import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

env = environ.Env()

# Only load a .env file if explicitly requested (or present)
ENV_FILE = os.environ.get("DJANGO_ENV_FILE")
if ENV_FILE:
    environ.Env.read_env(BASE_DIR / ENV_FILE)
elif (BASE_DIR / ".env").exists():
    environ.Env.read_env(BASE_DIR / ".env")  # optional, local dev convenience

SECRET_KEY = env("SECRET_KEY", default="not-so-secret-in-dev")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "land_registry",
    "projects",
    "users",
    "insights",
]

INSTALLED_APPS += [
    'widget_tweaks',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "property_development.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "property_development.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# 👇 This ensures your project-root /static folder (with css/output.css) is collected
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Media (LOCAL)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Allow embedding from same-origin (useful for iframed PDFs)
X_FRAME_OPTIONS = "SAMEORIGIN"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging config from environment
LOG_LEVEL = env("LOG_LEVEL", default="WARNING")
LOG_FILE = env("LOG_FILE", default="logs/django.log")

# Ensure logs directory exists
LOG_DIR = Path(LOG_FILE).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name} {message}", "style": "{"},
        "simple": {"format": "{levelname}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "file": {"level": LOG_LEVEL, "class": "logging.FileHandler", "filename": LOG_FILE, "formatter": "verbose"},
    },
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": LOG_LEVEL, "propagate": True},
        "land_registry": {"handlers": ["console", "file"], "level": LOG_LEVEL, "propagate": False},
    },
}

# Authentication
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "projects-list"    # after successful login
LOGOUT_REDIRECT_URL = "insights"           # after logout
