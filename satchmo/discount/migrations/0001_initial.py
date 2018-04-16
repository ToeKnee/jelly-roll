# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100, verbose_name='Description')),
                ('code', models.CharField(help_text='Coupon Code', unique=True, max_length=20, verbose_name='Discount Code')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=4, blank=True, help_text='Enter absolute discount amount OR percentage.', null=True, verbose_name='Discount Amount')),
                ('percentage', models.DecimalField(decimal_places=2, max_digits=4, blank=True, help_text='Enter absolute discount amount OR percentage.  Percentage example: "0.10".', null=True, verbose_name='Discount Percentage')),
                ('automatic', models.NullBooleanField(default=False, help_text='Use this field to advertise the discount on all products to which it applies.  Generally this is used for site-wide sales.', verbose_name='Is this an automatic discount?')),
                ('allowedUses', models.IntegerField(default=1, help_text='How many uses are allowed of this discount', verbose_name='Number of allowed uses')),
                ('numUses', models.IntegerField(default=0, verbose_name='Number of times already used', editable=False)),
                ('minOrder', models.DecimalField(null=True, verbose_name='Minimum order value', max_digits=6, decimal_places=2, blank=True)),
                ('startDate', models.DateField(verbose_name='Start Date')),
                ('endDate', models.DateField(verbose_name='End Date')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('freeShipping', models.NullBooleanField(default=False, help_text='Should this discount remove all shipping costs?', verbose_name='Free shipping')),
                ('includeShipping', models.NullBooleanField(default=False, help_text='Should shipping be included in the discount calculation?', verbose_name='Include shipping')),
                ('site', models.ForeignKey(verbose_name='site', to='sites.Site')),
            ],
            options={
                'verbose_name': 'Discount',
                'verbose_name_plural': 'Discounts',
            },
            bases=(models.Model,),
        ),
    ]
