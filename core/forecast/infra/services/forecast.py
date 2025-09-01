from core.forecast.domain.repository import MachineLearningRepository
from core.forecast.infra.models import Forecast
from core.occurrences.infra.models import Occurrence
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

def runForecast(repo: MachineLearningRepository):
    coords = repo.getCoords()
    for coord in coords:
        weathers = repo.getWeatherByCoord(coord["latitude"], coord["longitude"])
        condition = []
        floods = []            
        for weather in weathers:
            if None not in (
                weather.latitude, weather.longitude,
                weather.rain, weather.temperature,
                weather.humidity, weather.elevation,
                weather.pressure
            ):
                condition.append([
                    weather.latitude,
                    weather.longitude,
                    weather.rain,
                    weather.temperature,
                    weather.humidity,
                    weather.elevation,
                    weather.pressure
                ])
                has_occurrence = Occurrence.objects.filter(neighborhood=weather.neighborhood, date=weather.date).exists()
                floods.append(1 if (weather.rain > 10 and weather.humidity > 60 and weather.elevation < 10) or has_occurrence else 0)

        print("Tantos alagamentos: ", sum(floods))
        X_train, X_test, y_train, y_test = train_test_split(
            condition, floods, test_size=0.2, stratify=floods, random_state=42
        )
        clf = RandomForestClassifier(class_weight="balanced", random_state=42)
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        print(classification_report(y_test, preds))

        datas = weathers.order_by("-date")[:60]
        for data in datas:
            input = [[
                data.latitude, data.longitude, data.rain,
                data.temperature, data.humidity,
                data.elevation, data.pressure
            ]]
            flood = clf.predict(input)[0]
            risco = clf.predict_proba(input)
            print("Risco: ", risco)
            probability = risco[0][1] if risco.shape[1] > 1 else 0.0

            Forecast.objects.update_or_create(
                latitude = data.latitude,
                longitude = data.longitude,
                flood = flood,
                date = data.date,
                probability = probability
            )