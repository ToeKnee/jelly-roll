# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('brand', '0001_initial'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='categories',
            field=models.ManyToManyField(related_name='brands', verbose_name='Category', to='product.Category', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brand',
            name='products',
            field=models.ManyToManyField(related_name='brands', verbose_name='Products', to='product.Product', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='brand',
            name='site',
            field=models.ForeignKey(to='sites.Site'),
            preserve_default=True,
        ),
    ]
