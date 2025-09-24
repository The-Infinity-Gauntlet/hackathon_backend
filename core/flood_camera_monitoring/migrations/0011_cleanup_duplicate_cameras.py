from django.db import migrations


def forwards_func(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")
    from django.db.models import Count, Q

    # Para cada descrição com duplicatas, se existir pelo menos uma com lat/long,
    # remover as entradas que não têm alguma das coordenadas.
    duplicates = (
        Camera.objects.values("description").annotate(c=Count("id")).filter(c__gt=1)
    )
    for row in duplicates:
        desc = row["description"]
        qs = Camera.objects.filter(description=desc)
        has_coords = qs.filter(latitude__isnull=False, longitude__isnull=False).exists()
        if not has_coords:
            # Nenhuma tem coordenadas — não deletar nada para evitar perda de dados.
            continue
        qs.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True)).delete()


def reverse_func(apps, schema_editor):
    # Operação destrutiva; sem reversão segura.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("flood_camera_monitoring", "0010_seed_camera_coordinates"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_code=reverse_func)]
