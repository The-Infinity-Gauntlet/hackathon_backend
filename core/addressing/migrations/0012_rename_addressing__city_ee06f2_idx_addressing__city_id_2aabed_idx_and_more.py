from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("addressing", "0011_city_addressing__name_92704e_idx"),
    ]

    # No-op: keep Address/Neighborhood/Region.city as CharField
    # We rely on city_ref FKs introduced in 0010 for linking to City.
    operations = []
