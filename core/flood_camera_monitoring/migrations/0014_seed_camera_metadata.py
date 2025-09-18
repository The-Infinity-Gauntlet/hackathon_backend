from django.db import migrations


# Map alias descriptions to the canonical ones used in coordinates seeding
ALIASES = {
    "Centro: Avenida JK": "Avenida JK - Centro",
    "Centro: Praça da Bandeira": "Praça da Bandeira - Centro",
    "Centro: Terminal Central": "Terminal Central - Centro",
    "Rio Cachoeira: Terminal Norte": "Rio Cachoeira - Terminal Norte",
    "Águas Vermelhas: Rua Leopoldo Beninca": "Rua Leopoldo Beninca - Águas Vermelhas",
}


# Data provided to register cameras and their metadata
CAMERAS = [
    {
        "description": "Águas Vermelhas: Rua Leopoldo Beninca",
        "status": "OFFLINE",
        "video_hls": "https://connect-524.servicestream.io:8050/9980ca324f48.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/7d2551870cb4ca9f5a27b84391243775eaedad995dfd7e181d5430a000f0833961ba58cfcd5dbb88c9dd431cfc74",
        "neighborhood_id": "f089f425-4993-4f89-bd72-2b95afb6d044",
    },
    {
        "description": "Centro: Avenida JK",
        "status": "ACTIVE",
        "video_hls": "https://connect-92.servicestream.io:8050/bcc84c859ab7.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/83e3785a96f4e4a6f4b92b74ecf6a398e54ef285998f4d130aefa755f4155d66896770236366590e3975f90e4a00",
        "neighborhood_id": "3bafdd71-f122-4099-bd51-3e4f851c099a",
    },
    {
        "description": "Centro: Praça da Bandeira",
        "status": "ACTIVE",
        "video_hls": "https://connect-120.servicestream.io:8050/e7f57bcc97a2.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/8ee5d57ad06e2061f0f6903a7654f8922b2c26b9098bbe535182d9085e110faf78eb8772f018b50a712e92bd95e6",
        "neighborhood_id": "3bafdd71-f122-4099-bd51-3e4f851c099a",
    },
    {
        "description": "Centro: Terminal Central",
        "status": "ACTIVE",
        "video_hls": "https://connect-92.servicestream.io:8050/bcc84c859ab7.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/83e3785a96f4e4a6fhttps4b92b74ecf6a398e54ef285998f4d130aefa755f4155d66896770236366590e3975f90e4a00",
        "neighborhood_id": "3bafdd71-f122-4099-bd51-3e4f851c099a",
    },
    {
        "description": "Paranaguamirim: Rua 6 de Janeiro",
        "status": "ACTIVE",
        "video_hls": "https://connect-451.servicestream.io:8050/6272496274c1.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/984be5c620e7d2cc5571aa84f560b11558c4c2fd5ebf6ee547a55f579a5ebbeb05898dc008437e2124498ed96e8b",
        "neighborhood_id": "e013c475-ab65-4e87-b8b4-3b15f66066b3",
    },
    {
        "description": "Rio Águas Vermelhas: Rua Minas Gerais",
        "status": "OFFLINE",
        "video_hls": "https://connect-524.servicestream.io:8050/84b8b97bcdde.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/39858ef78be1f3117cd2dbd2f343bd3eabd9137fe6365ee64a99f7e316d07f4a08c50b51833b52e28c12288efde6",
        "neighborhood_id": "040873a8-33f8-4918-baf9-6063433342d3",
    },
    {
        "description": "Rio Cachoeira: Prefeitura",
        "status": "ACTIVE",
        "video_hls": "https://connect-272.servicestream.io:8050/919bd92b8436.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/e4fc2988b4bd8f292163de0ac6e46d6074bc223d3b9d096f645050e97eed3161c94abc6827cebb53bc924e4ed1b8",
        "neighborhood_id": "a3e04bc3-7b8e-4ecc-907b-eb1f641a8349",
    },
    {
        "description": "Rio Cachoeira: Terminal Norte",
        "status": "ACTIVE",
        "video_hls": "https://connect-92.servicestream.io:8050/85148626746f.m3u8",
        "video_embed": "https://www.khronosaavivo2.com.br/#/cembed/31237a32ad9912f2e817708c1875a9058fece000d303b4943f356db1a958ec17b39ada66462fdb3fcb917fd6486a",
        "neighborhood_id": "0c714a63-d6d2-49e2-84a5-024e08123cf2",
    },
    {
        "description": "Rio Cubatão: Canal",
        "status": "INACTIVE",
        "video_hls": "https://connect-92.servicestream.io:8050/3ab8e7fd6566.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/2e10c3f047ee6c80ae1ab16007263263006deedc08b2cf0fd401f43ee84bd4f9bea27d13f154969fea863650e16f",
        "neighborhood_id": "040873a8-33f8-4918-baf9-6063433342d3",
    },
    {
        "description": "Rio Cubatão: Ponte Quiriri",
        "status": "OFFLINE",
        "video_hls": "https://connect-524.servicestream.io:8050/d350ed83141b.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/7d2551870cb4ca9f5a27b84391243775eaedad995dfd7e181d5430a000f0833961ba58cfcd5dbb88c9dd431cfc74",
        "neighborhood_id": "040873a8-33f8-4918-baf9-6063433342d3",
    },
    {
        "description": "Rio do Braço: Jardim Sofia",
        "status": "OFFLINE",
        "video_hls": "https://connect-524.servicestream.io:8050/9980ca324f48.m3u8",
        "video_embed": "https://www.khronosaovivo2.com.br/#/cembed/7d2551870cb4ca9f5a27b84391243775eaedad995dfd7e181d5430a000f0833961ba58cfcd5dbb88c9dd431cfc74",
        "neighborhood_id": "6d45a8eb-75b7-42a2-8112-cb0f59bf9570",
    },
]


STATUS_MAP = {"ACTIVE": 1, "INACTIVE": 2, "OFFLINE": 3}


def forwards_func(apps, schema_editor):
    Camera = apps.get_model("flood_camera_monitoring", "Camera")

    for item in CAMERAS:
        desc = item["description"]
        canonical = ALIASES.get(desc, desc)

        qs = Camera.objects.filter(description=canonical)
        if not qs.exists():
            # Não cria novas câmeras; segue a política de update-only
            continue

        status_val = STATUS_MAP.get(item.get("status", "OFFLINE"), 3)
        updates = {
            "status": status_val,
            "video_hls": item.get("video_hls"),
            "video_embed": item.get("video_embed"),
        }

        nb_id = item.get("neighborhood_id")
        if nb_id:
            updates["neighborhood_id"] = nb_id

        qs.update(**updates)


def reverse_func(apps, schema_editor):
    # Não desfaz atualizações de metadados para evitar perda de dados.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("flood_camera_monitoring", "0013_remove_demo_camera"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_code=reverse_func)]
