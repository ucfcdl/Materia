# celery.py
import os

from celery import Celery

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "materia.settings.base")

app = Celery("core.tasks")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = settings.TIME_ZONE

app.conf.task_queues = {
    "celery_queue": {
        "exchange": "celery_queue",
        "routing_key": "celery_queue",
    }
}
app.autodiscover_tasks()
