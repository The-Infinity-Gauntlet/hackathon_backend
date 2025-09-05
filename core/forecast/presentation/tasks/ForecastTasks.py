from celery import shared_task
from core.forecast.infra.repository import ForecastRepoImpl
from core.forecast.app.services import floodingPredict

@shared_task
def forecast():
    repo = ForecastRepoImpl()
    floodingPredict(repo)
