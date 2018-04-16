# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_auto_20150713_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='enhanced_description',
            field=models.TextField(default=b'', help_text='Additional information about the product to appear below the fold.', verbose_name='Enhanced of product', blank=True),
            preserve_default=True,
        ),
    ]
