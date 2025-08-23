from core.forecast.domain.repository import MachineLearningRepository
from core.forecast.infra.models import Forecast
from core.occurrences.infra.models import Occurrence
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd

def runForecast(repo: MachineLearningRepository): # Aqui é onde realmente acontece a previsão com IA
    occurrence_qs = Occurrence.objects.all().values("datetime", "neighborhood")
    occurrences = pd.DataFrame(list(occurrence_qs))
    conditions = []
    coords = repo.getCoords()
    for coord in coords:
        weather = repo.getWeatherByCoord(coord["latitude"], coord["longitude"])
        for data in weather:
            if None not in (
                data.latitude, data.longitude, data.rain, data.temperature, data.humidity, data.elevation, data.pressure
            ):
                conditions.append([
                    data.latitude, 
                    data.longitude, 
                    data.rain, 
                    data.temperature, 
                    data.humidity, 
                    data.elevation, 
                    data.pressure
                ])

    df_weather = pd.DataFrame(conditions, columns=["latitude", "longitude", "rain", "temperature", "humidity", "elevation", "pressure", "datetime"])
    df = pd.merge(
        df_weather,
        occurrences,
        on=["latitude", "longitude", "date"],
        how="left"
    )
    df["flood"] = df["neighborhoods"].notna().astype(int)

    features = ["rain", "temperature", "humidity", "pressure", "elevation"]
    X = df[features].values
    Y = df["flood"].values # Aqui ele vai preencher os climas que estiverem sem registro de alagamento com NaN

    scaler = StandardScaler() # Padronizador
    X_scaled = scaler.fit_transform(X) # Treinar com base em X
    X_train, X_test, Y_train, Y_test = train_test_split(X_scaled, test_size=0.2, random_state=42) # Devolve variáveis de teste e de treinamento da IA com base no X padrão
        
    clf = RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        random_state=42,
        class_weight="balanced"
    )
    clf.fit(X_train, Y_train)
    Y_predict = clf.predict(X_test)
    Y_proba = clf.predict_proba(X_test)[:, 1]

    for i, row in df.itterrows():
        Forecast.objects.update_or_create(
            latitude = row.latitude,
            longitude = row.longitude,
            flood = row.get("flood", 0),
            probability = Y_proba[i]
        )