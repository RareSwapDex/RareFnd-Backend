"""
Django settings for RareFND project.

Generated by 'django-admin start-project' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, "files")
MEDIA_URL = "files/"


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

RAREFND_URL = "https://www.rarefnd.com/"

ALLOWED_HOSTS = [
    "rarefndapi.herokuapp.com",
    "127.0.0.1",
    "localhost",
    "bb41-2-50-43-16.ngrok.io",
    "192.168.0.92",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "RareFndApp.apps.RarefndappConfig",
    "rest_framework",
    "corsheaders",
    "ckeditor",
    "web3",
    "eth_defi",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_email_verification",
    "storages",
    "requests",
    # "coinbase_commerce",
]


def verified_callback(user):
    user.is_active = True


EMAIL_VERIFIED_CALLBACK = verified_callback
EMAIL_FROM_ADDRESS = config("EMAIL_FROM_ADDRESS")
EMAIL_MAIL_SUBJECT = "Confirm your email {{ user.username }}"
EMAIL_MAIL_HTML = "email_verification.html"
EMAIL_MAIL_PLAIN = "email_verification_plain.txt"
EMAIL_TOKEN_LIFE = 60 * 60 * 24
EMAIL_PAGE_TEMPLATE = "email_verificationcheck_token.html"
EMAIL_PAGE_DOMAIN = "https://rarefndapi.herokuapp.com"
EMAIL_MULTI_USER = True  # optional (defaults to False)

# For Django Email Backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.office365.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = config("EMAIL_FROM_ADDRESS")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # higher than the count of fields


AUTH_USER_MODEL = "RareFndApp.User"


CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "CMS",
        "width": "100%",
        "toolbar_CMS": [
            ["Format", "Styles", "FontSize"],
            ["Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript"],
            ["TextColor", "BGColor"],
            ["Link", "Unlink"],
            ["JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock"],
            ["Undo", "Redo"],
            ["Copy", "Paste", "PasteText", "PasteFromWord"],
            ["SelectAll", "Find", "Replace"],
            ["NumberedList", "BulletedList"],
            ["Outdent", "Indent"],
            ["Smiley", "SpecialChar", "Blockquote", "HorizontalRule"],
            ["Table", "Image", "Html5video", "Youtube"],
            ["ShowBlocks", "Source", "About"],
        ],
        "extraPlugins": ",".join(["youtube", "html5video"]),
    },
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "RareFND.urls"

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

WSGI_APPLICATION = "RareFND.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    # "default": {
    #     "ENGINE": "django.db.backends.sqlite3",
    #     "NAME": BASE_DIR / "db.sqlite3",
    # }
    # "default": {
    #     "ENGINE": "django.db.backends.postgresql",
    #     "NAME": "postgres",
    #     "USER": "rarefnd",
    #     "PASSWORD": "rarefnd",
    #     "HOST": "localhost",
    #     "PORT": "5432",
    # }
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "d8q7g3cng193np",
        "USER": config("DATABASE_USER"),
        "PASSWORD": config("DATABASE_PASSWORD"),
        "HOST": "ec2-3-219-19-205.compute-1.amazonaws.com",
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ORIGIN_ALLOW_ALL = True

TEMPLATE_DIRS = (os.path.join(BASE_DIR, "/RareFndApp/templates"),)

# CORS_ORIGIN_WHITELIST = (
#     'http://localhost:3001',
#     'http://localhost:3000',
#     'https://main--chic-sopapillas-1becfe.netlify.app'
# )

# S3 BUCKETS CONFIG
AWS_QUERYSTRING_AUTH = False
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = "rarefnd-bucket"
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_REGION_NAME = "us-east-2"
AWS_S3_SIGNATURE_VERSION = "s3v4"

# Venly creds
CLIENT_ID = config("VENLY_CLIENT_ID")
CLIENT_SECRET = config("VENLY_CLIENT_SECRET")
