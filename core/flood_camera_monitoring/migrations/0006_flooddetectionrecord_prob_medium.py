# Generated manually: add prob_medium field to FloodDetectionRecord
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("flood_camera_monitoring", "0005_flooddetectionrecord_medium"),
    ]

    operations = [
        migrations.AddField(
            model_name="flooddetectionrecord",
            name="prob_medium",
            field=models.FloatField(default=0.0),
        ),
    ]
