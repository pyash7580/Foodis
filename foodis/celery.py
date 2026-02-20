"""
Celery configuration for foodis project.
"""
import os
from celery import Celery
from celery.schedules import crontab
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodis.settings')

app = Celery('foodis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cancel-unpaid-orders': {
        'task': 'client.tasks.cancel_unpaid_orders',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    'update-restaurant-ratings': {
        'task': 'client.tasks.update_restaurant_ratings',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
    'send-order-reminders': {
        'task': 'client.tasks.send_order_reminders',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'update-trending-items': {
        'task': 'client.tasks.update_trending_items',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-old-otps': {
        'task': 'client.tasks.cleanup_old_otps',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    'generate-daily-reports': {
        'task': 'client.tasks.generate_daily_reports',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
