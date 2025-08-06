from .base import *  # noqa: F403,F401

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["yourdomain.com"])
