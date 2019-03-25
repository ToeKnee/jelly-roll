from unittest import skip
from django.test import TestCase
from satchmo.contact.forms import ContactInfoForm
from satchmo.contact.models import AddressBook, Contact, Organization, PhoneNumber
from satchmo.l10n.factories import USFactory, AUFactory, CAFactory
from satchmo.shop.factories import ShopConfigFactory
from satchmo.shop.models import Config


class ContactTest(TestCase):
    def setUp(self):
        self.us = USFactory.create()
        ShopConfigFactory.create(country=self.us)

    def test_base_contact(self):
        """Test creating a contact"""

        contact1 = Contact.objects.create(
            first_name="Jim",
            last_name="Tester",
            role="Customer",
            email="Jim@JimWorld.com",
        )

        self.assertEqual(contact1.full_name, "Jim Tester")

        # Add a phone number for this person and make sure that it's the default
        phone1 = PhoneNumber.objects.create(
            contact=contact1, type="Home", phone="800-111-9900"
        )
        self.assertTrue(contact1.primary_phone)
        self.assertEqual(contact1.primary_phone.phone, "800-111-9900")
        self.assertEqual(phone1.type, "Home")

        # Make sure that new primary phones become the default, and that
        # non-primary phones don't become the default when a default already exists.
        phone2 = PhoneNumber.objects.create(
            contact=contact1, type="Work", phone="800-222-9901", primary=True
        )
        PhoneNumber.objects.create(
            contact=contact1, type="Mobile", phone="800-333-9902"
        )
        self.assertEqual(contact1.primary_phone, phone2)

        # Add an address & make sure it is default billing and shipping
        add1 = AddressBook.objects.create(
            contact=contact1,
            description="Home Address",
            street1="56 Cool Lane",
            city="Niftyville",
            state="IA",
            postal_code="12344",
            country=self.us,
        )
        self.assertTrue(contact1.billing_address)
        self.assertEqual(contact1.billing_address, add1)
        self.assertEqual(contact1.billing_address.description, "Home Address")
        self.assertEqual(add1.street1, "56 Cool Lane")

        self.assertEqual(contact1.billing_address, contact1.shipping_address)
        self.assertEqual(contact1.billing_address.street1, "56 Cool Lane")

        # Add a new shipping address
        add2 = AddressBook(
            description="Work Address",
            street1="56 Industry Way",
            city="Niftytown",
            state="IA",
            postal_code="12366",
            country=self.us,
            is_default_shipping=True,
        )
        add2.contact = contact1
        add2.save()
        contact1.save()
        self.assertNotEqual(contact1.billing_address, contact1.shipping_address)
        self.assertEqual(contact1.billing_address.description, "Home Address")
        self.assertEqual(contact1.shipping_address.description, "Work Address")

    def test_contact_org(self):
        Contact.objects.create(
            first_name="Org",
            last_name="Tester",
            role="Customer",
            email="org@example.com",
        )
        org = Organization.objects.by_name("The Testers", create=True)
        self.assertTrue(org)
        self.assertEqual(org.role, "Customer")
        org2 = Organization.objects.by_name("The Testers", create=True)
        self.assertEqual(org, org2)


class ContactInfoFormTest(TestCase):
    def setUp(self):
        ShopConfigFactory.create()

    def test_missing_first_and_last_name_should_not_raise_exception(self):
        shop = Config.objects.get_current()
        form = ContactInfoForm(shop=shop, contact=None, data={"phone": "800-111-9900"})
        self.assertEqual(False, form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "city": ["This field is required."],
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "street1": ["This field is required."],
                "postal_code": ["This field is required."],
                "email": ["This field is required."],
            },
        )


class ContactInfoFormL10NTestUS(TestCase):
    def setUp(self):
        self.us = USFactory.create()
        ShopConfigFactory.create(country=self.us)
        self.shop = Config.objects.get_current()

    def test_company(self):
        data = {
            "email": "company@satchmoproject.com",
            "first_name": "Test",
            "last_name": "Company",
            "phone": "123-111-4411",
            "street1": "56 Cool Lane",
            "city": "Niftyville",
            "state": "IA",
            "postal_code": "12344",
            "country": self.us.id,
            "ship_street1": "56 Industry Way",
            "ship_city": "Niftytown",
            "ship_state": "IA",
            "ship_postal_code": "12366",
            "ship_country": self.us.id,
            "company": "Testers Anonymous",
        }
        contact = Contact.objects.create()
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(True, form.is_valid(), form.errors)
        contactid = form.save(contact)
        self.assertEqual(contact.id, contactid)
        self.assertTrue(contact.organization)
        self.assertEqual(contact.organization.name, "Testers Anonymous")

    def test_valid(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "56 Cool Lane",
            "city": "Niftyville",
            "state": "IA",
            "postal_code": "12344",
            "country": self.us.id,
            "ship_street1": "56 Industry Way",
            "ship_city": "Niftytown",
            "ship_state": "IA",
            "ship_postal_code": "12366",
            "ship_country": self.us.id,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(True, form.is_valid(), form.errors)

    @skip("Check state for USA addresses")
    def test_invalid_state(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "56 Cool Lane",
            "city": "Niftyville",
            "state": "ON",
            "postal_code": "12344",
            "country": self.us.id,
            "ship_street1": "56 Industry Way",
            "ship_city": "Niftytown",
            "ship_state": "ON",
            "ship_postal_code": "12366",
            "ship_country": self.us.id,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(False, form.is_valid(), form.errors)
        self.assertEqual(
            form.errors,
            {
                "country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ],
                "ship_country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ],
            },
        )


class ContactInfoFormL10NTestCA(TestCase):
    def setUp(self):
        self.ca = CAFactory.create()
        ShopConfigFactory.create(country=self.ca)
        self.shop = Config.objects.get_current()

    def test_valid(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "301 Front Street West",
            "city": "Toronto",
            "state": "ON",
            "postal_code": "M5V 2T6",
            "country": self.ca.id,
            "ship_street1": "301 Front Street West",
            "ship_city": "Toronto",
            "ship_state": "ON",
            "ship_postal_code": "M5V 2T6",
            "ship_country": self.ca.id,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(True, form.is_valid(), form.errors)

    @skip("Check province for Canadian addresses")
    def test_invalid_province(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "301 Front Street West",
            "city": "Toronto",
            "state": "NY",
            "postal_code": "M5V 2T6",
            "country": self.ca.id,
            "ship_street1": "301 Front Street West",
            "ship_city": "Toronto",
            "ship_state": "NY",
            "ship_postal_code": "M5V 2T6",
            "ship_country": self.ca.id,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(False, form.is_valid(), form.errors)
        self.assertEqual(
            form.errors,
            {
                "country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ],
                "ship_country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ],
            },
        )

    def test_invalid_postcode(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "301 Front Street West",
            "city": "Toronto",
            "state": "ON",
            "postal_code": "M5V 2TA",
            "country": self.ca.id,
            "ship_street1": "301 Front Street West",
            "ship_city": "Toronto",
            "ship_state": "ON",
            "ship_postal_code": "M5V 2TA",
            "ship_country": self.ca.id,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(False, form.is_valid(), form.errors)
        self.assertEqual(
            form.errors,
            {
                "ship_postal_code": ["Please enter a valid Canadian postal code."],
                "postal_code": ["Please enter a valid Canadian postal code."],
            },
        )


class ContactInfoFormL10NTestAU(TestCase):
    def setUp(self):
        self.au = AUFactory.create()
        ShopConfigFactory.create(country=self.au)
        self.shop = Config.objects.get_current()

    def test_valid(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "Macquarie Street",
            "city": "Sydney",
            "state": "NSW",
            "postal_code": "2000",
            "country": self.au.id,
            "ship_street1": "Macquarie Street",
            "ship_city": "Sydney",
            "ship_state": "NSW",
            "ship_postal_code": "2000",
            "ship_country": self.au.id,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(True, form.is_valid(), form.errors)

    def test_invalid_state(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "Macquarie Street",
            "city": "Sydney",
            "state": "NY",
            "postal_code": "2000",
            "country": 14,
            "ship_street1": "Macquarie Street",
            "ship_city": "Sydney",
            "ship_state": "NY",
            "ship_postal_code": "2000",
            "ship_country": 14,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(False, form.is_valid(), form.errors)
        self.assertEqual(
            form.errors,
            {
                "country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ],
                "ship_country": [
                    "Select a valid choice. That choice is not one of the available choices."
                ],
            },
        )

    def test_invalid_postal_code(self):
        contact = Contact.objects.create()
        data = {
            "email": "test_email@satchmoproject.com",
            "first_name": "Test",
            "last_name": "McTestalot",
            "phone": "123-111-4411",
            "street1": "Macquarie Street",
            "city": "Sydney",
            "state": "NSW",
            "postal_code": "200A",
            "country": self.au.id,
            "ship_street1": "Macquarie Street",
            "ship_city": "Sydney",
            "ship_state": "NSW",
            "ship_postal_code": "200A",
            "ship_country": self.au.id,
        }
        form = ContactInfoForm(data, shop=self.shop, contact=contact)
        self.assertEqual(False, form.is_valid(), form.errors)
        self.assertEqual(
            form.errors,
            {
                "ship_postal_code": ["Please enter a valid Australian postal code."],
                "postal_code": ["Please enter a valid Australian postal code."],
            },
        )
