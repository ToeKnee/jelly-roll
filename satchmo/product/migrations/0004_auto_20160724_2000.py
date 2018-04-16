# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_enhanced_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryimage',
            name='picture',
            field=models.ImageField(upload_to=b'product-category/', max_length=200, verbose_name='Picture'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='categoryimagetranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='customtextfieldtranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='optiongrouptranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='optiontranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='enhanced_description',
            field=models.TextField(default=b'', help_text='Additional information about the product to appear below the fold.', verbose_name='Enhanced description of product', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='languagecode',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productimage',
            name='picture',
            field=models.ImageField(upload_to=b'products/', max_length=200, verbose_name='Picture'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productimagetranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='producttranslation',
            name='languagecode',
            field=models.CharField(max_length=10, verbose_name='language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
    ]
