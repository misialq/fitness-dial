"""
Django settings for withconn project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.utils.log import DEFAULT_LOGGING

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS")
if "," in ALLOWED_HOSTS:
    ALLOWED_HOSTS = ALLOWED_HOSTS.split(",")
else:
    ALLOWED_HOSTS = [ALLOWED_HOSTS]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "connector.apps.ConnectorConfig",
    "django_celery_beat",
    "import_export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "request_logging.middleware.LoggingMiddleware",
]

ROOT_URLCONF = "withconn.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates/")],
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

WSGI_APPLICATION = "withconn.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DB_NAME = os.getenv("POSTGRES_DB", "testdb")
DB_USER = os.getenv("POSTGRES_USER", "test")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "test")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "PORT": DB_PORT,
        "HOST": DB_HOST,
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(
    PROJECT_ROOT, "static"
)  # static files will be collected into here
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "boot"),
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] [{asctime}] [{module}] [process-{process:d}] [thread-{thread:d}] {message}",
            "style": "{",
        },
        "simple": {"format": "[{levelname}] {message}", "style": "{",},
        "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL,},
    "loggers": {
        "django": {"level": LOG_LEVEL, "handlers": ["console"], "propagate": True,},
        "django.request": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        "connector": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
    },
}
