import factory

from satchmo.l10n.models import Continent
from satchmo.l10n.models import Country


class ContinentFactory(factory.Factory):
    FACTORY_FOR = Continent

    code = "PG"
    name = "Patagonia"


class EUFactory(ContinentFactory):
    code = "EU"
    name = "Europe"


class NAFactory(ContinentFactory):
    code = "NA"
    name = "North America"


class OCFactory(ContinentFactory):
    code = "OC"
    name = "Oceania"


class CountryFactory(factory.Factory):
    FACTORY_FOR = Country

    iso2_code = "gb"
    name = "United Kingdom of Great Britain & Northern Ireland"
    printable_name = "United Kingdom"
    iso3_code = "gbr"
    numcode = 826
    active = True
    continent = factory.SubFactory(ContinentFactory)


class UKFactory(CountryFactory):
    iso2_code = "GB"
    name = "United Kingdom of Great Britain & Northern Ireland"
    printable_name = "United Kingdom"
    iso3_code = "GBR"
    numcode = 82
    continent = factory.SubFactory(EUFactory)


class USFactory(CountryFactory):
    iso2_code = "us"
    name = "United States"
    printable_name = "United States of America"
    iso3_code = "USA"
    numcode = 1
    continent = factory.SubFactory(NAFactory)


class CAFactory(CountryFactory):
    iso2_code = "CA"
    name = "Canada"
    printable_name = "Canada"
    iso3_code = "CAN"
    numcode = 124
    continent = factory.SubFactory(NAFactory)


class AUFactory(CountryFactory):
    iso2_code = "AU"
    name = "Australia"
    printable_name = "Australia"
    iso3_code = "AUS"
    numcode = 36
    continent = factory.SubFactory(OCFactory)
