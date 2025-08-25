import requests, time

def fillClimate(lat, lon, start, end, wait=60):
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ",".join([
            "precipitation_sum",
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "surface_pressure_mean"
        ]),
        "timezone": "America/Sao_Paulo"
    }

    while True:
        response = requests.get(url, params=params)
        data = response.json()

        if "daily" in data:
            return {
                "days": data["daily"]["time"],
                "rain": data["daily"]["precipitation_sum"],
                "temperature": data["daily"]["temperature_2m_mean"],
                "humidity": data["daily"]["relative_humidity_2m_mean"],
                "pressure": data["daily"]["surface_pressure_mean"]
            }
        
        elif data.get("error") and "request limit exceeded" in data.get("reason", "").lower():
            print(f"Limite de requisições atingido. Tentando novamente em {wait} segundos... ")
            print("outro erro: ", data)
            time.sleep(wait)
        else:
            print(f"Erro inesperado na API: {data}")
            time.sleep(wait)

    return {"days": [], "rain": [], "temperature": [], "humidity": [], "pressure": []}

def fillFutureClimate(lat, lon, start, end, retries=3, wait=60):
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "hourly": ",".join([
            "precipitation",
            "temperature_2m",
            "relative_humidity_2m",
        ])
    }

    for attempt in range(retries):
        response = requests.get(url, params=params)
        data = response.json()

        if "hourly" in data:
            return {
                "days": data["hourly"]["time"],
                "rain": data["hourly"]["precipitation"],
                "temperature": data["hourly"]["temperature_2m"],
                "humidity": data["hourly"]["relative_humidity_2m"]
            }
        
        elif data.get("error") and "request limit exceeded" in data.get("reason", "").lower():
                print(f"Limite de requisições atingido. Tentando novamente em {wait} segundos... ({attempt+1}/{retries})")
                time.sleep(wait)
        else:
            print(f"Erro inesperado na API: {data}")
            break

def fillFlood(lat: float, lon: float):
    url = f"https://flood-api.open-meteo.com/v1/flood"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "river_discharge"
        ])
    }
    response = requests.get(url, params=params)
    data = response.json()
    return {
        "river_discharge": data["daily"]["river_discharge"]
    }

def fillElevation(lat, lon):
    url = f'https://api.open-elevation.com/api/v1/lookup'
    params = {"locations": f'{lat}, {lon}'}
    response = requests.get(url, params=params)
    data = response.json()
    return {
        "elevation": data["results"][0]["elevation"]
    }