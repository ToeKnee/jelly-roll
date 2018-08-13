# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('brand', '0004_auto_20160701_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brandtranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[
                                   (b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='brandtranslation',
            name='picture',
            field=models.ImageField(
                max_length=200, upload_to='brand/', null=True, verbose_name='Picture', blank=True),
            preserve_default=True,
        ),
    ]
