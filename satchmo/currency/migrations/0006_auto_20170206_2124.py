# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0005_auto_20170206_2107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='iso_4217_code',
            field=models.CharField(unique=True, max_length=3, verbose_name='ISO 4217 code'),
            preserve_default=True,
        ),
    ]
