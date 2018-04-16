# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0003_auto_20150304_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrier',
            name='estimated_delivery_expected_days',
            field=models.PositiveIntegerField(default=7, verbose_name='Usual number of days after shipping until delivery'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='carrier',
            name='estimated_delivery_max_days',
            field=models.PositiveIntegerField(default=25, verbose_name='Maximum number of days after shipping until delivery'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='carrier',
            name='estimated_delivery_min_days',
            field=models.PositiveIntegerField(default=1, verbose_name='Minimum number of days after shipping until delivery'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='carriertranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='zonetranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
    ]
