import factory

from decimal import Decimal

from .models import Currency, ExchangeRate


class ExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExchangeRate

    currency = factory.LazyAttribute(lambda a: Currency.objects.get(iso_4217_code="GBP"))
    rate = Decimal("0.5")
