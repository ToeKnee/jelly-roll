import factory

from django.contrib.auth.models import User
from satchmo.contact.models import AddressBook, Contact
from satchmo.l10n.factories import CountryFactory


class AddressBookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AddressBook

    addressee = factory.LazyAttribute(lambda a: u'{0} {1}'.format(a.contact.first_name, a.contact.last_name))
    street1 = u"123 EZ Street"
    city = u"The big easy"
    postal_code = u"KY12 8OR"
    country = factory.SubFactory(CountryFactory)
    is_default_shipping = True
    is_default_billing = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = u'Joe'
    last_name = u'Bloggs'
    username = factory.LazyAttributeSequence(lambda a, n: '{0}-{1}-{2}'.format(a.first_name, a.last_name, n).lower())
    email = factory.LazyAttributeSequence(lambda a, n: '{0}+{1}@example.com'.format(a.username, n).lower())
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', "let-me-in")
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    first_name = factory.LazyAttribute(lambda a: a.user.first_name)
    last_name = factory.LazyAttribute(lambda a: a.user.last_name)
    email = factory.LazyAttribute(lambda a: u'{0}-{1}@example.com'.format(a.user.first_name, a.user.last_name).lower())
    user = factory.SubFactory(UserFactory)
    role = "Customer"

    @factory.post_generation
    def add_addressbook(obj, create, extracted, **kwargs):
        AddressBookFactory(contact=obj)
