# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('brand', '0002_auto_20150207_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='last_restocked',
            field=models.DateField(help_text='Date of last restock', null=True, verbose_name='Last Restocked', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brand',
            name='restock_interval',
            field=models.IntegerField(help_text='Typical value in days between restocks', null=True, verbose_name='Restock Interval'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brand',
            name='stock_due_on',
            field=models.DateField(help_text='Date of next restock if known', null=True, verbose_name='Stock Due On', blank=True),
            preserve_default=True,
        ),
    ]
