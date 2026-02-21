"""
Django settings for foodis project.
"""

from pathlib import Path
from decouple import config
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# Production Deployment Settings
# Format requested for Render + Neon
SECRET_KEY = config('SECRET_KEY', default='strong_random_key_foodis_2026')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='foodis-jpvq.onrender.com,foodis-backend.onrender.com,localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

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
    'corsheaders',
    'django_filters',
    'core',
    'client',
    'restaurant',
    'rider_legacy',
    'rider',
    'admin_panel',
    'ai_engine',
    'rest_framework_simplejwt',
]

# Optional apps - add if installed
try:
    import daphne
    INSTALLED_APPS.insert(0, 'daphne')
except ImportError:
    pass

try:
    import channels
    INSTALLED_APPS.append('channels')
except ImportError:
    pass

try:
    import django_celery_beat
    INSTALLED_APPS.append('django_celery_beat')
except ImportError:
    pass

try:
    import django_celery_results
    INSTALLED_APPS.append('django_celery_results')
except ImportError:
    pass

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RoleAwareMiddleware',
]

ROOT_URLCONF = 'foodis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'rider' / 'templates'],
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

WSGI_APPLICATION = 'foodis.wsgi.application'

# ASGI application (only if channels is installed)
try:
    import channels
    ASGI_APPLICATION = 'foodis.asgi.application'
except ImportError:
    pass

# Database
# Neon PostgreSQL Configuration
USE_POSTGRES = config('USE_POSTGRES', default=True, cast=bool)

if USE_POSTGRES:
    import dj_database_url
    DATABASE_URL = config('DATABASE_URL', default='')
    if DATABASE_URL:
        # Neon requires SSL, which is encoded in the DATABASE_URL ?sslmode=require
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    else:
        # Fallback to manual components if DATABASE_URL is missing
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config('DB_NAME', default='neondb'),
                'USER': config('DB_USER', default='neondb_owner'),
                'PASSWORD': config('DB_PASSWORD', default='npg_8djsPyMJSYV7'),
                'HOST': config('DB_HOST', default='ep-holy-mouse-aipoipo6-pooler.c-4.us-east-1.aws.neon.tech'),
                'PORT': config('DB_PORT', default='5432'),
                'OPTIONS': {
                    'sslmode': 'require',
                }
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Production Security Hardening
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://foodis-pi.vercel.app', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

# Redis Configuration
# Default to None to avoid accidental local connections in production
REDIS_URL = config('REDIS_URL', default=None)

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Use Redis for cache in production IF valid REDIS_URL is provided
if not DEBUG and REDIS_URL and 'localhost' not in REDIS_URL and '127.0.0.1' not in REDIS_URL:
    try:
        import redis
        CACHES['default'] = {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    except ImportError:
        pass

# Channel Layers (only if channels is installed) - Failsafe for Render Free tier
try:
    import channels
    # Only use RedisChannelLayer if a real remote Redis URL is provided
    if not DEBUG and REDIS_URL and 'localhost' not in REDIS_URL and '127.0.0.1' not in REDIS_URL:
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [REDIS_URL],
                },
            },
        }
    else:
        # Fallback to InMemory for local or Render without Redis service
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
            },
        }
except ImportError:
    CHANNEL_LAYERS = {}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Simple JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='https://foodis-pi.vercel.app,http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
CORS_ALLOW_CREDENTIALS = True

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-role',
    'x-device-id',
]

# Google Maps API
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# Razorpay Configuration
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

# Celery Configuration
try:
    import celery
    if REDIS_URL and 'localhost' not in REDIS_URL and '127.0.0.1' not in REDIS_URL:
        CELERY_BROKER_URL = REDIS_URL
        try:
            import django_celery_results
            CELERY_RESULT_BACKEND = 'django-db'
        except ImportError:
            CELERY_RESULT_BACKEND = REDIS_URL
    else:
        # Failsafe: Use eager tasks if no Redis is found
        CELERY_TASK_ALWAYS_EAGER = True
    
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    
    # In production, use real Celery IF configured. In development/debug, remain eager.
    if not hasattr(locals(), 'CELERY_TASK_ALWAYS_EAGER'):
        CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=DEBUG, cast=bool)
    CELERY_TASK_EAGER_PROPAGATES = True
except ImportError:
    pass

# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5

# MSG91 SMS Configuration
MSG91_API_KEY = config('MSG91_API_KEY', default=None)
MSG91_TEMPLATE_ID = config('MSG91_TEMPLATE_ID', default=None)

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Order Settings
ORDER_CANCELLATION_TIME_LIMIT = 525600  # 1 Year (Effectively Removed)
RIDER_ASSIGNMENT_RADIUS = 5  # km
COMMISSION_PERCENTAGE = 15  # percentage

# AI Engine Settings
AI_ENGINE_ENABLED = config('AI_ENGINE_ENABLED', default=True, cast=bool)
