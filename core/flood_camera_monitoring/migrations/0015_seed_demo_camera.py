from django.db import migrations


DEMO_DESCRIPTION = "Camera Demo Alagamento (Loop)"
# Use local demo MP4s in MEDIA_ROOT via the custom 'loop:' scheme understood by OpenCV adapter
DEMO_VIDEO_HLS = "loop:media:0001.mp4,media:0002.mp4"


def create_demo_camera(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")

    qs = Camera.objects.filter(description=DEMO_DESCRIPTION)
    obj = None
    if qs.exists():
        # If duplicates exist, keep the first and remove the rest
        obj = qs.first()
        extra_ids = list(qs.values_list("pk", flat=True))[1:]
        if extra_ids:
            Camera.objects.filter(pk__in=extra_ids).delete()
    else:
        obj = Camera.objects.create(
            description=DEMO_DESCRIPTION,
            status=1,  # CameraStatus.ACTIVE
            video_hls=DEMO_VIDEO_HLS,
        )

    updated = False
    if getattr(obj, "video_hls", None) != DEMO_VIDEO_HLS:
        obj.video_hls = DEMO_VIDEO_HLS
        updated = True
    if getattr(obj, "status", None) != 1:
        obj.status = 1
        updated = True
    if updated:
        obj.save(update_fields=["video_hls", "status"])  # type: ignore[arg-type]


def remove_demo_camera(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")
    Camera.objects.filter(description=DEMO_DESCRIPTION).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("flood_camera_monitoring", "0014_seed_camera_metadata"),
    ]

    operations = [
        migrations.RunPython(create_demo_camera, remove_demo_camera),
    ]
