from celery import shared_task
from datetime import date, timedelta

@shared_task
def enqueueDailyTask():
    from core.weather.infra.services.queue import enqueueFillClimates
    today = date.today()
    start = today - timedelta(days=7)
    end = today + timedelta(days=7)
    total, coords = enqueueFillClimates(start, end)
    print("Task executada para: ", coords)