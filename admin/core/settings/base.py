"""
Django settings for crypto_storage project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from .config import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.django.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.django.debug

ALLOWED_HOSTS = config.django.allowed_hosts

CSRF_TRUSTED_ORIGINS = config.django.csrf_trusted_origins
# Application definition

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000000

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    # 'django_celery_beat',
    # 'django_celery_results',
    "core",
    "users.apps.UsersConfig",
    "solana",
    "external_services",
]


AUTH_USER_MODEL = "users.User"  # new

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
#

# from django.db.backends.postgresql.psycopg_any import IsolationLevel
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.db.name,
        "USER": config.db.user,
        "PASSWORD": config.db.password,
        "HOST": config.db.host,  # имя вашего сервиса PostgreSQL в Docker Compose
        "PORT": config.db.port,
        # "OPTIONS": {
        #     "isolation_level": IsolationLevel.READ_UNCOMMITTED,
        # }
    }
}

MIGRATION_MODULES = {
    # "users": None,
    "solana": None,
    "external_services": None,
    # и другие приложения, которые ты не хочешь мигрировать
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",  # <-- будет использоваться для новых паролей
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
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
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=90),  # Время жизни access токена
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # Время жизни refresh токена
    "ROTATE_REFRESH_TOKENS": True,  # Генерация нового refresh токена при обновлении
    "BLACKLIST_AFTER_ROTATION": True,  # Устаревание старых refresh токенов
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

TIME_ZONE = config.django.time_zone
USE_TZ = True

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

USE_I18N = True
USE_L10N = True

LANGUAGE_CODE = "ru"  # Установите русский как основной язык

LANGUAGES = [
    ("en", "English"),
    ("ru", "Russian"),
    ('th', 'Thai'),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
    "C:\\Python\\Мои проекты\\CryptoStorage\\.venv\\Lib\\site-packages\\unfold\\",
]
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "core/static"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
