import os, geopandas as gpd
from decimal import getcontext, Decimal
from shapely.geometry import Point, Polygon, MultiPolygon
from core.weather.presentation.tasks.fillWeatherTask import fillWeather

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
file = os.path.join(BASE_DIR, "fixtures", "neighborhoods.geojson")
neighborhoods = gpd.read_file(file)
totalCoords = 2
getcontext().prec = 8

def enqueueFillClimates(start: str, end: str):
    total_tasks = 0
    coords = []
    step = Decimal("0.01")

    max_points = 10000

    for idx, nb in neighborhoods.iterrows():
        if "bairro" in nb:
            neighborhood = nb["bairro"]
        elif "name" in nb:
            neighborhood = nb["name"]
        else:
            print(f'Bairro não encontrado em {idx}')
            continue

        if not neighborhood:
            print("Bairro completo: ", neighborhood)
            continue
    
        geom_nb = nb["geometry"]

        if isinstance(geom_nb, Polygon):
            geoms_nb = [geom_nb]
        elif isinstance(geom_nb, MultiPolygon):
            geoms_nb = list(geom_nb.geoms)
        else:
            print(f'Geometria incorreta para {neighborhood}')

        points = 0

        for poligono in geoms_nb:
            lon_min, lat_min, lon_max, lat_max = poligono.bounds
            lat = Decimal(str(lat_min))

            while lat <= Decimal(str(lat_max)): # Enquanto a latitude currente for menor que a máxima
                lon = Decimal(str(lon_min)) # Esta é a longitude
                while lon <= Decimal(str(lon_max)): # Enquanto a longitude currente for menor que a máxima
                    point = Point(float(lon), float(lat)) # Esta é a coordenada
                    if poligono.contains(point): # Se o bairro contiver este ponto
                        #print("Polígono contém: ", point)
                        fin_lat = Decimal(lat)
                        fin_lon = Decimal(lon)
                        #print("Lat: ", fin_lat)
                        #print("Lon: ", fin_lon)
                        fillWeather.delay(fin_lat, fin_lon, neighborhood, start, end) # Aplique a função
                        coords.append({"lat": fin_lat, "lon": fin_lon})
                        total_tasks += 1
                        points += 1
                        if points > max_points:
                            break
                    lon += step
                    if points > max_points:
                        break
                lat += step
                if points > max_points:
                    break
            if points > max_points:
                break
        if points > max_points:
                break

    return total_tasks, coords