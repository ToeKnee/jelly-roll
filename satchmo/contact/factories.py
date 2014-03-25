import factory

from satchmo.contact.models import AddressBook, Contact
from satchmo.l10n.factories import CountryFactory


class AddressBookFactory(factory.Factory):
    FACTORY_FOR = AddressBook

    addressee = factory.LazyAttribute(lambda a: '{0} {1}'.format(a.contact.first_name, a.contact.last_name))
    street1 = "123 EZ Street"
    city = "The big easy"
    postal_code = "KY12 *OR"
    country = factory.SubFactory(CountryFactory)
    is_default_shipping = True
    is_default_billing = True


class ContactFactory(factory.Factory):
    FACTORY_FOR = Contact

    first_name = "Joe"
    last_name = "Bloggs"
    email = factory.LazyAttribute(lambda a: '{0}-{1}@example.com'.format(a.first_name, a.last_name).lower())
    role = "Customer"

    addressbook = factory.RelatedFactory(AddressBookFactory)
