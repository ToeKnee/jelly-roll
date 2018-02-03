# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0003_auto_20170206_2031'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='currency',
            options={'verbose_name': 'Currency', 'verbose_name_plural': 'Currencies'},
        ),
        migrations.AddField(
            model_name='currency',
            name='accepted',
            field=models.BooleanField(default=False, help_text='Accepted alternative currency for the shop', verbose_name='Accepted'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='currency',
            name='primary',
            field=models.BooleanField(default=False, help_text='Primary currency for the shop', verbose_name='Primary'),
            preserve_default=True,
        ),
    ]
