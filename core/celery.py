# http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html - django redis
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
# Configure Celery to use a specific log format and level
app.conf.update(
    task_track_started=True,
    task_time_limit=300,
    worker_redirect_stdouts_level='INFO',
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    task_annotations={'tasks.add': {'rate_limit': '10/m'}}
)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
 print('Request: {0!r}'.format(self.request))
