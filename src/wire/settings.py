"""
Django settings for wire project — Django 5.2.4
Clean, production-ready version (Decouple + NeonDB + WhiteNoise + Crispy + Allauth)
"""

from pathlib import Path
from decouple import config, Csv
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,raymon-postcerebellar-percy.ngrok-free.dev",
    cast=Csv(),
)


INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Your apps
    "saas",
    "commando",
    "customers",
    "profiles",
    "subscriptions",
    "helpcenter",
    "chatbot",

    # Third-party
    "crispy_forms",
    "crispy_tailwind",
    "widget_tweaks",
    "storages",
    "tailwind",
    "allauth_ui",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "slippers",
]


# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "wire.urls"
WSGI_APPLICATION = "wire.wsgi.application"


# ---------------------------------------------------------------------
# Database (NeonDB via Decouple)
# ---------------------------------------------------------------------
DATABASE_URL = config("DATABASE_URL")
CONN_MAX_AGE = config("CONN_MAX_AGE", default=600, cast=int)

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=CONN_MAX_AGE,
        conn_health_checks=True,
        ssl_require=True,  # Neon requires SSL
    )
}


# ---------------------------------------------------------------------
# Storage (Django 5+ unified)
# ---------------------------------------------------------------------
STORAGES = {
    # Default file storage for uploads
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": BASE_DIR / "media"},
    },
    # Static files (with WhiteNoise compression)
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Extra dirs for collectstatic
STATICFILES_BASE_DIR = BASE_DIR / "static"
STATICFILES_BASE_DIR.mkdir(exist_ok=True, parents=True)
STATICFILES_VENDORS_DIR = STATICFILES_BASE_DIR / "vendors"
STATICFILES_DIRS = [STATICFILES_BASE_DIR, STATICFILES_VENDORS_DIR]


# ---------------------------------------------------------------------
# Authentication / Allauth
# ---------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[wire]"
ACCOUNT_LOGIN_BY_CODE_ENABLED = True

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": config("OAUTH_GITHUB_CLIENT_ID"),
            "secret": config("OAUTH_GITHUB_SECRET"),
        },
        "SCOPE": ["user", "repo", "read:org"],
    },
    "google": {
        "APP": {
            "client_id": config("OAUTH_GOOGLE_CLIENT_ID"),
            "secret": config("OAUTH_GOOGLE_SECRET"),
        }
    }
}

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
}

GROQ_API_KEY = config("GROQ_API_KEY")


# ---------------------------------------------------------------------
# Crispy Forms
# ---------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = ["tailwind"]
CRISPY_TEMPLATE_PACK = "tailwind"


# ---------------------------------------------------------------------
# Email (Gmail SMTP)
# ---------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")


# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------
# Auth Redirects
# ---------------------------------------------------------------------
LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"


# ---------------------------------------------------------------------
# Security best practices
# ---------------------------------------------------------------------
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True


# ---------------------------------------------------------------------
# Default primary key
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
