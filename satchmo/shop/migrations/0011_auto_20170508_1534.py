# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import django.utils.timezone
import satchmo.payment.fields
import satchmo.shipping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_auto_20170505_0922'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRefund',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment', satchmo.payment.fields.PaymentChoiceCharField(blank=True, max_length=25, choices=[(b'PAYMENT_AUTOSUCCESS', 'Pay Now')])),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=18, decimal_places=2)),
                ('exchange_rate', models.DecimalField(decimal_places=4, default=Decimal('1.00'), editable=False, max_digits=6, help_text='Rate from primary currency  at time of refund', verbose_name='Exchange Rate')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('transaction_id', models.CharField(max_length=25, null=True, verbose_name='Transaction ID', blank=True)),
                ('order', models.ForeignKey(related_name='refunds', to='shop.Order')),
            ],
            options={
                'verbose_name': 'Order Refund',
                'verbose_name_plural': 'Order Refunds',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='orderpayment',
            name='currency',
        ),
        migrations.AlterField(
            model_name='order',
            name='discount',
            field=models.DecimalField(null=True, verbose_name='Discount amount', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='refund',
            field=models.DecimalField(default=Decimal('0.00'), help_text='The amount refunded in the currency of the order', verbose_name='Refund', max_digits=18, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_cost',
            field=models.DecimalField(null=True, verbose_name='Shipping Cost', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_discount',
            field=models.DecimalField(null=True, verbose_name='Shipping Discount', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_model',
            field=satchmo.shipping.fields.ShippingChoiceCharField(max_length=30, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='sub_total',
            field=models.DecimalField(null=True, verbose_name='Subtotal', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='tax',
            field=models.DecimalField(null=True, verbose_name='Tax', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(null=True, verbose_name='Total', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='discount',
            field=models.DecimalField(null=True, verbose_name='Line item discount', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='line_item_price',
            field=models.DecimalField(verbose_name='Line item price', max_digits=18, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='tax',
            field=models.DecimalField(null=True, verbose_name='Line item tax', max_digits=18, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='unit_price',
            field=models.DecimalField(verbose_name='Unit price', max_digits=18, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='unit_tax',
            field=models.DecimalField(null=True, verbose_name='Unit tax', max_digits=18, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderitemdetail',
            name='price_change',
            field=models.DecimalField(null=True, verbose_name='Price Change', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='amount',
            field=models.DecimalField(null=True, verbose_name='amount', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=4, default=Decimal('1.00'), editable=False, max_digits=6, help_text='Rate from primary currency at time of payment', verbose_name='Exchange Rate'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='payment',
            field=satchmo.payment.fields.PaymentChoiceCharField(max_length=25, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ordertaxdetail',
            name='tax',
            field=models.DecimalField(null=True, verbose_name='Tax', max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
