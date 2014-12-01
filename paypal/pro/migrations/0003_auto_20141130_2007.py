# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0002_auto_20141117_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalnvp',
            name='city',
            field=models.CharField(blank=True, verbose_name='City', max_length=255),
        ),
        migrations.AlterField(
            model_name='paypalnvp',
            name='countrycode',
            field=models.CharField(blank=True, verbose_name='Country', max_length=2),
        ),
        migrations.AlterField(
            model_name='paypalnvp',
            name='firstname',
            field=models.CharField(blank=True, verbose_name='First Name', max_length=255),
        ),
        migrations.AlterField(
            model_name='paypalnvp',
            name='lastname',
            field=models.CharField(blank=True, verbose_name='Last Name', max_length=255),
        ),
        migrations.AlterField(
            model_name='paypalnvp',
            name='state',
            field=models.CharField(blank=True, verbose_name='State', max_length=255),
        ),
        migrations.AlterField(
            model_name='paypalnvp',
            name='street',
            field=models.CharField(blank=True, verbose_name='Street Address', max_length=255),
        ),
        migrations.AlterField(
            model_name='paypalnvp',
            name='zip',
            field=models.CharField(blank=True, verbose_name='Postal / Zip Code', max_length=32),
        ),
    ]
