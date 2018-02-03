# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    def primary_currency(apps, schema_editor):
        """ Move the Currency setting in to the currency app

        """
        Currency = apps.get_model("currency", "Currency")
        Setting = apps.get_model("configuration", "Setting")
        try:
            currency_setting = Setting.objects.get(
                key='CURRENCY',
                group='CURRENCY',
            )
        except Setting.DoesNotExist:
            currency_setting = None

        if currency_setting:
            try:
                currency = Currency.objects.get(symbol=currency_setting.value)
            except Currency.DoesNotExist:
                currency = Currency.objects.first()
        else:
            currency = Currency.objects.first()

        currency.primary = True
        currency.accepted = True
        currency.save()

    dependencies = [
        ('currency', '0004_auto_20170206_2106'),
    ]

    operations = [
        migrations.RunPython(primary_currency),
    ]
