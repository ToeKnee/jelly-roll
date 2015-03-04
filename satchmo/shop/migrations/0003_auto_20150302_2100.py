# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import satchmo.payment.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20150225_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fulfilled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(max_length=64, null=True, verbose_name='Tracking Number', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_url',
            field=models.URLField(null=True, verbose_name='Tracking URL', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment',
            field=satchmo.payment.fields.PaymentChoiceCharField(max_length=25, blank=True),
            preserve_default=True,
        ),
    ]
