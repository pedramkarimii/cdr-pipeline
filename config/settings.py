from pathlib import Path

from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent
APPLICATIONS = ["cdr", "core"]


def csv(name: str, default: str = "") -> list[str]:
    return [
        value.strip()
        for value in config(name, default=default).split(",")
        if value.strip()
    ]


SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool, default=False)
TIME_ZONE = config("TIME_ZONE", default="Asia/Tehran")
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

ALLOWED_HOSTS = csv("ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = csv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:8082,http://127.0.0.1:8082",
)

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_elasticsearch_dsl",
    *[f"apps.{app}" for app in APPLICATIONS],
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "default": "60/min",
        "admin": "120/min",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "CDR Pipeline API",
    "DESCRIPTION": "Call Detail Record ingestion, processing, and search API.",
    "VERSION": "1.0.0",
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="cdr"),
        "USER": config("DB_USER", default="cdr"),
        "PASSWORD": config("DB_PASSWORD", default="cdr"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", cast=int, default=60),
    },
}

REDIS_URL = config(
    "REDIS_URL",
    default="redis://{}:{}/0".format(
        config("REDIS_HOST", default="redis"),
        config("REDIS_PORT", default="6379"),
    ),
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}

CELERY_BROKER_URL = config(
    "CELERY_BROKER_URL",
    default="amqp://{}:{}@{}:{}/%2F".format(
        config("RABBITMQ_USER", default="guest"),
        config("RABBITMQ_PASSWORD", default="guest"),
        config("RABBITMQ_HOST", default="rabbitmq"),
        config("RABBITMQ_PORT", default="5672"),
    ),
)
CELERY_RESULT_BACKEND = config(
    "CELERY_RESULT_BACKEND",
    default="redis://{}:{}/1".format(
        config("REDIS_HOST", default="redis"),
        config("REDIS_PORT", default="6379"),
    ),
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

ELASTICSEARCH_HOST = config(
    "ELASTICSEARCH_HOST",
    default="http://elasticsearch:9200",
)
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": ELASTICSEARCH_HOST,
    },
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "storage" / "static_collected"
STATICFILES_DIRS = [BASE_DIR / "storage" / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "storage" / "media"

LOG_LEVEL = config("API_LOG_LEVEL", default="INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
}

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool, default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", cast=bool, default=False)
