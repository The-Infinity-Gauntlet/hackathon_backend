from django.db import migrations


def seed_and_backfill(apps, schema_editor):
    City = apps.get_model("addressing", "City")
    Neighborhood = apps.get_model("addressing", "Neighborhood")
    Region = apps.get_model("addressing", "Region")

    # Ensure cities exist
    jv, _ = City.objects.get_or_create(name="Joinville")
    ar, _ = City.objects.get_or_create(name="Araquari")

    name_to_id = {"joinville": jv.id, "araquari": ar.id}

    # Backfill Region.city_ref
    for reg in Region.objects.all().only("id", "city", "city_ref_id"):
        if getattr(reg, "city_ref_id", None):
            continue
        key = (reg.city or "").strip().lower()
        cid = name_to_id.get(key)
        if cid:
            reg.city_ref_id = cid
            reg.save(update_fields=["city_ref"])

    # Backfill Neighborhood.city_ref
    for nb in Neighborhood.objects.all().only("id", "city", "city_ref_id"):
        if getattr(nb, "city_ref_id", None):
            continue
        key = (nb.city or "").strip().lower()
        cid = name_to_id.get(key)
        if cid:
            nb.city_ref_id = cid
            nb.save(update_fields=["city_ref"])


class Migration(migrations.Migration):
    dependencies = [
        (
            "addressing",
            "0012_rename_addressing__city_ee06f2_idx_addressing__city_id_2aabed_idx_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(seed_and_backfill, migrations.RunPython.noop),
    ]
