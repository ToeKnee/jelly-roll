# -*- coding: utf-8 -*-


from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0007_auto_20170214_0926'),
        ('shop', '0009_auto_20170503_0917'),
    ]

    def set_primary_currency(apps, schema_editor):
        """ Set the OrderPayment currency to the primary currency

        """
        Currency = apps.get_model("currency", "Currency")
        OrderPayment = apps.get_model("shop", "OrderPayment")
        currency = Currency.objects.get(primary=True)
        OrderPayment.objects.update(currency=currency)

    operations = [
        migrations.AddField(
            model_name='orderpayment',
            name='currency',
            field=models.ForeignKey(related_name='order_payments', default=1, editable=False, to='currency.Currency', verbose_name='Currency'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderpayment',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=4, default=Decimal('1.00'), editable=False, max_digits=6, help_text='Rate from primary currency', verbose_name='Exchange Rate'),
            preserve_default=True,
        ),
        migrations.RunPython(set_primary_currency),

    ]
