# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20170320_2124'),
    ]

    def set_primary_currency(apps, schema_editor):
        """ Set the primary currency on all existing orders
        """
        Currency = apps.get_model("currency", "Currency")
        Order = apps.get_model("shop", "Order")

        currency = Currency.objects.get(primary=True)
        Order.objects.all().update(currency=currency)

    operations = [
        migrations.RunPython(set_primary_currency),
    ]
