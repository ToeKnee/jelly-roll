# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20160727_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderstatus',
            name='time_stamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Timestamp', db_index=True),
            preserve_default=True,
        ),
    ]
