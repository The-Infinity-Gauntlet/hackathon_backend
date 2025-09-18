from django.db import migrations


DEMO_DESCRIPTIONS = [
    "Camera Demo Alagamento (Loop)",
]


def forwards_func(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")
    Camera.objects.filter(description__in=DEMO_DESCRIPTIONS).delete()


def reverse_func(apps, schema_editor):
    # Destrutivo; não recria a câmera demo
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("flood_camera_monitoring", "0012_cleanup_alias_duplicate_cameras"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_code=reverse_func)]
