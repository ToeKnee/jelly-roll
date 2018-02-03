# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    def copy_currency(apps, schema_editor):
        """If there is already a currency set, migrate it to the new
        setting.

        """
        Setting = apps.get_model("configuration", "Setting")
        try:
            currency_setting = Setting.objects.get(
                key='CURRENCY',
                group='SHOP',
            )
        except Setting.DoesNotExist:
            pass
        else:
            currency_setting.group = 'CURRENCY'
            currency_setting.save()

    dependencies = [
        ('configuration', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_currency),
    ]
