from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipn", "0002_paypalipn_mp_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paypalipn",
            name="ipaddress",
            field=models.GenericIPAddressField(null=True, blank=True),
        ),
    ]
