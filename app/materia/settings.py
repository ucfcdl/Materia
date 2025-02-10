"""
Django settings for materia project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DIRS = {
    "media": os.path.realpath(os.path.join(APP_PATH, "media")),  # + os.sep,
    "media_uploads": os.path.realpath(
        os.path.join(APP_PATH, "media", "uploads")
    ),  # + os.sep,
    "widgets": os.path.realpath(
        os.path.join(APP_PATH, "staticfiles", "widget")
    ),  # + os.sep
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "materia-local-dev-secret-key"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # apps
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "materia.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "materia.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "HOST": os.environ.get("MYSQL_HOST"),
        "PORT": os.environ.get("MYSQL_PORT"),
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Eastern"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

MEDIA_URL = "/media/"

# figure out how to get images working

STATIC_URL = "/static/"
STATIC_ROOT = "./staticfiles/"

# STATIC_URL = "/"
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "public"),
# ]

URLS = {
    "BASE_URL": "http://localhost:420/",
    "WIDGET_URL": "http://localhost:420/widget/",
    "STATIC_CROSSDOMAIN": "http://localhost:420/",
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "./logfile.log",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["file", "console"], "level": "INFO", "propagate": True},
        "django.db": {
            "handlers": ["file", "console"],
            "level": "ERROR",  # change to DEBUG to see all queries
        },
    },
}

SEMESTERS = [
    {
        "spring": {
            "month": 1,
            "day": 1
        },
        "summer": {
            "month": 5,
            "day": 3
        },
        "fall": {
            "month": 8,
            "day": 7
        }
    }
]

WIDGETS = [
    {
        "id": 1,
        "package": "https://github.com/ucfopen/crossword-materia-widget/releases/latest/download/crossword.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/crossword-materia-widget/releases/latest/download/crossword-build-info.yml",  # noqa:E501
    },
    {
        "id": 2,
        "package": "https://github.com/ucfopen/guess-the-phrase-materia-widget/releases/latest/download/guess-the-phrase.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/guess-the-phrase-materia-widget/releases/latest/download/guess-the-phrase-build-info.yml",  # noqa:E501
    },
    {
        "id": 3,
        "package": "https://github.com/ucfopen/matching-materia-widget/releases/latest/download/matching.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/matching-materia-widget/releases/latest/download/matching-build-info.yml",  # noqa:E501
    },
    {
        "id": 4,
        "package": "https://github.com/ucfopen/enigma-materia-widget/releases/latest/download/enigma.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/enigma-materia-widget/releases/latest/download/enigma-build-info.yml",  # noqa:E501
    },
    {
        "id": 5,
        "package": "https://github.com/ucfopen/labeling-materia-widget/releases/latest/download/labeling.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/labeling-materia-widget/releases/latest/download/labeling-build-info.yml",  # noqa:E501
    },
    {
        "id": 6,
        "package": "https://github.com/ucfopen/flash-cards-materia-widget/releases/latest/download/flash-cards.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/flash-cards-materia-widget/releases/latest/download/flash-cards-build-info.yml",  # noqa:E501
    },
    {
        "id": 7,
        "package": "https://github.com/ucfopen/this-or-that-materia-widget/releases/latest/download/this-or-that.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/this-or-that-materia-widget/releases/latest/download/this-or-that-build-info.yml",  # noqa:E501
    },
    {
        "id": 8,
        "package": "https://github.com/ucfopen/word-search-materia-widget/releases/latest/download/word-search.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/word-search-materia-widget/releases/latest/download/word-search-build-info.yml",  # noqa:E501
    },
    {
        "id": 9,
        "package": "https://github.com/ucfopen/adventure-materia-widget/releases/latest/download/adventure.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/adventure-materia-widget/releases/latest/download/adventure-build-info.yml",  # noqa:E501
    },
    {
        "id": 10,
        "package": "https://github.com/ucfopen/equation-sandbox-materia-widget/releases/latest/download/equation-sandbox.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/equation-sandbox-materia-widget/releases/latest/download/equation-sandbox-build-info.yml",  # noqa:E501
    },
    {
        "id": 11,
        "package": "https://github.com/ucfopen/sort-it-out-materia-widget/releases/latest/download/sort-it-out.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/sort-it-out-materia-widget/releases/latest/download/sort-it-out-build-info.yml",  # noqa:E501
    },
    {
        "id": 12,
        "package": "https://github.com/ucfopen/survey-materia-widget/releases/latest/download/simple-survey.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/survey-materia-widget/releases/latest/download/simple-survey-build-info.yml",  # noqa:E501
    },
    {
        "id": 13,
        "package": "https://github.com/ucfopen/sequencer-materia-widget/releases/latest/download/sequencer.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/sequencer-materia-widget/releases/latest/download/sequencer-build-info.yml",  # noqa:E501
    },
    {
        "id": 14,
        "package": "https://github.com/ucfopen/syntax-sorter-materia-widget/releases/latest/download/syntax-sorter.wigt",  # noqa:E501
        "checksum": "https://github.com/ucfopen/syntax-sorter-materia-widget/releases/latest/download/syntax-sorter-build-info.yml",  # noqa:E501
    },
]
