from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pdt", "0002_paypalpdt_mp_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paypalpdt",
            name="ipaddress",
            field=models.GenericIPAddressField(null=True, blank=True),
        ),
    ]
