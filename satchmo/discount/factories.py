import factory

from satchmo.discount.models import Discount


class DiscountFactory(factory.Factory):
    FACTORY_FOR = Discount

    store_name = "Test Shop"

    country = factory.LazyAttribute(lambda a: CountryFactory())
