from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development")

app = Celery("mysite")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "clear-expired-sessions-every-day": {
        "task": "bookshop.tasks.clear_expired_sessions",
        "schedule": crontab(hour=0, minute=0),
    },
    "generate-daily-report": {
        "task": "bookshop.tasks.generate_daily_sales_report",
        "schedule": crontab(hour=23, minute=50),
    },
}
