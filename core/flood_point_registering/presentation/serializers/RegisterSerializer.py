from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from core.flood_point_registering.infra.models import Flood_Point_Register


class FloodPointRegisterSerializer(serializers.ModelSerializer):
    """Serializer for Flood Point Register.

    - Writeable fields: city (int), region (pk), neighborhood (pk), possibility (float), created_at, finished_at, props (JSON)
    - Read-only helpers: city_display, region_name, neighborhood_name
    - Validations: possibility 0..1, created_at <= finished_at
    """

    # Read-only helper fields for client convenience
    region_name = serializers.CharField(source="region.name", read_only=True)
    neighborhood_name = serializers.CharField(
        source="neighborhood.name", read_only=True
    )
    # Require props and validate as GeoJSON Feature
    props = serializers.JSONField()

    class Meta:
        model = Flood_Point_Register
        fields = [
            "id",
            "region",
            "region_name",
            "neighborhood",
            "neighborhood_name",
            "possibility",
            "created_at",
            "finished_at",
            "props",
        ]
        extra_kwargs = {
            "props": {"required": True},
            # allow API to omit timestamps; we'll default them
            "created_at": {"required": False},
            "finished_at": {"required": False},
        }

    def validate_possibility(self, value: float) -> float:
        # Accept probability in [0,1]. If 1<value<=100, interpret as percentage.
        v = float(value)
        if 0 <= v <= 1:
            return v
        if 1 < v <= 100:
            return round(v / 100.0, 6)
        raise serializers.ValidationError(
            "possibility deve estar no intervalo [0, 1] ou percentual até 100"
        )

    def validate(self, attrs):
        # GeoJSON minimal validation (Feature with geometry)
        props = attrs.get("props")
        if not isinstance(props, dict) or props.get("type") != "Feature":
            raise serializers.ValidationError(
                {"props": "props deve ser um GeoJSON Feature"}
            )
        geom = (props or {}).get("geometry")
        if not isinstance(geom, dict) or not geom.get("type"):
            raise serializers.ValidationError(
                {"props": "Feature.geometry é obrigatório"}
            )

        # Default created_at/finished_at when omitted
        created_at = attrs.get("created_at") or getattr(
            self.instance, "created_at", None
        )
        if created_at is None:
            created_at = timezone.now()
            attrs["created_at"] = created_at

        finished_at = attrs.get("finished_at") or getattr(
            self.instance, "finished_at", None
        )
        if finished_at is None and created_at is not None:
            finished_at = created_at + timedelta(hours=2)
            attrs["finished_at"] = finished_at
        if created_at and finished_at and created_at > finished_at:
            raise serializers.ValidationError(
                {"finished_at": "finished_at deve ser maior ou igual a created_at"}
            )
        # Cross-field validation: region/neighborhood consistency
        region = attrs.get("region") or getattr(self.instance, "region", None)
        neighborhood = attrs.get("neighborhood") or getattr(
            self.instance, "neighborhood", None
        )
        if region and neighborhood:
            # neighborhood must belong to region
            if getattr(neighborhood, "region_id", None) and getattr(region, "id", None):
                if neighborhood.region_id != region.id:
                    raise serializers.ValidationError(
                        {"neighborhood": "neighborhood não pertence à region informada"}
                    )
        return attrs
