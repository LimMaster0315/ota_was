import json
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default):
    value = os.getenv(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def load_ota_download_map():
    raw_map = os.getenv("OTA_DOWNLOAD_MAP", '{"ml":"ml/C3_EasyIoT_M3_L3_OTA.bin"}')
    try:
        parsed = json.loads(raw_map)
    except json.JSONDecodeError as exc:
        raise ImproperlyConfigured("OTA_DOWNLOAD_MAP must be valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise ImproperlyConfigured("OTA_DOWNLOAD_MAP must be a JSON object.")

    download_map = {}
    for key, value in parsed.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ImproperlyConfigured("OTA_DOWNLOAD_MAP keys and values must be strings.")
        clean_key = key.strip("/")
        if not clean_key:
            raise ImproperlyConfigured("OTA_DOWNLOAD_MAP cannot contain an empty route key.")
        download_map[clean_key] = value

    return download_map


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-secret-key")
DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["*"])

INSTALLED_APPS = [
    "ota",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

OTA_FILE_ROOT = Path(os.getenv("OTA_FILE_ROOT", BASE_DIR / "ota_files")).resolve()
OTA_DOWNLOAD_MAP = load_ota_download_map()
