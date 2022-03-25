from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pro", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="paypalnvp",
            name="ipaddress",
            field=models.GenericIPAddressField(null=True, blank=True),
        ),
    ]
