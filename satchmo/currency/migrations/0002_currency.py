# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('l10n', '0001_initial'),
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_4217_code', models.CharField(max_length=3, verbose_name='ISO 4217 code')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('symbol', models.CharField(max_length=5, verbose_name='Symbol')),
                ('minor_symbol', models.CharField(help_text='Pence, Cent, Sen, etc.', max_length=5, verbose_name='Minor Symbol')),
                ('countries', models.ManyToManyField(related_name='currency', to='l10n.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
