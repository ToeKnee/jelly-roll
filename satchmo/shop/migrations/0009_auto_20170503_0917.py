# -*- coding: utf-8 -*-


from django.db import models, migrations
import satchmo.payment.fields
import satchmo.shipping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0007_auto_20170214_0926'),
        ('shop', '0008_auto_20170320_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='currency',
            field=models.ForeignKey(related_name='carts', blank=True, editable=False, to='currency.Currency', null=True, verbose_name='Currency'),
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
