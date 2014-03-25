import factory

from satchmo.discount.models import Discount


class DiscountFactory(factory.Factory):
    FACTORY_FOR = Discount

    site_id = 1
    store_name = "Test Shop"

    country = factory.LazyAttribute(lambda a: CountryFactory())
