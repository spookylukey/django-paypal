# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pdt', '0003_auto_20141117_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paypalpdt',
            name='address_country_code',
            field=models.CharField(help_text='ISO 3166', blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='auction_closing_date',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='business',
            field=models.CharField(help_text='Email where the money was sent.', blank=True, max_length=127),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='case_creation_date',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='currency_code',
            field=models.CharField(default='USD', blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='mc_currency',
            field=models.CharField(default='USD', blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='next_payment_date',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='parent_txn_id',
            field=models.CharField(blank=True, verbose_name='Parent Transaction ID', max_length=19),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='payment_date',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='retry_at',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='subscr_date',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='subscr_effective',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='time_created',
            field=models.DateTimeField(help_text='HH:MM:SS DD Mmm YY, YYYY PST', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='txn_id',
            field=models.CharField(help_text='PayPal transaction ID.', db_index=True, verbose_name='Transaction ID', blank=True, max_length=19),
        ),
        migrations.AlterField(
            model_name='paypalpdt',
            name='txn_type',
            field=models.CharField(help_text='PayPal transaction type.', blank=True, verbose_name='Transaction Type', max_length=128),
        ),
    ]
