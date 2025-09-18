from django.db import migrations


ALIASES = {
    # old -> canonical
    "Centro: Avenida JK": "Avenida JK - Centro",
    "Centro: Praça da Bandeira": "Praça da Bandeira - Centro",
    "Centro: Terminal Central": "Terminal Central - Centro",
    "Rio Cachoeira: Terminal Norte": "Rio Cachoeira - Terminal Norte",
    "Águas Vermelhas: Rua Leopoldo Beninca": "Rua Leopoldo Beninca - Águas Vermelhas",
}


def forwards_func(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")

    for old_desc, canonical_desc in ALIASES.items():
        has_canonical = Camera.objects.filter(
            description=canonical_desc,
            latitude__isnull=False,
            longitude__isnull=False,
        ).exists()
        if not has_canonical:
            # Não há câmera canônica com coordenadas — não deletar nada por segurança
            continue

        # Apaga todas as câmeras com a descrição antiga sem coordenadas
        Camera.objects.filter(description=old_desc).filter(
            latitude__isnull=True
        ).delete()

        Camera.objects.filter(description=old_desc).filter(
            longitude__isnull=True
        ).delete()


def reverse_func(apps, schema_editor):
    # Operação destrutiva, sem reversão segura
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("flood_camera_monitoring", "0011_cleanup_duplicate_cameras"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_code=reverse_func)]
