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
    CORS_ALLOWED_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CSRF_TRUSTED_ORIGINS,
    ROOT_URLCONF,
    BASE_API_URL, #for api/endpoint url
    #for keycloak
    KEYCLOAK_SERVER_URL,
    KEYCLOAK_REALM,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_CLIENT_SECRET,
    KEYCLOAK_OPENID_CONFIG_URL,
    keycloak_openid,
    REST_FRAMEWORK,
    ENABLE_KEYCLOAK_AUTH



)

DEBUG = True

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
    "DEBUG",
    "DATABASES",
    "ALLOWED_HOSTS",
]
