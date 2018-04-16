# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0006_auto_20170206_2124'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Date', editable=False)),
                ('rate', models.DecimalField(help_text='Rate from primary currency', verbose_name='Rate', editable=False, max_digits=6, decimal_places=4)),
                ('currency', models.ForeignKey(related_name='exchange_rates', editable=False, to='currency.Currency')),
            ],
            options={
                'get_latest_by': 'date',
                'ordering': ('-date',),
                'verbose_name_plural': 'Exchange Rates',
                'verbose_name': 'Exchange Rate',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='exchangerate',
            unique_together={('currency', 'date')},
        ),
        migrations.AlterOrderWithRespectTo(
            name='exchangerate',
            order_with_respect_to='currency',
        ),
    ]
