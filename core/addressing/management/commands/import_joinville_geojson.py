from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from django.core.management.base import BaseCommand, CommandError

from core.addressing.infra.models import Neighborhood, Region


# ---- Geometry helpers (module-level) ----
def geom_centroid(geom: Dict[str, Any] | None) -> Tuple[float, float] | None:
    if not geom:
        return None
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if not coords:
        return None

    def _centroid_polygon(poly: List[List[List[float]]]) -> Tuple[float, float]:
        ring = poly[0] if poly else []
        if not ring:
            return (0.0, 0.0)
        sx = sum(p[0] for p in ring)
        sy = sum(p[1] for p in ring)
        n = len(ring)
        return (sx / n, sy / n)

    if geom["type"] == "Polygon":
        return _centroid_polygon(coords)  # type: ignore[arg-type]
    if geom["type"] == "MultiPolygon":
        cents: List[Tuple[float, float]] = []
        for poly in coords:  # type: ignore[assignment]
            cents.append(_centroid_polygon(poly))
        if not cents:
            return None
        sx = sum(c[0] for c in cents)
        sy = sum(c[1] for c in cents)
        return (sx / len(cents), sy / len(cents))
    return None


def geom_bbox(geom: Dict[str, Any] | None) -> Tuple[float, float, float, float] | None:
    if not geom:
        return None
    gtype = geom.get("type")
    coords = geom.get("coordinates")
    if not coords:
        return None
    xs: List[float] = []
    ys: List[float] = []

    def add_ring(ring: List[List[float]]):
        for p in ring:
            xs.append(float(p[0]))
            ys.append(float(p[1]))

    if gtype == "Polygon":
        add_ring(coords[0])
    elif gtype == "MultiPolygon":
        for poly in coords:
            add_ring(poly[0])
    else:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def geom_area_km2(geom: Dict[str, Any] | None) -> float | None:
    # Rough area using planar shoelace on first ring, converted by latitude scale.
    if not geom or geom.get("type") not in ("Polygon", "MultiPolygon"):
        return None

    def polygon_area(ring: List[List[float]]) -> float:
        if len(ring) < 3:
            return 0.0
        s = 0.0
        for i in range(len(ring) - 1):
            x1, y1 = ring[i]
            x2, y2 = ring[i + 1]
            s += x1 * y2 - x2 * y1
        return abs(s) / 2.0

    if geom["type"] == "Polygon":
        a = polygon_area(geom["coordinates"][0])
    else:
        a = 0.0
        for poly in geom["coordinates"]:
            a += polygon_area(poly[0])
    c = geom_centroid(geom) or (0.0, 0.0)
    lat_scale = 111_000.0
    lon_scale = 111_000.0 * max(0.1, math.cos(math.radians(c[1])))
    return (a * lat_scale * lon_scale) / 1_000_000.0


class Command(BaseCommand):
    help = "Importa Regiões e Bairros de um GeoJSON (Joinville, Araquari, etc.). Pode inferir zonas quando faltarem."

    def add_arguments(self, parser):
        parser.add_argument("geojson_path", help="Caminho para o arquivo GeoJSON")
        parser.add_argument(
            "--city",
            default="Joinville",
            help="Nome da cidade a ser gravado nos registros (default: Joinville)",
        )
        parser.add_argument(
            "--city-prop",
            default="cidade",
            help="Nome da propriedade que contém o nome da cidade no GeoJSON (default: cidade)",
        )
        parser.add_argument(
            "--region-prop",
            default="zona",
            help="Nome da propriedade que contém o nome da região (ex.: zona). Se ausente, pode ser inferida",
        )
        parser.add_argument(
            "--neighborhood-prop",
            default="bairro",
            help="Nome da propriedade que contém o nome do bairro (ex.: bairro)",
        )
        parser.add_argument(
            "--geometry",
            action="store_true",
            help="Se presente, salva GeoJSON de região em Region.geometry (se disponível)",
        )
        parser.add_argument(
            "--infer-zones-if-missing",
            action="store_true",
            help="Se a propriedade de região/zona estiver vazia, infere automaticamente com base no centróide",
        )
        parser.add_argument(
            "--center-lat",
            type=float,
            default=None,
            help="Latitude do centro da cidade (opcional). Se omitido, será inferido pela média dos centróides",
        )
        parser.add_argument(
            "--center-lon",
            type=float,
            default=None,
            help="Longitude do centro da cidade (opcional). Se omitido, será inferido pela média dos centróides",
        )

    def handle(self, *args, **opts):
        path = Path(opts["geojson_path"]).expanduser()
        if not path.exists():
            raise CommandError(f"Arquivo não encontrado: {path}")

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        city = opts["city"]
        prop_city = opts["city_prop"]
        prop_region = opts["region_prop"]
        prop_neigh = opts["neighborhood_prop"]
        keep_geometry = bool(opts.get("geometry"))
        infer_zones = bool(opts.get("infer_zones_if_missing"))
        center_lat = opts.get("center_lat")
        center_lon = opts.get("center_lon")

        if data.get("type") != "FeatureCollection":
            raise CommandError("GeoJSON inválido: esperado FeatureCollection")

        # Filtra features pela cidade desejada
        features: List[Dict[str, Any]] = []
        for feat in data.get("features", []):
            props: Dict[str, Any] = feat.get("properties") or {}
            feat_city = (props.get(prop_city) or "").strip()
            if not feat_city or feat_city.lower() == city.lower():
                features.append(feat)

        if not features:
            raise CommandError(
                f"Nenhuma feature encontrada para a cidade '{city}' usando a propriedade '{prop_city}'."
            )

        created_regions = 0
        created_neighs = 0

        # Pré-calcula centróides para a cidade e infere centro se necessário
        centroids: List[Tuple[float, float]] = []
        if infer_zones and (center_lat is None or center_lon is None):
            for feat in features:
                g = feat.get("geometry") if feat.get("geometry") else None
                c = geom_centroid(g)
                if c:
                    centroids.append((c[1], c[0]))  # (lat, lon)
            if centroids:
                center_lat = sum(lat for lat, _ in centroids) / len(centroids)
                center_lon = sum(lon for _, lon in centroids) / len(centroids)

        def infer_zone_name(centroid: Tuple[float, float]) -> str:
            assert center_lat is not None and center_lon is not None
            lat, lon = centroid
            dy = lat - center_lat
            dx = lon - center_lon
            ang = math.atan2(dy, dx)
            deg = (math.degrees(ang) + 360) % 360
            bins = [
                (22.5, "Leste"),
                (67.5, "Nordeste"),
                (112.5, "Norte"),
                (157.5, "Noroeste"),
                (202.5, "Oeste"),
                (247.5, "Sudoeste"),
                (292.5, "Sul"),
                (337.5, "Sudeste"),
                (360.0, "Leste"),
            ]
            for limit, name in bins:
                if deg <= limit:
                    return name
            return "Leste"

        # index regions by (city, name)
        def get_or_create_region(
            name: str, geometry: Dict[str, Any] | None, inferred: bool = False
        ) -> Region:
            nonlocal created_regions
            r, created = Region.objects.get_or_create(
                name=name.strip(),
                city=city,
                defaults={
                    "props": (
                        {
                            "inferred": inferred,
                            **(
                                {"geometry": geometry}
                                if (keep_geometry and geometry and not inferred)
                                else {}
                            ),
                        }
                    ),
                },
            )
            if created:
                created_regions += 1
            else:
                if not inferred and keep_geometry and geometry:
                    props = dict(r.props or {})
                    if props.get("geometry") != geometry:
                        props["geometry"] = geometry
                        r.props = props
                        r.save(update_fields=["props"])
            return r

        # Se vamos inferir zonas quando faltarem, precisamos talvez das coords dos bairros
        for feat in features:
            props: Dict[str, Any] = feat.get("properties") or {}
            g = feat.get("geometry") if keep_geometry else None

            region_name = (props.get(prop_region) or "").strip()
            neigh_name = (props.get(prop_neigh) or "").strip()

            if not region_name and not neigh_name:
                continue

            region: Region | None = None
            if region_name:
                region = get_or_create_region(region_name, g)
            elif infer_zones and neigh_name:
                c = geom_centroid(
                    feat.get("geometry") if feat.get("geometry") else None
                )
                if c is not None and center_lat is not None and center_lon is not None:
                    zone = infer_zone_name((c[1], c[0]))  # (lat, lon)
                else:
                    zone = "Centro"
                region = get_or_create_region(zone, None, inferred=True)

            if neigh_name:
                # Build props containing geometry and metrics only inside JSON
                n_props = {"source_props": props}
                area_val = None
                if keep_geometry and g:
                    n_props["geometry"] = g
                    c = geom_centroid(g)
                    if c:
                        n_props["centroid"] = [c[0], c[1]]  # [lon, lat]
                    area_val = geom_area_km2(g)
                    if area_val is not None:
                        n_props["area_km2"] = area_val

                n, created = Neighborhood.objects.get_or_create(
                    name=neigh_name,
                    city=city,
                    defaults={"region": region, "props": n_props, "area_km2": area_val},
                )

                updates = {}
                if region and n.region_id != getattr(region, "id", None):
                    n.region = region
                    updates["region"] = region

                # Merge props on update
                merged = dict(n.props or {})
                for k, v in n_props.items():
                    merged[k] = v
                if merged != (n.props or {}):
                    n.props = merged
                    updates["props"] = merged

                # Update area_km2 if computed
                if area_val is not None and n.area_km2 != area_val:
                    n.area_km2 = area_val
                    updates["area_km2"] = area_val

                if updates and not created:
                    n.save(update_fields=list(updates.keys()))
                if created:
                    created_neighs += 1
