# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_postage_speed',
            field=models.PositiveIntegerField(default=2, verbose_name='Postage Speed', choices=[(0, 'Urgent'), (1, 'Priority'), (2, 'Standard'), (3, 'Economy')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_signed_for',
            field=models.BooleanField(default=False, verbose_name='Signed For'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_tracked',
            field=models.BooleanField(default=False, verbose_name='Tracked'),
            preserve_default=True,
        ),
    ]
