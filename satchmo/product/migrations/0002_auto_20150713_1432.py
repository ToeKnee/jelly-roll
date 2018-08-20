# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='productimage',
            name='is_swatch',
            field=models.BooleanField(default=True, verbose_name='Is Swatch'),
            preserve_default=True,
        ),
    ]
