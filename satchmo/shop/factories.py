import factory

from satchmo.l10n.factories import CountryFactory
from satchmo.shop.models import Config


class ShopConfigFactory(factory.Factory):
    FACTORY_FOR = Config

    site_id = 1
    store_name = "Test Shop"

    country = factory.LazyAttribute(lambda a: CountryFactory())
