# Generated by Django 2.1.7 on 2019-04-24 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('brand', '0009_auto_20190424_1435'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brandtranslation',
            name='brand',
        ),
        migrations.DeleteModel(
            name='BrandTranslation',
        ),
    ]
