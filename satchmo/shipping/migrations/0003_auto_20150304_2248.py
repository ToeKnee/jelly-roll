# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0002_auto_20150225_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carrier',
            name='postage_speed',
            field=models.PositiveIntegerField(default=2, verbose_name='Postage Speed', choices=[(0, 'Urgent'), (1, 'Priority'), (2, 'Standard'), (3, 'Economy')]),
            preserve_default=True,
        ),
    ]
