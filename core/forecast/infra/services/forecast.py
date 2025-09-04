from core.forecast.domain.repository import MachineLearningRepository
from core.forecast.infra.models import Forecast
from core.occurrences.infra.models import Occurrence
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from imblearn.over_sampling import SMOTE

import pandas as pd

def runForecast(repo: MachineLearningRepository): # Aqui é onde realmente acontece a previsão com IA
    # Treinamento
    occurrence_qs = Occurrence.objects.all().values("date", "neighborhood")
    occurrences = pd.DataFrame(list(occurrence_qs))
    conditions = []
    coords = repo.getCoords()
    print("Coords: ", coords)
    for coord in coords:
        weather = repo.getWeatherByCoord(coord["latitude"], coord["longitude"])
        for data in weather:
            if None not in (
                data.latitude, data.longitude, data.neighborhood, data.date, data.rain, data.temperature, data.humidity, data.elevation, data.pressure
            ):
                conditions.append([
                    data.latitude, 
                    data.longitude,
                    data.neighborhood, 
                    data.date,
                    data.rain, 
                    data.temperature, 
                    data.humidity, 
                    data.elevation, 
                    data.pressure
                ])

    print("Conditions: ", len(conditions))
    df_weather = pd.DataFrame(conditions, columns=["latitude", "longitude", "neighborhood", "date", "rain", "temperature", "humidity", "elevation", "pressure"])
    occurrences["date"] = pd.to_datetime(occurrences["date"]).dt.date
    df_weather["date"] = pd.to_datetime(df_weather["date"]).dt.date

    df = pd.merge(
        df_weather,
        occurrences,
        on=["neighborhood", "date"],
        how="left",
        suffixes=("", "_occurrence")
    )

    #occurrence_renamed = occurrences.rename(columns={"date": "date_flood"})
    df["flood"] = df.apply(
        lambda row: 1 if ((occurrences["neighborhood"] == row["neighborhood"]) & 
                          (occurrences["date"] == row["date"])).any() or 
                          (row.rain > 10 and row.humidity > 60 and row.elevation < 10)
                          else 0,
        axis=1
    )
    print(df["flood"])
    features = ["rain", "temperature", "humidity", "pressure", "elevation"]
    X = df[features].values
    Y = df["flood"].values # Aqui ele vai preencher os climas que estiverem sem registro de alagamento com NaN

    scaler = StandardScaler() # Padronizador
    X_scaled = scaler.fit_transform(X) # Treinar com base em X
    X_train, X_test, Y_train, Y_test = train_test_split(X_scaled, Y, test_size=0.25) # Devolve variáveis de teste e de treinamento da IA com base no X padrão

    rf = RandomForestClassifier(
        n_estimators=1000,
        max_depth=None,
        random_state=None,
        max_features="sqrt",
        class_weight="balanced"
    )
    clf = CalibratedClassifierCV(rf, cv=3, method="isotonic")
    smote = SMOTE()
    X_res, Y_res = smote.fit_resample(X_train, Y_train)
    clf.fit(X_res, Y_res)

    # Previsão
    df["date"] = pd.to_datetime(df["date"])
    today = pd.Timestamp.today().normalize()
    df_future = df[df["date"] >= today - pd.Timedelta(days=7)]

    X_future = df_future[features].values
    X_future_scaled = scaler.transform(X_future)

    Y_predict = clf.predict(X_future_scaled)
    Y_proba = clf.predict_proba(X_future_scaled)[:, 1]

    for i, row in enumerate(df_future.itertuples(index=False)):
        Forecast.objects.update_or_create(
            date = row.date,
            latitude = row.latitude,
            longitude = row.longitude,
            flood = int(Y_predict[i]),
            probability = float(Y_proba[i])
        )