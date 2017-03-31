# -*- coding: utf-8 -*-
import factory

from decimal import Decimal

from satchmo.l10n.models import Country
from .models import Currency, ExchangeRate


class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Currency
        django_get_or_create = ('iso_4217_code',)

    iso_4217_code = "EUR"
    name = "Euro"
    symbol = "€"
    minor_symbol = "c"

    @factory.post_generation
    def countries(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

            if extracted:
                # A list of countries were passed in, use them
                for country in extracted:
                    self.countries.add(country)
            else:
                self.countries = Country.objects.filter(printable_name__in=[
                    "Austria", "Belgium", "Cyprus", "Estonia",
                    "Finland", "France", "Germany", "Greece",
                    "Ireland", "Italy", "Latvia", "Lithuania",
                    "Luxembourg", "Malta", "Netherlands", "Portugal",
                    "Slovakia", "Slovenia", "Spain"
                ])


class ExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExchangeRate

    currency = factory.LazyAttribute(lambda a: Currency.objects.get(iso_4217_code="GBP"))
    rate = Decimal("0.5")
