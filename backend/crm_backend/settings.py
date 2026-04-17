import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*'] # crm.domain.com


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'channels',
    'users', # we created this app for registration, login, jwt auth
    'leads', # CRUD, notes, dashboard
    'chat',  #conversations, messages, websocket consumer
]

MIDDLEWARE = [
    'corsheaders.middleware.Corsmiddleware', #security guard
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crm_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#WSGI_APPLICATION = 'crm_backend.wsgi.application' Not requied
ASGI_APPLICATION = 'crm_backend.asgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'crm_database',
        'USER' : 'root',
        'PASSWORD': 'password123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

AUTH_USER_MODEL = 'users.User'
# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173/',
    'http://127.0.0.1:5173',
]

CORS_ALLOWED_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  #each registerd user has its own token, and this line of code tells DRF to verify with it. sp, with jwtauth helps to read authorization bearer.
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthnticated', # this givs permission what they are allowed to do
    ),
    'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PagenNumberPagination', #20 leads per page 
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME' : timedelta(minutes=60), #short enough that a stolen token expires quickly
    'REFRESH_TOKEN_LIFETIME' : timedelta(days=7), #long enough that users dont get logged out constantly
    'ROTATE_REFRESH_TOKENS' : True, #Each refresh issues a brand new refresh token- old token is one time use only 
    'BACKLIST_AFTER_ROTATION' : True, #Invalidates used refreshed tokens- prevents token reuse attacks
    'ALGORITHM' : 'HS256', # HMAC-SHA256-fast, secure, industry-standard signing algorithm
    'USER_ID_FEILD': 'id', # which field on your User model is the unigue id
    'USER_ID_CLAIM':'user_id', # the key name inside the jwt payload that holds the userid
    'AUTH_HEADER_TYPES':('Bearer',), # React sends Authorization:bearer.... this tells DRF to look for the prefix
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND' : 'channels_redis.core.RedisChannelLayer',
        'CONFIG' : {
            'hosts' : ['redis-cli --tls -u redis://default:gQAAAAAAAVAKAAIncDFkMjE0YjYyZjEyOWI0NDg4OTQ0ZmZhOWM1NWQyNzJlMHAxODYwMjY@rested-pangolin-86026.upstash.io:6379']
        },
    },

}

DEFAULT_AUTO_FEILD = 'django.db.models.BigAutoFeild'