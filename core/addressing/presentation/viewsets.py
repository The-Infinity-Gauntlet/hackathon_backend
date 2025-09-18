from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from core.addressing.application.services import build_neighborhoods_feature_collection
from core.addressing.infra.repositories import DjangoNeighborhoodRepository
from core.addressing.infra.models import Region, Neighborhood


class AddressingViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="regions-neighborhoods")
    def regions_neighborhoods(self, request):
        """Return regions and their neighborhoods, optionally filtered by city.

        Query params:
        - city: case-insensitive string (optional). If provided, only regions/neighborhoods for that city are returned.

        Response shape:
        {
          "city": "Joinville" | null,
          "total_regions": int,
          "total_neighborhoods": int,
          "regions": [
            {"id": uuid, "name": str, "city": str, "neighborhood_count": int,
             "neighborhoods": [{"id": uuid, "name": str, "city": str}]}
          ]
        }
        """
        city = request.query_params.get("city")

        regions_qs = Region.objects.all()
        if city:
            regions_qs = regions_qs.filter(city__iexact=city)
        regions_qs = regions_qs.order_by("name").prefetch_related("neighborhoods")

        payload_regions = []
        total_nb = 0
        for reg in regions_qs:
            # Restrict neighborhoods to same city (defensive)
            nbs = [
                nb
                for nb in reg.neighborhoods.all()
                if not city or nb.city.lower() == reg.city.lower()
            ]
            nbs_sorted = sorted(nbs, key=lambda x: (x.name or ""))
            total_nb += len(nbs_sorted)
            payload_regions.append(
                {
                    "id": str(reg.id),
                    "name": reg.name,
                    "city": reg.city,
                    "neighborhood_count": len(nbs_sorted),
                    "neighborhoods": [
                        {"id": str(nb.id), "name": nb.name, "city": nb.city}
                        for nb in nbs_sorted
                    ],
                }
            )

        return Response(
            {
                "city": city or None,
                "total_regions": len(payload_regions),
                "total_neighborhoods": total_nb,
                "regions": payload_regions,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="dados_geograficos")
    def dados_geograficos(self, request):
        city = request.query_params.get("city")
        region = request.query_params.get("region")
        all_param = request.query_params.get("all")

        def _parse_bool(val):
            if val is None:
                return None
            v = str(val).strip().lower()
            if v == "true":
                return True
            if v == "false":
                return False
            return "invalid"

        all_flag = _parse_bool(all_param)
        if all_flag == "invalid":
            return Response(
                {
                    "error": "Invalid 'all' value",
                    "detail": "Use one of: true,false",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if all_flag is True and (city or region):
            return Response(
                {
                    "error": "Conflicting parameters",
                    "detail": "When 'all' is true, do not provide city or region filters.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        repo = DjangoNeighborhoodRepository()
        collection = build_neighborhoods_feature_collection(
            repo, all_flag=all_flag, city=city, region=region
        )
        return Response(collection, status=status.HTTP_200_OK)
