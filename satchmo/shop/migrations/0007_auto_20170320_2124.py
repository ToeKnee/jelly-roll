# -*- coding: utf-8 -*-


from django.db import models, migrations
from decimal import Decimal
import satchmo.payment.fields
import satchmo.shipping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0007_auto_20170214_0926'),
        ('shop', '0006_auto_20160905_1952'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='currency',
            field=models.ForeignKey(related_name='orders', default=1, editable=False, to='currency.Currency', verbose_name='Currency'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='exchange_rate',
            field=models.DecimalField(decimal_places=4, default=Decimal('1.00'), editable=False, max_digits=6, help_text='Rate from primary currency', verbose_name='Exchange Rate'),
            preserve_default=True,
        )
    ]
