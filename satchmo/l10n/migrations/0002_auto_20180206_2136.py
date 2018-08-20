# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('l10n', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ('printable_name',), 'verbose_name': 'Country', 'verbose_name_plural': 'Countries'},
        ),
        migrations.AlterField(
            model_name='adminarea',
            name='name',
            field=models.CharField(max_length=60, verbose_name='Admin Area name', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='country',
            name='printable_name',
            field=models.CharField(max_length=128, verbose_name='Country name', db_index=True),
            preserve_default=True,
        ),
    ]
