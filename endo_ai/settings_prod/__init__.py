import os
from endoreg_db_api.utils import DbConfig
from endoreg_db_api.settings_base import (
    BASE_DIR,
    CONF_DIR,
    DEBUG,
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
    DEFAULT_AUTO_FIELD,
    STATIC_ROOT,
    STATICFILES_DIRS,
)

DB_CFG_FILE = CONF_DIR / "db.yaml"

SECRET_KEY = "django-insecure-ehohvfo*#^_blfeo_n$p31v2+&ylp$(1$96d%5!0y(-^l28x-6"
ALLOWED_HOSTS = ["*"]


db_config: DbConfig = DbConfig.from_file(DB_CFG_FILE)

DATABASES = {
    "default": {
        "ENGINE": db_config.engine,
        "NAME": db_config.name,
        "USER": db_config.user,
        "PASSWORD": db_config.password,
        "HOST": db_config.host,
        "PORT": str(db_config.port),
    }
}
