# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(
                    max_length=60, verbose_name='Admin Area name')),
                ('abbrev', models.CharField(max_length=3, null=True,
                                            verbose_name='Postal Abbreviation', blank=True)),
                ('active', models.BooleanField(
                    default=True, verbose_name='Area is active')),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'l10n_adminarea',
                'verbose_name': 'Administrative Area',
                'verbose_name_plural': 'Administrative Areas',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True,
                                          max_length=2, verbose_name='2 letter code')),
                ('name', models.CharField(max_length=128, verbose_name='Official name')),
            ],
            options={
                'db_table': 'l10n_continent',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('iso2_code', models.CharField(unique=True,
                                               max_length=2, verbose_name='ISO alpha-2')),
                ('name', models.CharField(max_length=128,
                                          verbose_name='Official name (CAPS)')),
                ('printable_name', models.CharField(
                    max_length=128, verbose_name='Country name')),
                ('iso3_code', models.CharField(unique=True,
                                               max_length=3, verbose_name='ISO alpha-3')),
                ('numcode', models.PositiveSmallIntegerField(
                    null=True, verbose_name='ISO numeric', blank=True)),
                ('active', models.BooleanField(
                    default=True, verbose_name='Country is active')),
                ('admin_area', models.CharField(blank=True, max_length=2, null=True, verbose_name='Administrative Area', choices=[(b'a', 'Another'), (b'i', 'Island'), (b'ar', 'Arrondissement'), (b'at', 'Atoll'), (b'ai', 'Autonomous island'), (b'ca', 'Canton'), (b'cm', 'Commune'), (b'co', 'County'), (b'dp', 'Department'), (b'de', 'Dependency'), (b'dt', 'District'), (b'dv', 'Division'), (
                    b'em', 'Emirate'), (b'gv', 'Governorate'), (b'ic', 'Island council'), (b'ig', 'Island group'), (b'ir', 'Island region'), (b'kd', 'Kingdom'), (b'mu', 'Municipality'), (b'pa', 'Parish'), (b'pf', 'Prefecture'), (b'pr', 'Province'), (b'rg', 'Region'), (b'rp', 'Republic'), (b'sh', 'Sheading'), (b'st', 'State'), (b'sd', 'Subdivision'), (b'sj', 'Subject'), (b'ty', 'Territory')])),
                ('eu', models.BooleanField(default=False,
                                           verbose_name='Country is a member of the European Union')),
                ('continent', models.ForeignKey(to='l10n.Continent',
                                                to_field='code', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'l10n_country',
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='adminarea',
            name='country',
            field=models.ForeignKey(
                to='l10n.Country', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
