# Generated by Django 2.1 on 2018-08-23 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_auto_20180519_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpayment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Transaction ID'),
        ),
    ]