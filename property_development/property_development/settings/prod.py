from . import base

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = base.env.list("ALLOWED_HOSTS", default=["vincegomez.com"])
