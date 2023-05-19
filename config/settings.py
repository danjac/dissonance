import pathlib
from email.utils import getaddresses

import environ

# Default flags
env = environ.Env(
    DEBUG=(bool, False),
)

BASE_DIR = pathlib.Path(__file__).resolve(strict=True).parent.parent

environ.Env.read_env(BASE_DIR / ".env")

# Development settings

DEBUG = env("DEBUG")

SECRET_KEY = env.str(
    "SECRET_KEY",
    default="django-insecure-+-pzc(vc+*=sjj6gx84da3y-2y@h_&f=)@s&fvwwpz_+8(ced^",
)

INSTALLED_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.forms",
    "heroicons",
    "dissonance.chatrooms",
]


MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
]

# Databases

CONN_MAX_AGE = env.int("CONN_MAX_AGE", default=0)

DATABASES = {
    "default": {
        **env.db(default="postgresql://postgres:password@127.0.0.1:5432/postgres"),
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": CONN_MAX_AGE,
        "CONN_HEALTH_CHECKS": CONN_MAX_AGE > 0,
    }
}

# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


# prevent deprecation warnings
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Server settings

ASGI_APPLICATION = "config.asgi.application"

ROOT_URLCONF = "config.urls"

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

SITE_ID = 1

# Session and cookies

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email configuration

EMAIL_HOST = env.str("EMAIL_HOST", default="127.0.0.1")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_PORT = env.int("EMAIL_PORT", default=1025)

EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default=None)
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default=None)

EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)

ADMINS = getaddresses(env.list("ADMINS", default=[]))

SERVER_EMAIL = env.str("SERVER_EMAIL", default=f"errors@{EMAIL_HOST}")
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default=f"no-reply@{EMAIL_HOST}")

# authentication settings
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends

LOGIN_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# admin settings

ADMIN_URL = env.str("ADMIN_URL", default="admin/")

# Internationalization/Localization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files

STATIC_URL = env.str("STATIC_URL", default="/static/")
# STATICFILES_DIRS = [BASE_DIR / "static"]
# STATIC_ROOT = BASE_DIR / "staticfiles"

# Templates
# https://docs.djangoproject.com/en/1.11/ref/forms/renderers/

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "django.request": {
            "level": "CRITICAL",
            "propagate": False,
        },
    },
}
