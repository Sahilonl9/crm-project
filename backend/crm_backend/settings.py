import os                              # os environment setup 
from pathlib import Path               # cleaner path handling 
from datetime import timedelta         # token expiry
from dotenv import load_dotenv          # loan .env file in the environment

load_dotenv()   # 


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-p(4m@=u9zcp^7y-+jg%k560z2on(%y4l+38pt&$%udo21qq7*='          # we could hid it in env file 

DEBUG = True            

ALLOWED_HOSTS = ['*']           # allowed domain name here

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',                                         # enable api devlopment
    'rest_framework_simplejwt',                               # jwt authentication system
    'rest_framework_simplejwt.token_blacklist',               # token expiry (logout)
    'corsheaders',                                            #handle frontrnd-backend commn
    'channels',                                                # enable websocket (chat)
    'users',
    'leads',
    'chat',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # cross handling origin 
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

ASGI_APPLICATION = 'crm_backend.asgi.application'                   # webscoket

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',               
        'NAME': os.environ.get('DB_NAME', 'crm_database'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',      # forntend server
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True    

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',          # generate key
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',      # permission 
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',  # limit api response size
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS':  True,
    'BLACKLIST_AFTER_ROTATION': True,   # 
    'ALGORITHM': 'HS256',
    'USER_ID_FIELD': 'id',              # 
    'USER_ID_CLAIM': 'user_id',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://default:gQAAAAAAAVAKAAIncDFkMjE0YjYyZjEyOWI0NDg4OTQ0ZmZhOWM1NWQyNzJlMHAxODYwMjY@rested-pangolin-86026.upstash.io:6379'],  # 
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # ✅ fixed typo