# Generated by Django 2.1.7 on 2019-04-17 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tieredweightzone', '0003_auto_20190417_1857'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carriertranslation',
            name='carrier',
        ),
        migrations.RemoveField(
            model_name='zonetranslation',
            name='zone',
        ),
        migrations.DeleteModel(
            name='CarrierTranslation',
        ),
        migrations.DeleteModel(
            name='ZoneTranslation',
        ),
    ]