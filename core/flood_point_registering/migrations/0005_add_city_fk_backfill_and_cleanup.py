from django.db import migrations, models
import django.db.models.deletion


def backfill_city_from_neighborhood(apps, schema_editor):
    Register = apps.get_model("flood_point_registering", "Flood_Point_Register")
    Neighborhood = apps.get_model("addressing", "Neighborhood")
    City = apps.get_model("addressing", "City")

    # Build a map of City names to IDs for fallback
    city_name_to_id = dict(City.objects.values_list("name", "id"))

    # Iterate in chunks to avoid loading all rows in memory
    qs = Register.objects.all().only("id", "city_id", "neighborhood_id")
    batch = []
    BATCH_SIZE = 500

    def flush(batch_items):
        if not batch_items:
            return
        Register.objects.bulk_update(batch_items, ["city"])

    for reg in qs.iterator(chunk_size=BATCH_SIZE):
        if getattr(reg, "city_id", None):
            continue
        nb_id = getattr(reg, "neighborhood_id", None)
        city_id = None
        if nb_id:
            try:
                nb = Neighborhood.objects.only("city", "city_ref_id").get(id=nb_id)
                # Prefer linked City by FK when available
                if getattr(nb, "city_ref_id", None):
                    city_id = nb.city_ref_id
                else:
                    # Fallback: resolve by name
                    city_id = city_name_to_id.get(getattr(nb, "city", None))
            except Neighborhood.DoesNotExist:
                city_id = None
        if city_id:
            reg.city_id = city_id
            batch.append(reg)
            if len(batch) >= BATCH_SIZE:
                flush(batch)
                batch = []
    flush(batch)


class Migration(migrations.Migration):
    dependencies = [
        ("addressing", "0010_city_and_links"),
        (
            "flood_point_registering",
            "0004_alter_flood_point_register_created_at_and_more",
        ),
    ]

    operations = [
        # 1) Add new City FK as nullable to allow data backfill
        migrations.AddField(
            model_name="flood_point_register",
            name="city",
            field=models.ForeignKey(
                to="addressing.city",
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
            ),
        ),
        # 2) Drop legacy region field if it still exists in DB vs current model
        migrations.RemoveField(
            model_name="flood_point_register",
            name="region",
        ),
        # 3) Align created_at to auto_now_add (migration for model parity; DB default handled by Django)
        migrations.AlterField(
            model_name="flood_point_register",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="flood_point_register",
            name="finished_at",
            field=models.DateTimeField(db_index=True),
        ),
        # 4) Backfill city from neighborhood link
        migrations.RunPython(
            backfill_city_from_neighborhood, migrations.RunPython.noop
        ),
        # 5) Make City FK mandatory after backfill
        migrations.AlterField(
            model_name="flood_point_register",
            name="city",
            field=models.ForeignKey(
                to="addressing.city",
                on_delete=django.db.models.deletion.PROTECT,
                null=False,
            ),
        ),
    ]
