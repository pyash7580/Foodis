"""
Development settings with SQLite for easier setup
"""
from .settings import *

# Override database to use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Simplified Redis config (can work without Redis for basic testing)
# Comment out if Redis is not available
try:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
except:
    # Fallback to local memory cache if Redis not available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Disable Celery for basic testing (comment out if you have Redis/Celery)
CELERY_TASK_ALWAYS_EAGER = True  # Run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True

