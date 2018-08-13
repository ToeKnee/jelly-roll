# Generated by Django 2.0.5 on 2018-05-19 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('l10n', '0002_auto_20180206_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='admin_area',
            field=models.CharField(blank=True, choices=[('a', 'Another'), ('i', 'Island'), ('ar', 'Arrondissement'), ('at', 'Atoll'), ('ai', 'Autonomous island'), ('ca', 'Canton'), ('cm', 'Commune'), ('co', 'County'), ('dp', 'Department'), ('de', 'Dependency'), ('dt', 'District'), ('dv', 'Division'), ('em', 'Emirate'), ('gv', 'Governorate'), ('ic', 'Island council'), ('ig', 'Island group'), ('ir', 'Island region'), ('kd', 'Kingdom'), ('mu', 'Municipality'), ('pa', 'Parish'), ('pf', 'Prefecture'), ('pr', 'Province'), ('rg', 'Region'), ('rp', 'Republic'), ('sh', 'Sheading'), ('st', 'State'), ('sd', 'Subdivision'), ('sj', 'Subject'), ('ty', 'Territory')], max_length=2, null=True, verbose_name='Administrative Area'),
        ),
    ]
