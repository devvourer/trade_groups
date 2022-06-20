import os

from datetime import timedelta

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ['trusttrade.pro', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'djoser',
    'debug_toolbar',
    'corsheaders',
    'import_export',

    # 2fa
    'django_otp',
    'django_otp.plugins.otp_totp',

    # apps
    'apps.users.apps.UsersConfig',
    'apps.copytrade.apps.CopytradeConfig',
    'apps.telegram_bot.apps.TelegramBotConfig',
    'apps.payments.apps.PaymentsConfig',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'sky_invest_trading.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sky_invest_trading.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASS'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'users.User'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = config('EMAIL_USER')
EMAIL_HOST = 'smtp.yandex.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')


REST_FRAMEWORK = {
    'DEFAULT_PERMISSIONS_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissions'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),

}

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'confirm-password?token={token}&id={uid}',
    'ACTIVATION_URL': 'activated?token={token}&id={uid}',
    'SEND_ACTIVATION_EMAIL': True,

    'SERIALIZERS': {
        'user': 'apps.users.serializers.UserSerializer',
        # 'user_create': 'apps.users.serializers.UserRegisterSerializer',
        'current_user': 'apps.users.serializers.UserSerializer',
    },
    'EMAIL': {
        'activation': 'apps.users.email.ActivationEmail',
        'password_reset': 'apps.users.email.PasswordResetEmail'
    }

}

CORS_ORIGIN_ALLOW_ALL = True


INTERNAL_IPS = [
    '127.0.0.1',
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'register': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/register.log'
        },
        'payment_tether': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/payment_tether'
        },
        'withdraw': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/withdraw'
        },
        'withdraw_from_groups': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/withdraw_from_groups'
        }
    },
    'loggers': {
        'register': {
            'level': 'INFO',
            'handlers': ['register'],
            'propagate': True
        },
        'payment_tether': {
            'level': 'WARNING',
            'handlers': ['payment_tether'],
            'propagate': True
        },
        'withdraw': {
            'level': 'WARNING',
            'handlers': ['withdraw'],
            'propagate': True
        },
        'withdraw_from_groups': {
            'level': 'WARNING',
            'handlers': ['withdraw'],
            'propagate': True
        }
    }
}


# Yomoney
YOOMONEY_POCKET = config('YOOMONEY_POCKET')
YOOMONEY_SECRET = config('YOOMONEY_SECRET')


CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672/'


BINANCE_API = config('BINANCE_API')
BINANCE_SECRET = config('BINANCE_SECRET')

CSRF_TRUSTED_ORIGINS = ['https://trusttrade.pro']
