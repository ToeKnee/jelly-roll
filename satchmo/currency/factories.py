# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import factory

from decimal import Decimal

from satchmo.l10n.factories import UKFactory, USFactory
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
    primary = True
    accepted = True


class EURCurrencyFactory(CurrencyFactory):
    primary = False

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
            countries = [
                "Austria", "Belgium", "Cyprus", "Estonia",
                "Finland", "France", "Germany", "Greece",
                "Ireland", "Italy", "Latvia", "Lithuania",
                "Luxembourg", "Malta", "Netherlands", "Portugal",
                "Slovakia", "Slovenia", "Spain"
            ]

            self.countries = Country.objects.filter(printable_name__in=countries)


class GBPCurrencyFactory(CurrencyFactory):
    iso_4217_code = "GBP"
    name = "Pounds"
    symbol = "£"
    minor_symbol = "p"
    primary = False

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
            countries = [
                "United Kingdom", "Guernsey", "Isle of Man", "Jersey"
            ]

            self.countries = Country.objects.filter(printable_name__in=countries)

            if len(self.countries.all()) == 0:
                self.countries.add(UKFactory())


class USDCurrencyFactory(CurrencyFactory):
    iso_4217_code = "USD"
    name = "U.S. Dollar"
    symbol = "$"
    minor_symbol = "c"
    primary = False

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
            countries = [
                "United States of America",
                "Timor-Leste", "Ecuador", "El Salvador", "Marshall Islands",
                "Micronesia, Federated States of", "Palau",
                "Panama", "Zimbabwe"
            ]

            self.countries = Country.objects.filter(printable_name__in=countries)
            if len(self.countries.all()) == 0:
                self.countries.add(USFactory())


class ExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExchangeRate

    currency = factory.LazyAttribute(lambda a: Currency.objects.get(iso_4217_code="GBP"))
    rate = Decimal("0.5")
