from .base import *  # noqa: F403,F401

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["wales.vincegomez.com"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["https://wales.vincegomez.com"])
