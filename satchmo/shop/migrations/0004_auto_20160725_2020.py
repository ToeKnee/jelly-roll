# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_auto_20150302_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='time_stamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time stamp'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='downloadlink',
            name='time_stamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time stamp'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='time_stamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='timestamp'),
            preserve_default=True,
        ),
    ]
