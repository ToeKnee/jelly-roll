# -*- coding: utf-8 -*-


from django.core.management import call_command
from django.db import migrations


class Migration(migrations.Migration):
    def setup_currencies(apps, schema_editor):
        Country = apps.get_model("l10n", "Country")
        Currency = apps.get_model("currency", "Currency")

        if Country.objects.all().count() == 0:
            call_command('loaddata', "l10n_data", app_label='l10n')

        data = [
            {
                "iso_4217_code": "EUR",
                "name": "Euro",
                "symbol": "€",
                "minor_symbol": "c",
                "countries": [
                    "Austria", "Belgium", "Cyprus", "Estonia",
                    "Finland", "France", "Germany", "Greece",
                    "Ireland", "Italy", "Latvia", "Lithuania",
                    "Luxembourg", "Malta", "Netherlands", "Portugal",
                    "Slovakia", "Slovenia", "Spain"
                ]
            },
            {
                "iso_4217_code": "GBP",
                "name": "Pound Sterling",
                "symbol": "£",
                "minor_symbol": "p",
                "countries": [
                    "United Kingdom", "Guernsey", "Isle of Man",
                    "Jersey"
                ]
            },
            {
                "iso_4217_code": "USD",
                "name": "U.S. Dollar",
                "symbol": "$",
                "minor_symbol": "c",
                "countries": [
                    "United States of America",
                    "Timor-Leste", "Ecuador", "El Salvador", "Marshall Islands",
                    "Micronesia, Federated States of", "Palau",
                    "Panama", "Zimbabwe"
                ]
            },
        ]
        for datum in data:
            currency, created = Currency.objects.get_or_create(
                iso_4217_code=datum["iso_4217_code"],
                name=datum["name"],
                symbol=datum["symbol"],
                minor_symbol=datum["minor_symbol"],
            )
            for country in datum["countries"]:
                currency.countries.add(Country.objects.get(printable_name=country))

    dependencies = [
        ('l10n', '0001_initial'),
        ('currency', '0002_currency'),
    ]

    operations = [
        migrations.RunPython(setup_currencies),
    ]
