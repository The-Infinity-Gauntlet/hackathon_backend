from core.forecast.domain.repository import MachineLearningRepository
from core.forecast.infra.models import Forecast
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd

def runForecast(repo: MachineLearningRepository): # Aqui é onde realmente acontece a previsão com IA
    coords = repo.getCoords()
    for coord in coords:
        weather = repo.getWeatherByCoord(repo["latitude"], repo["longitude"])
        condition = []
        for data in weather:
            if None not in (
                data.latitude, data.longitude, data.rain, data.temperature, data.humidity, data.elevation, data.pressure
            ):
                condition.append([
                    data.latitude, 
                    data.longitude, 
                    data.rain, 
                    data.temperature, 
                    data.humidity, 
                    data.elevation, 
                    data.pressure
                ])

        occurrences = pd.read_csv("") # arquivo de ocorrências

    df_weather = pd.DataFrame(condition)
    df = pd.merge(
        df_weather,
        occurrences,
        on=["latitude", "longitude", "date"],
        how="left"
    )
    #df_flood = df[df["flood"].notna()]

    features = ["rain", "temperature", "humidity", "pressure", "elevation"]
    X = df[features].values
    Y = df[df["flood"].notna()].values # Aqui ele vai preencher os climas que estiverem sem registro de alagamento com NaN

    scaler = StandardScaler() # Padronizador
    X_scaled = scaler.fit_transform(X) # Treinar com base em X
    X_test, X_train, Y_test, Y_train = train_test_split(X_scaled, test_size=0.2, random_state=42) # Devolve variáveis de teste e de treinamento da IA com base no X padrão
    
    clf = RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        random_state=42,
        class_weight="balanced"
    )
    clf.fit(X_train, Y_train)
    Y_predict = clf.predict(X_test)
    Y_proba = clf.predict_proba(X_test)[:, 1]

    Forecast.objects.update_or_create(
        latitude = data.latitude,
        longitude = data.longitude,
        flood = data.flood,
        probability = data.probability
    )