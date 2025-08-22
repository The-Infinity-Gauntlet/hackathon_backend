from core.forecast.infra.services.forecast import runForecast
from core.forecast.domain.repository import MachineLearningRepository

def floodingPredict(repo: MachineLearningRepository):
    runForecast(repo)