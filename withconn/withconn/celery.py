from __future__ import absolute_import, unicode_literals

import logging
import os

from celery import Celery
from . import celerysettings as cset


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "withconn.settings.prod")

CELERY_BROKER = os.environ.get("CELERY_BROKER")
app = Celery("withconn", broker=CELERY_BROKER)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.conf.update(
    task_queues=cset.task_queues,
    task_default_queue=cset.task_default_queue,
    task_serializer=cset.task_serializer,
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
