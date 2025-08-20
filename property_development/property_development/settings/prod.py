from .base import *  # noqa: F403,F401

DEBUG = env("DEBUG", default=False)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Tell Django about the proxy's TLS header (Nginx sets X-Forwarded-Proto)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Strong HSTS (set once certs are working)
SECURE_HSTS_SECONDS = 31536000          # (1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Sensible modern defaults
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["wales.vincegomez.com"])
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["https://wales.vincegomez.com"],
)
LOGGING["handlers"]["console"]["level"] = "INFO"
LOGGING["loggers"]["django"]["handlers"] = ["console"]
LOGGING["loggers"]["land_registry"]["handlers"] = ["console"]
