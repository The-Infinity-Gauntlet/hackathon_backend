from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.addressing.application.services import build_neighborhoods_feature_collection
from core.addressing.infra.repositories import DjangoNeighborhoodRepository


class NeighborhoodGeoJSONView(APIView):
    def get(self, request):
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

        # Build response through application service + repository (Clean Architecture)
        repo = DjangoNeighborhoodRepository()
        collection = build_neighborhoods_feature_collection(
            repo, all_flag=all_flag, city=city, region=region
        )
        return Response(collection, status=status.HTTP_200_OK)
