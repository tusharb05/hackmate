from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule

class Command(BaseCommand):
    help = 'Sets up periodic tasks like expiring old team applications'

    def handle(self, *args, **kwargs):
        schedule, _ = CrontabSchedule.objects.get_or_create(minute="0", hour="0")
        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name="Expire old team applications",
            task="teams.tasks.expire_old_team_applications",
        )
        if created:
            self.stdout.write("✅ Periodic task created.")
        else:
            self.stdout.write("ℹ️ Periodic task already exists.")
