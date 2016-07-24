# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
try:
    import satchmo.thumbnail.field
except ImportError:
    pass
import satchmo.product.models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('tax', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('slug', models.SlugField(help_text='Used for URLs, auto-generated from name if blank', verbose_name='Slug', blank=True)),
                ('active', models.BooleanField(default=False, verbose_name='Active')),
                ('meta', models.TextField(help_text='Meta description for this category', null=True, verbose_name='Meta Description', blank=True)),
                ('description', models.TextField(help_text=b'Optional', verbose_name='Description', blank=True)),
                ('ordering', models.IntegerField(default=0, help_text='Override alphabetical order in category display', verbose_name='Ordering')),
                ('parent', models.ForeignKey(related_name='child', blank=True, to='product.Category', null=True)),
                ('related_categories', models.ManyToManyField(related_name='related_categories_rel_+', null=True, verbose_name='Related Categories', to='product.Category', blank=True)),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            options={
                'ordering': ['site', 'parent__id', 'ordering', 'name'],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', models.ImageField(max_length=200, verbose_name='Picture')),
                ('caption', models.CharField(max_length=100, null=True, verbose_name='Optional caption', blank=True)),
                ('sort', models.IntegerField(verbose_name='Sort Order')),
                ('category', models.ForeignKey(related_name='images', blank=True, to='product.Category', null=True)),
            ],
            options={
                'ordering': ['sort'],
                'verbose_name': 'Category Image',
                'verbose_name_plural': 'Category Images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryImageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('caption', models.CharField(max_length=255, verbose_name='Translated Caption')),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('categoryimage', models.ForeignKey(related_name='translations', to='product.CategoryImage')),
            ],
            options={
                'ordering': ('categoryimage', 'caption', 'languagecode'),
                'verbose_name': 'Category Image Translation',
                'verbose_name_plural': 'Category Image Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.CharField(max_length=255, verbose_name='Translated Category Name')),
                ('description', models.TextField(default=b'', verbose_name='Description of category', blank=True)),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('category', models.ForeignKey(related_name='translations', to='product.Category')),
            ],
            options={
                'ordering': ('category', 'name', 'languagecode'),
                'verbose_name': 'Category Translation',
                'verbose_name_plural': 'Category Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomTextField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40, verbose_name='Custom field name')),
                ('slug', models.SlugField(help_text='Auto-generated from name if blank', verbose_name='Slug', blank=True)),
                ('sort_order', models.IntegerField(help_text='The display order for this group.', verbose_name='Sort Order')),
                ('price_change', models.DecimalField(null=True, verbose_name='Price Change', max_digits=14, decimal_places=6, blank=True)),
            ],
            options={
                'ordering': ('sort_order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomTextFieldTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.CharField(max_length=255, verbose_name='Translated Custom Text Field Name')),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('customtextfield', models.ForeignKey(related_name='translations', to='product.CustomTextField')),
            ],
            options={
                'ordering': ('customtextfield', 'name', 'languagecode'),
                'verbose_name': 'CustomTextField Translation',
                'verbose_name_plural': 'CustomTextField Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientsList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('ingredients', models.TextField(verbose_name='Ingredients listing')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('instructions', models.TextField(verbose_name='Usage Instructions')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Display value')),
                ('value', models.CharField(max_length=50, verbose_name='Stored value')),
                ('price_change', models.DecimalField(decimal_places=6, max_digits=14, blank=True, help_text='This is the price differential for this option.', null=True, verbose_name='Price Change')),
                ('sort_order', models.IntegerField(verbose_name='Sort Order')),
            ],
            options={
                'ordering': ('option_group', 'sort_order', 'name'),
                'verbose_name': 'Option Item',
                'verbose_name_plural': 'Option Items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OptionGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='This will be the text displayed on the product page.', max_length=50, verbose_name='Name of Option Group')),
                ('description', models.CharField(help_text='Further description of this group (i.e. shirt size vs shoe size).', max_length=100, verbose_name='Detailed Description', blank=True)),
                ('sort_order', models.IntegerField(help_text='The display order for this group.', verbose_name='Sort Order')),
                ('site', models.ForeignKey(verbose_name='Site', to='sites.Site')),
            ],
            options={
                'ordering': ['sort_order', 'name'],
                'verbose_name': 'Option Group',
                'verbose_name_plural': 'Option Groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OptionGroupTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.CharField(max_length=255, verbose_name='Translated OptionGroup Name')),
                ('description', models.TextField(default=b'', verbose_name='Description of OptionGroup', blank=True)),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('optiongroup', models.ForeignKey(related_name='translations', to='product.OptionGroup')),
            ],
            options={
                'ordering': ('optiongroup', 'name', 'languagecode'),
                'verbose_name': 'Option Group Translation',
                'verbose_name_plural': 'Option Groups Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OptionTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.CharField(max_length=255, verbose_name='Translated Option Name')),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('option', models.ForeignKey(related_name='translations', to='product.Option')),
            ],
            options={
                'ordering': ('option', 'name', 'languagecode'),
                'verbose_name': 'Option Translation',
                'verbose_name_plural': 'Option Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Precaution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('precautions', models.TextField(verbose_name='Precautions')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(verbose_name='Price', max_digits=14, decimal_places=6)),
                ('quantity', models.IntegerField(default=1, help_text='Use this price only for this quantity or higher', verbose_name='Discount Quantity')),
                ('expires', models.DateField(null=True, verbose_name='Expires', blank=True)),
            ],
            options={
                'ordering': ['expires', '-quantity'],
                'verbose_name': 'Price',
                'verbose_name_plural': 'Prices',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='This is what the product will be called in the default site language.  To add non-default translations, use the Product Translation section below.', max_length=255, verbose_name='Full Name')),
                ('slug', models.SlugField(help_text='Used for URLs, auto-generated from name if blank', max_length=80, verbose_name='Slug Name', blank=True)),
                ('sku', models.CharField(help_text='Defaults to slug if left blank', max_length=255, null=True, verbose_name='SKU', blank=True)),
                ('short_description', models.TextField(default=b'', help_text='This should be a 1 or 2 line description in the default site language for use in product listing screens', max_length=200, verbose_name='Short description of product', blank=True)),
                ('description', models.TextField(default=b'', help_text='This field can contain HTML and should be a few paragraphs in the default site language explaining the background of the product, and anything that would help the potential customer make their purchase.', verbose_name='Description of product', blank=True)),
                ('items_in_stock', models.IntegerField(default=0, verbose_name='Number in stock')),
                ('meta', models.TextField(help_text='Meta description for this product', max_length=200, null=True, verbose_name='Meta Description', blank=True)),
                ('date_added', models.DateField(verbose_name='Date added')),
                ('date_updated', models.DateField(verbose_name='Date updated')),
                ('active', models.BooleanField(default=True, help_text='This will determine whether or not this product will appear on the site', verbose_name='Is product active?')),
                ('featured', models.BooleanField(default=False, help_text='Featured items will show on the front page', verbose_name='Featured Item')),
                ('ordering', models.IntegerField(default=0, help_text='Override alphabetical order in category display', verbose_name='Ordering')),
                ('weight', models.DecimalField(null=True, verbose_name='Weight', max_digits=8, decimal_places=2, blank=True)),
                ('weight_units', models.CharField(max_length=3, null=True, verbose_name='Weight units', blank=True)),
                ('length', models.DecimalField(null=True, verbose_name='Length', max_digits=6, decimal_places=2, blank=True)),
                ('length_units', models.CharField(max_length=3, null=True, verbose_name='Length units', blank=True)),
                ('width', models.DecimalField(null=True, verbose_name='Width', max_digits=6, decimal_places=2, blank=True)),
                ('width_units', models.CharField(max_length=3, null=True, verbose_name='Width units', blank=True)),
                ('height', models.DecimalField(null=True, verbose_name='Height', max_digits=6, decimal_places=2, blank=True)),
                ('height_units', models.CharField(max_length=3, null=True, verbose_name='Height units', blank=True)),
                ('total_sold', models.IntegerField(default=0, verbose_name='Total sold')),
                ('taxable', models.BooleanField(default=False, verbose_name='Taxable')),
                ('shipclass', models.CharField(default=b'YES', help_text="If this is 'Default', then we'll use the product type to determine if it is shippable.", max_length=10, verbose_name='Shipping', choices=[(b'DEFAULT', 'Default'), (b'YES', 'Shippable'), (b'NO', 'Not Shippable')])),
            ],
            options={
                'ordering': ('site', 'ordering', 'name'),
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DownloadableProduct',
            fields=[
                ('product', models.OneToOneField(primary_key=True, serialize=False, to='product.Product', verbose_name='Product')),
                ('file', models.FileField(upload_to=satchmo.product.models._protected_dir, verbose_name='File')),
                ('num_allowed_downloads', models.IntegerField(help_text='Number of times link can be accessed.', verbose_name='Num allowed downloads')),
                ('expire_minutes', models.IntegerField(help_text='Number of minutes the link should remain active.', verbose_name='Expire minutes')),
                ('active', models.BooleanField(default=True, help_text='Is this download currently active?', verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Downloadable Product',
                'verbose_name_plural': 'Downloadable Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomProduct',
            fields=[
                ('product', models.OneToOneField(primary_key=True, serialize=False, to='product.Product', verbose_name='Product')),
                ('downpayment', models.IntegerField(default=20, verbose_name='Percent Downpayment')),
                ('deferred_shipping', models.BooleanField(default=False, help_text='Do not charge shipping at checkout for this item.', verbose_name='Deferred Shipping')),
                ('option_group', models.ManyToManyField(to='product.OptionGroup', verbose_name='Option Group', blank=True)),
            ],
            options={
                'verbose_name': 'Custom Product',
                'verbose_name_plural': 'Custom Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigurableProduct',
            fields=[
                ('product', models.OneToOneField(primary_key=True, serialize=False, to='product.Product', verbose_name='Product')),
                ('create_subs', models.BooleanField(default=False, help_text="Create ProductVariations for all this product's options.  To use this, you must first add an option, save, then return to this page and select this option.", verbose_name='Create Variations')),
                ('option_group', models.ManyToManyField(to='product.OptionGroup', verbose_name='Option Group', blank=True)),
            ],
            options={
                'verbose_name': 'Configurable Product',
                'verbose_name_plural': 'Configurable Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(blank=True, max_length=10, null=True, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.SlugField(max_length=100, verbose_name='Attribute Name')),
                ('value', models.CharField(max_length=255, verbose_name='Value')),
            ],
            options={
                'verbose_name': 'Product Attribute',
                'verbose_name_plural': 'Product Attributes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('picture', models.ImageField(max_length=200, verbose_name='Picture')),
                ('caption', models.CharField(max_length=100, null=True, verbose_name='Optional caption', blank=True)),
                ('sort', models.IntegerField(verbose_name='Sort Order')),
            ],
            options={
                'ordering': ['sort'],
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductImageTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('caption', models.CharField(max_length=255, verbose_name='Translated Caption')),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
                ('productimage', models.ForeignKey(related_name='translations', to='product.ProductImage')),
            ],
            options={
                'ordering': ('productimage', 'caption', 'languagecode'),
                'verbose_name': 'Product Image Translation',
                'verbose_name_plural': 'Product Image Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductPriceLookup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('siteid', models.IntegerField()),
                ('key', models.CharField(max_length=60, null=True)),
                ('parentid', models.IntegerField(null=True)),
                ('productslug', models.CharField(max_length=80)),
                ('price', models.DecimalField(max_digits=14, decimal_places=6)),
                ('quantity', models.IntegerField()),
                ('active', models.BooleanField(default=False)),
                ('discountable', models.BooleanField(default=False)),
                ('items_in_stock', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('languagecode', models.CharField(max_length=10, verbose_name='language', choices=[(b'af', b'Afrikaans'), (b'ar', b'Arabic'), (b'ast', b'Asturian'), (b'az', b'Azerbaijani'), (b'bg', b'Bulgarian'), (b'be', b'Belarusian'), (b'bn', b'Bengali'), (b'br', b'Breton'), (b'bs', b'Bosnian'), (b'ca', b'Catalan'), (b'cs', b'Czech'), (b'cy', b'Welsh'), (b'da', b'Danish'), (b'de', b'German'), (b'el', b'Greek'), (b'en', b'English'), (b'en-au', b'Australian English'), (b'en-gb', b'British English'), (b'eo', b'Esperanto'), (b'es', b'Spanish'), (b'es-ar', b'Argentinian Spanish'), (b'es-mx', b'Mexican Spanish'), (b'es-ni', b'Nicaraguan Spanish'), (b'es-ve', b'Venezuelan Spanish'), (b'et', b'Estonian'), (b'eu', b'Basque'), (b'fa', b'Persian'), (b'fi', b'Finnish'), (b'fr', b'French'), (b'fy', b'Frisian'), (b'ga', b'Irish'), (b'gl', b'Galician'), (b'he', b'Hebrew'), (b'hi', b'Hindi'), (b'hr', b'Croatian'), (b'hu', b'Hungarian'), (b'ia', b'Interlingua'), (b'id', b'Indonesian'), (b'io', b'Ido'), (b'is', b'Icelandic'), (b'it', b'Italian'), (b'ja', b'Japanese'), (b'ka', b'Georgian'), (b'kk', b'Kazakh'), (b'km', b'Khmer'), (b'kn', b'Kannada'), (b'ko', b'Korean'), (b'lb', b'Luxembourgish'), (b'lt', b'Lithuanian'), (b'lv', b'Latvian'), (b'mk', b'Macedonian'), (b'ml', b'Malayalam'), (b'mn', b'Mongolian'), (b'mr', b'Marathi'), (b'my', b'Burmese'), (b'nb', b'Norwegian Bokmal'), (b'ne', b'Nepali'), (b'nl', b'Dutch'), (b'nn', b'Norwegian Nynorsk'), (b'os', b'Ossetic'), (b'pa', b'Punjabi'), (b'pl', b'Polish'), (b'pt', b'Portuguese'), (b'pt-br', b'Brazilian Portuguese'), (b'ro', b'Romanian'), (b'ru', b'Russian'), (b'sk', b'Slovak'), (b'sl', b'Slovenian'), (b'sq', b'Albanian'), (b'sr', b'Serbian'), (b'sr-latn', b'Serbian Latin'), (b'sv', b'Swedish'), (b'sw', b'Swahili'), (b'ta', b'Tamil'), (b'te', b'Telugu'), (b'th', b'Thai'), (b'tr', b'Turkish'), (b'tt', b'Tatar'), (b'udm', b'Udmurt'), (b'uk', b'Ukrainian'), (b'ur', b'Urdu'), (b'vi', b'Vietnamese'), (b'zh-cn', b'Simplified Chinese'), (b'zh-hans', b'Simplified Chinese'), (b'zh-hant', b'Traditional Chinese'), (b'zh-tw', b'Traditional Chinese')])),
                ('name', models.CharField(max_length=255, verbose_name='Full Name')),
                ('description', models.TextField(default=b'', help_text='This field can contain HTML and should be a few paragraphs explaining the background of the product, and anything that would help the potential customer make their purchase.', verbose_name='Description of product', blank=True)),
                ('short_description', models.TextField(default=b'', help_text='This should be a 1 or 2 line description for use in product listing screens', max_length=200, verbose_name='Short description of product', blank=True)),
                ('version', models.IntegerField(default=1, verbose_name='version')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
            ],
            options={
                'ordering': ('product', 'name', 'languagecode'),
                'verbose_name': 'Product Translation',
                'verbose_name_plural': 'Product Translations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductVariation',
            fields=[
                ('product', models.OneToOneField(primary_key=True, serialize=False, to='product.Product', verbose_name='Product')),
                ('options', models.ManyToManyField(to='product.Option', verbose_name='Options')),
                ('parent', models.ForeignKey(verbose_name='Parent', to='product.ConfigurableProduct')),
            ],
            options={
                'verbose_name': 'Product variation',
                'verbose_name_plural': 'Product variations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionProduct',
            fields=[
                ('product', models.OneToOneField(primary_key=True, serialize=False, to='product.Product', verbose_name='Product')),
                ('recurring', models.BooleanField(default=False, help_text='Customer will be charged the regular product price on a periodic basis.', verbose_name='Recurring Billing')),
                ('recurring_times', models.IntegerField(help_text='Number of payments which will occur at the regular rate.  (optional)', null=True, verbose_name='Recurring Times', blank=True)),
                ('expire_length', models.IntegerField(help_text='Length of each billing cycle', null=True, verbose_name='Duration', blank=True)),
                ('expire_unit', models.CharField(default=b'DAY', max_length=5, verbose_name='Expire Unit', choices=[(b'DAY', 'Days'), (b'MONTH', 'Months')])),
                ('is_shippable', models.IntegerField(help_text='Is this product shippable?', max_length=1, verbose_name='Shippable?', choices=[(b'0', 'No Shipping Charges'), (b'1', 'Pay Shipping Once'), (b'2', 'Pay Shipping Each Billing Cycle')])),
            ],
            options={
                'verbose_name': 'Subscription Product',
                'verbose_name_plural': 'Subscription Products',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Trial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(help_text='Set to 0 for a free trial.  Leave empty if product does not have a trial.', null=True, verbose_name='Price', max_digits=10, decimal_places=2)),
                ('expire_length', models.IntegerField(help_text='Length of trial billing cycle.  Leave empty if product does not have a trial.', null=True, verbose_name='Trial Duration', blank=True)),
                ('subscription', models.ForeignKey(to='product.SubscriptionProduct')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'Trial Terms',
                'verbose_name_plural': 'Trial Terms',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='producttranslation',
            name='product',
            field=models.ForeignKey(related_name='translations', to='product.Product'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='producttranslation',
            unique_together=set([('product', 'languagecode', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='productimagetranslation',
            unique_together=set([('productimage', 'languagecode', 'version')]),
        ),
        migrations.AddField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(blank=True, to='product.Product', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productattribute',
            name='product',
            field=models.ForeignKey(to='product.Product'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='also_purchased',
            field=models.ManyToManyField(related_name='also_purchased_rel_+', null=True, verbose_name='Previously Purchased', to='product.Product', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ManyToManyField(to='product.Category', verbose_name='Category', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='ingredients',
            field=models.ForeignKey(blank=True, to='product.IngredientsList', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='instructions',
            field=models.ForeignKey(blank=True, to='product.Instruction', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='precautions',
            field=models.ForeignKey(blank=True, to='product.Precaution', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='related_items',
            field=models.ManyToManyField(related_name='related_items_rel_+', null=True, verbose_name='Related Items', to='product.Product', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='site',
            field=models.ForeignKey(verbose_name='Site', to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='taxClass',
            field=models.ForeignKey(blank=True, to='tax.TaxClass', help_text='If it is taxable, what kind of tax?', null=True, verbose_name='Tax Class'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('site', 'slug'), ('site', 'sku')]),
        ),
        migrations.AddField(
            model_name='price',
            name='product',
            field=models.ForeignKey(to='product.Product'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='price',
            unique_together=set([('product', 'quantity', 'expires')]),
        ),
        migrations.AlterUniqueTogether(
            name='optiontranslation',
            unique_together=set([('option', 'languagecode', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='optiongrouptranslation',
            unique_together=set([('optiongroup', 'languagecode', 'version')]),
        ),
        migrations.AddField(
            model_name='option',
            name='option_group',
            field=models.ForeignKey(to='product.OptionGroup'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('option_group', 'value')]),
        ),
        migrations.AlterUniqueTogether(
            name='customtextfieldtranslation',
            unique_together=set([('customtextfield', 'languagecode', 'version')]),
        ),
        migrations.AddField(
            model_name='customtextfield',
            name='products',
            field=models.ForeignKey(related_name='custom_text_fields', verbose_name='Custom Fields', to='product.CustomProduct'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='categorytranslation',
            unique_together=set([('category', 'languagecode', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='categoryimagetranslation',
            unique_together=set([('categoryimage', 'languagecode', 'version')]),
        ),
        migrations.AlterUniqueTogether(
            name='categoryimage',
            unique_together=set([('category', 'sort')]),
        ),
    ]
