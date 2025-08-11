from celery import Celery
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "team_service.settings")

from django.conf import settings


app = Celery(
    'team_service',
    broker=settings.CELERY_BROKER_URL,  # or your RabbitMQ URL
    # backend='rpc://'
)

app.conf.task_routes = {
    'teams.tasks.expire_old_team_applications': {
        'queue': 'team-tasks',
        'routing_key': 'team-tasks'
    }
}

app.conf.beat_schedule = {
    'expire-old-teams-daily': {
        'task': 'teams.tasks.expire_old_team_applications',
        'schedule': 86400.0,
        'options': {
            'queue': 'team-tasks',
            'routing_key': 'team-tasks'
        }
    }
}


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
