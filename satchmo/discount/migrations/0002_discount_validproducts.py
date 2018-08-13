# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('discount', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='discount',
            name='validProducts',
            field=models.ManyToManyField(help_text='Make sure not to include gift certificates!',
                                         to='product.Product', null=True, verbose_name='Valid Products', blank=True),
            preserve_default=True,
        ),
    ]
