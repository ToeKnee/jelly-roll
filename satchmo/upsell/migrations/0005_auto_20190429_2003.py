# Generated by Django 2.1.7 on 2019-04-29 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upsell', '0004_auto_20190429_2002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upselltranslation',
            name='menu',
        ),
        migrations.DeleteModel(
            name='UpsellTranslation',
        ),
    ]
