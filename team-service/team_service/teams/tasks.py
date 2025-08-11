from celery import shared_task
from datetime import date
from .models import TeamApplication

@shared_task
def expire_old_team_applications():
    print("TASK RAN!!!!!!!!!!!!")
    today = date.today()
    expired_teams = TeamApplication.objects.filter(status='open', hackathon_date__lt=today)

    count = expired_teams.update(status='expired')
    print(f"[CRON] Marked {count} teams as expired.")
