from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pdt", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paypalpdt",
            name="mp_id",
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
    ]
