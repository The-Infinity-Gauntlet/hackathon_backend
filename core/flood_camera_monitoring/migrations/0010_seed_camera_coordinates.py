from django.db import migrations


CAMERA_COORDS = [
    {
        "name": "Avenida JK - Centro",
        "lng": -48.84799478818965,
        "lat": -26.301488088946193,
    },
    {
        "name": "Praça da Bandeira - Centro",
        "lng": -48.843745058066915,
        "lat": -26.301637239913898,
    },
    {
        "name": "Terminal Central - Centro",
        "lng": -48.844827710812304,
        "lat": -26.301645718372086,
    },
    {
        "name": "Rio Cachoeira - Terminal Norte",
        "lng": -48.84981079761562,
        "lat": -26.272573511196754,
    },
    {
        "name": "Rua Leopoldo Beninca - Águas Vermelhas",
        "lng": -48.89619558776599,
        "lat": -26.292079675592188,
    },
    {
        "name": "Paranaguamirim: Rua 6 de Janeiro",
        "lng": -48.79105942168681,
        "lat": -26.346719706566272,
    },
    {
        "name": "Rio Águas Vermelhas: Rua Minas Gerais",
        "lng": -48.889186970324765,
        "lat": -26.337840010970712,
    },
    {
        "name": "Rio do Braço: Jardim Sofia",
        "lng": -48.834506504574115,
        "lat": -26.240114194675723,
    },
    {
        "name": "Rio Cubatão: Ponte Quiriri",
        "lng": -49.01251736504492,
        "lat": -26.147494911589785,
    },
    {
        "name": "Rio Cubatão: Canal",
        "lng": -48.90778497207297,
        "lat": -26.19535630390123,
    },
    {
        "name": "Rio Cachoeira: Prefeitura",
        "lng": -48.84109469618179,
        "lat": -26.30181422755672,
    },
]


def forwards_func(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")
    for item in CAMERA_COORDS:
        # Usa "description" como o campo de nome amigável
        Camera.objects.update_or_create(
            description=item["name"],
            defaults={
                "latitude": item["lat"],
                "longitude": item["lng"],
            },
        )


def reverse_func(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")
    names = [c["name"] for c in CAMERA_COORDS]
    Camera.objects.filter(description__in=names).update(latitude=None, longitude=None)


class Migration(migrations.Migration):

    dependencies = [
        (
            "flood_camera_monitoring",
            "0009_remove_camera_address_camera_latitude_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_code=reverse_func),
    ]
