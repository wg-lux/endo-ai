from endo_ai.settings_base import (
    BASE_DIR,
    CONF_DIR,
    INSTALLED_APPS,
    MIDDLEWARE,
    ROOT_URLCONF,
    TEMPLATES,
    AUTH_PASSWORD_VALIDATORS,
    LANGUAGE_CODE,
    TIME_ZONE,
    USE_I18N,
    USE_TZ,
    STATIC_URL,
    STATIC_ROOT,
    DEFAULT_AUTO_FIELD,
    STATICFILES_DIRS,
    MEDIA_ROOT,
    MEDIA_URL,
)

DEBUG = True
SECRET_KEY = "django-insecure-ehohvfo*#^_blfeo_n$p31v2+&ylp$(1$96d%5!0y(-^l28x-6"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

ALLOWED_HOSTS = ["*"]

__all__ = [
    "BASE_DIR",
    "CONF_DIR",
    "DEBUG",
    "INSTALLED_APPS",
    "MIDDLEWARE",
    "ROOT_URLCONF",
    "TEMPLATES",
    "AUTH_PASSWORD_VALIDATORS",
    "LANGUAGE_CODE",
    "TIME_ZONE",
    "USE_I18N",
    "USE_TZ",
    "STATIC_URL",
    "STATIC_ROOT",
    "DEFAULT_AUTO_FIELD",
    "STATICFILES_DIRS",
    "MEDIA_ROOT",
    "MEDIA_URL",
    "SECRET_KEY",
    "DEBUG",
    "DATABASES",
    "ALLOWED_HOSTS",
]
