# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('brand', '0003_auto_20150531_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='brandtranslation',
            name='meta_description',
            field=models.TextField(verbose_name='Meta Description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='brandtranslation',
            name='description',
            field=models.TextField(verbose_name='Full description, visible to customers', blank=True),
            preserve_default=True,
        ),
    ]
