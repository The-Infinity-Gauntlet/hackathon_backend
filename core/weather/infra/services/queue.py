import os, geopandas as gpd
from decimal import getcontext, Decimal
from shapely.geometry import Point, Polygon, MultiPolygon
from core.weather.presentation.tasks.tasks import fillWeather

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
file = os.path.join(BASE_DIR, "fixtures", "neighborhoods.geojson")
neighborhoods = gpd.read_file(file)
print("Bairros: ", neighborhoods)
points = []
totalCoords = 2
getcontext().prec = 8

def enqueueFillClimates(start: str, end: str):
    total_tasks = 0
    coords = []
    step = Decimal("0.001")

    for idx, nb in neighborhoods.iterrows():
        if "bairro" in nb:
            neighborhood = nb["bairro"]
        elif "name" in nb:
            neighborhood = nb["name"]
        else:
            print(f'Bairro não encontrado em {idx}')
            continue
    
        geom_nb = nb["geometry"]

        if isinstance(geom_nb, Polygon):
            geoms_nb = [geom_nb]
        elif isinstance(geom_nb, MultiPolygon):
            geoms_nb = list(geom_nb.geoms)
        else:
            print(f'Geometria incorreta para {neighborhood}')

        for poligono in geoms_nb:
            if poligono is None: # Debug
                print(f"⚠️  Geometria inválida em {neighborhoods}")
                continue

            if not hasattr(poligono, "bounds"): # Debug
                    print(f"⚠️  Geometria sem bounds em {neighborhoods}: {type(poligono)}")
                    continue
            
            lon_min, lat_min, lon_max, lat_max = poligono.bounds
            lat = Decimal(str(lat_min))

            while lat <= Decimal(str(lat_max)): # Enquanto a latitude currente for menor que a máxima
                lon = Decimal(str(lon_min))
                while lon <= Decimal(str(lon_max)):
                    point = Point(float(lon), float(lat))
                    if poligono.contains(point):
                        #print("Polígono contém: ", point)
                        fin_lat = float(lat)
                        fin_lon = float(lon)
                        fillWeather.delay(fin_lat, fin_lon, neighborhood, start, end)
                        coords.append({"lat": fin_lat, "lon": fin_lon})
                        total_tasks += 1
                    lon += step
                lat += step

    return total_tasks, coords