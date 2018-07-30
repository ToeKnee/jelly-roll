# -*- coding: utf-8 -*-


from django.db import models, migrations
import satchmo.caching.models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LongSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100)),
                ('value', models.TextField(blank=True)),
                ('site', models.ForeignKey(verbose_name='Site',
                                           to='sites.Site', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'configuration_longsetting',
            },
            bases=(models.Model, satchmo.caching.models.CachedObjectMixin),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('group', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=255, blank=True)),
                ('site', models.ForeignKey(verbose_name='Site',
                                           to='sites.Site', on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'configuration_setting',
            },
            bases=(models.Model, satchmo.caching.models.CachedObjectMixin),
        ),
        migrations.AlterUniqueTogether(
            name='setting',
            unique_together={('site', 'group', 'key')},
        ),
        migrations.AlterUniqueTogether(
            name='longsetting',
            unique_together={('site', 'group', 'key')},
        ),
    ]
