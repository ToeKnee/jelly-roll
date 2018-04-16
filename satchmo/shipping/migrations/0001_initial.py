# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('l10n', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(verbose_name='Key')),
                ('ordering', models.IntegerField(default=0, verbose_name='Ordering')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'db_table': 'tieredweightzone_carrier',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CarrierTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.CharField(max_length=50, verbose_name='Carrier')),
                ('description', models.CharField(max_length=200, verbose_name='Description')),
                ('method', models.CharField(help_text='i.e. US Mail', max_length=200, verbose_name='Method')),
                ('delivery', models.CharField(max_length=200, verbose_name='Delivery Days')),
                ('carrier', models.ForeignKey(related_name='translations', to='shipping.Carrier')),
            ],
            options={
                'ordering': ('languagecode', 'name'),
                'db_table': 'tieredweightzone_carriertranslation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShippingDiscount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.IntegerField(verbose_name='Percentage Discount')),
                ('minimum_order_value', models.DecimalField(verbose_name='Minimum Order Value', max_digits=10, decimal_places=2)),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('end_date', models.DateField(null=True, verbose_name='End Date', blank=True)),
                ('carrier', models.ForeignKey(related_name='shipping_discount', to='shipping.Carrier')),
            ],
            options={
                'db_table': 'tieredweightzone_shippingdiscount',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WeightTier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_weight', models.DecimalField(help_text='The minumum weight for this tier to apply', verbose_name='Min Weight', max_digits=10, decimal_places=2)),
                ('price', models.DecimalField(verbose_name='Shipping Price', max_digits=10, decimal_places=2)),
                ('expires', models.DateField(null=True, verbose_name='Expires', blank=True)),
                ('carrier', models.ForeignKey(related_name='tiers', to='shipping.Carrier')),
            ],
            options={
                'ordering': ('zone', 'carrier', 'price'),
                'db_table': 'tieredweightzone_weighttier',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(verbose_name='Key')),
                ('continent', models.ManyToManyField(related_name='continent', db_table=b'tieredweightzone_zone_continent', to='l10n.Continent')),
                ('country', models.ManyToManyField(related_name='zone', null=True, to='l10n.Country', db_table=b'tieredweightzone_zone_country', blank=True)),
            ],
            options={
                'db_table': 'tieredweightzone_zone',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ZoneTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.CharField(max_length=50, verbose_name='Zone')),
                ('description', models.CharField(max_length=200, verbose_name='Description')),
                ('zone', models.ForeignKey(related_name='translations', to='shipping.Zone')),
            ],
            options={
                'ordering': ('languagecode', 'name'),
                'db_table': 'tieredweightzone_zonetranslation',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='weighttier',
            name='zone',
            field=models.ForeignKey(related_name='tiers', to='shipping.Zone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shippingdiscount',
            name='zone',
            field=models.ForeignKey(related_name='shipping_discount', to='shipping.Zone'),
            preserve_default=True,
        ),
    ]
