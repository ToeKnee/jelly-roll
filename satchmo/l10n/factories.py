import factory

from satchmo.l10n.models import Continent
from satchmo.l10n.models import Country


class ContinentFactory(factory.Factory):
    FACTORY_FOR = Continent

    code = "eu"
    name = "Europe"


class CountryFactory(factory.Factory):
    FACTORY_FOR = Country

    iso2_code = "gb"
    name = "United Kingdom of Great Britain & Northern Ireland"
    printable_name = "United Kingdom"
    iso3_code = "gbr"
    numcode = 826
    active = True
    continent = factory.LazyAttribute(lambda a: ContinentFactory())
