from __future__ import absolute_import, unicode_literals

from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

app.conf.broker_url = "redis://localhost:6379/0"

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
