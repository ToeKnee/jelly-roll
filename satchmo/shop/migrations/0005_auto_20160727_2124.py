# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import satchmo.payment.fields
import satchmo.shipping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_auto_20160725_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='estimated_delivery_expected_days',
            field=models.PositiveIntegerField(default=7, verbose_name='Usual number of days after shipping until delivery'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='estimated_delivery_max_days',
            field=models.PositiveIntegerField(default=25, verbose_name='Maximum number of days after shipping until delivery'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='estimated_delivery_min_days',
            field=models.PositiveIntegerField(default=1, verbose_name='Minimum number of days after shipping until delivery'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_model',
            field=satchmo.shipping.fields.ShippingChoiceCharField(max_length=30, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment',
            field=satchmo.payment.fields.PaymentChoiceCharField(max_length=25, blank=True),
            preserve_default=True,
        ),
    ]
