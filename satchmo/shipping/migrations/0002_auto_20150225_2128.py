# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrier',
            name='postage_speed',
            field=models.PositiveIntegerField(default=2, verbose_name='Postage Speed'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='carrier',
            name='signed_for',
            field=models.BooleanField(default=False, verbose_name='Signed For'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='carrier',
            name='tracked',
            field=models.BooleanField(default=False, verbose_name='Tracked'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='carrier',
            name='active',
            field=models.BooleanField(default=False, verbose_name='Active'),
            preserve_default=True,
        ),
    ]
