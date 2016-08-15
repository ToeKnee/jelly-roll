import factory
from decimal import Decimal

from satchmo.l10n.factories import CountryFactory
from satchmo.shipping.models import ECONOMY
from .models import (
    Carrier,
    WeightTier,
    Zone,
)


class CarrierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Carrier

    key = factory.Sequence(lambda n: "carrier-{n}".format(n=n))
    active = True

    # Set to non default values
    signed_for = True
    tracked = True
    postage_speed = ECONOMY
    estimated_delivery_min_days = 2
    estimated_delivery_expected_days = 4
    estimated_delivery_max_days = 15


class ZoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Zone

    key = factory.Sequence(lambda n: "Zone {}".format(n))

    @factory.post_generation
    def set_location(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # Set up a country and a continent
        country = CountryFactory()
        self.country.add(country)
        self.continent.add(country.continent)


class WeightTierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WeightTier

    carrier = factory.SubFactory(CarrierFactory)
    zone = factory.SubFactory(ZoneFactory)
    min_weight = 0
    price = Decimal("1.00")
