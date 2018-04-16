# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('l10n', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='Displayed title of this tax.', max_length=20, verbose_name='Title')),
                ('description', models.CharField(help_text='Description of products that would be taxed.', max_length=30, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Tax Class',
                'verbose_name_plural': 'Tax Classes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaxRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.DecimalField(help_text='% tax for this area and type', verbose_name='Percentage', max_digits=7, decimal_places=6)),
                ('taxClass', models.ForeignKey(verbose_name='Tax Class', to='tax.TaxClass')),
                ('taxCountry', models.ForeignKey(verbose_name='Tax Country', blank=True, to='l10n.Country', null=True)),
                ('taxZone', models.ForeignKey(verbose_name='Tax Zone', blank=True, to='l10n.AdminArea', null=True)),
            ],
            options={
                'verbose_name': 'Tax Rate',
                'verbose_name_plural': 'Tax Rates',
            },
            bases=(models.Model,),
        ),
    ]
