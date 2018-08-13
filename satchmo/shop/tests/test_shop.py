import warnings
from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse as url
from django.test import TestCase
from django.test.client import Client
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site

from satchmo.caching import cache_delete
from satchmo.configuration.functions import config_get, config_value
from satchmo.contact import CUSTOMER_ID
from satchmo.contact.models import Contact, AddressBook
from satchmo.l10n.factories import USFactory
from satchmo.l10n.models import Country
from satchmo.product.models import Product
from satchmo.shop.satchmo_settings import get_satchmo_setting
from satchmo.shop.models import (
    Order,
    OrderItem,
)
from .test_cart import CartTest

prefix = get_satchmo_setting('SHOP_BASE')
if prefix == '/':
    prefix = ''


def get_step1_post_data(US):
    return {
        'email': 'sometester@example.com',
        'first_name': 'Teddy',
        'last_name': 'Tester',
        'phone': '456-123-5555',
        'street1': '8299 Some Street',
        'city': 'Springfield',
        'state': 'MO',
        'postal_code': '81122',
        'country': US.pk,
        'ship_street1': '1011 Some Other Street',
        'ship_city': 'Springfield',
        'ship_state': 'MO',
        'ship_postal_code': '81123',
        'paymentmethod': 'PAYMENT_DUMMY',
        'copy_address': True
    }


class ShopTest(TestCase):
    def setUp(self):
        # Every test needs a client
        self.client = Client()
        self.US = USFactory()

    def tearDown(self):
        cache_delete()


#    def test_checkout(self):
#        """
#        Run through a full checkout process
#        """
#        print "TODO: Split this out, too much in one test"
#        # TODO: Split this out, too much in one test
#        cache_delete()
#        tax = config_get('TAX','MODULE')
#        tax.update('satchmo.tax.modules.percent')
#        pcnt = config_get('TAX', 'PERCENT')
#        pcnt.update('10')
#        shp = config_get('TAX', 'TAX_SHIPPING')
#        shp.update(False)
#
#        CartTest().test_cart_adding()
#        response = self.client.post(url('satchmo_checkout-step1'), get_step1_post_data(self.US))
#        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step2'),
#            status_code=302, target_status_code=200)
#        data = {
#            'credit_type': 'Visa',
#            'credit_number': '4485079141095836',
#            'month_expires': '1',
#            'year_expires': '2009',
#            'ccv': '552',
#            'shipping': 'FlatRate'}
#        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
#        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step3'),
#            status_code=302, target_status_code=200)
#        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))
#        self.assertContains(response, smart_str("Shipping + %s4.00" % config_value('CURRENCY', 'CURRENCY')), count=1, status_code=200)
#        self.assertContains(response, smart_str("Tax + %s4.60" % config_value('CURRENCY', 'CURRENCY')), count=1, status_code=200)
#        self.assertContains(response, smart_str("Total = %s54.60" % config_value('CURRENCY', 'CURRENCY')), count=1, status_code=200)
#        response = self.client.post(url('DUMMY_satchmo_checkout-step3'), {'process' : 'True'})
#        self.assertRedirects(response, url('DUMMY_satchmo_checkout-success'),
#            status_code=302, target_status_code=200)
#        self.assertEqual(len(mail.outbox), 1)
#
#        # Log in as a superuser
#        user = User.objects.create_user('fredsu', 'fred@root.org', 'passwd')
#        user.is_staff = True
#        user.is_superuser = True
#        user.save()
#        self.client.login(username='fredsu', password='passwd')
#
#        # Test pdf generation
#        response = self.client.get('/admin/print/invoice/1/')
#        self.assertContains(response, 'reportlab', status_code=200)
#        response = self.client.get('/admin/print/packingslip/1/')
#        self.assertContains(response, 'reportlab', status_code=200)
#        response = self.client.get('/admin/print/shippinglabel/1/')
#        self.assertContains(response, 'reportlab', status_code=200)

    def test_product(self):
        # Test for an easily missed reversion. When you lookup a productvariation product then
        # you should get the page of the parent configurableproduct, but with the options for
        # that variation already selected
        response = self.client.get(prefix + '/product/neat-book-soft/')
        self.assertContains(response, 'option value="soft" selected="selected"')
        self.assertContains(response, smart_str("%s5.00" % config_value('CURRENCY', 'CURRENCY')))

    def test_orphaned_product(self):
        """
        Get the page of a Product that is not in a Category.
        """
        Product.objects.create(name="Orphaned Product", slug="orphaned-product",
                               site=Site.objects.get_current())
        response = self.client.get(prefix + '/product/orphaned-product/')
        self.assertContains(response, 'Orphaned Product')

    def test_get_price(self):
        """
        Get the price and productname of a ProductVariation.
        """
        response = self.client.get(prefix + '/product/dj-rocks/')
        self.assertContains(response, "Django Rocks shirt", count=2, status_code=200)

        # this tests the unmolested price from the ConfigurableProduct, and
        # makes sure we get a good productname back for the ProductVariation
        response = self.client.post(prefix + '/product/dj-rocks/prices/', {"1": "S",
                                                                           "2": "B",
                                                                           "quantity": 1
                                                                           })
        content = response.content.split(',')
        self.assertEqual(content[0], '["dj-rocks-s-b"')
        self.assertTrue(content[1].endswith('20.00"]'))

        # This tests the option price_change feature, and again the productname
        response = self.client.post(prefix + '/product/dj-rocks/prices/', {"1": "L",
                                                                           "2": "BL",
                                                                           "quantity": 2})
        content = response.content.split(',')
        self.assertEqual(content[0], '["dj-rocks-l-bl"')
        self.assertTrue(content[1].endswith('23.00"]'))

    def test_contact_form(self):
        """
        Validate the contact form works
        """
        # TODO: Contact shouldn't be the shops
        response = self.client.get(prefix + '/contact/')
        self.assertContains(response, '<h3>Contact Information</h3>',
                            count=1, status_code=200)
        response = self.client.post(prefix + '/contact/', {'name': 'Test Runner',
                                                           'sender': 'Someone@testrunner.com',
                                                           'subject': 'A question to test',
                                                           'inquiry': 'General Question',
                                                           'contents': 'A lot of info goes here.'
                                                           })
        self.assertRedirects(response, prefix + '/contact/thankyou/',
                             status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'A question to test')

    def test_contact_login(self):
        """Check that when a user logs in, the user's existing Contact will be
        used.
        """
        user = User.objects.create_user('teddy', 'sometester@example.com', 'guz90tyc')
        Contact.objects.create(user=user, first_name="Teddy", last_name="Tester")
        self.client.login(username='teddy', password='guz90tyc')
        CartTest().test_cart_adding()
        response = self.client.get(url('satchmo_checkout-step1'))
        self.assertContains(response, "Teddy", status_code=200)

    def test_contact_attaches_to_user(self):
        """Check that if a User registers and later creates a Contact, the
        Contact will be attached to the existing User.
        """
        user = User.objects.create_user('teddy', 'sometester@example.com', 'guz90tyc')
        self.assertEqual(user.contact_set.count(), 0)
        self.client.login(username='teddy', password='guz90tyc')
        CartTest().test_cart_adding()
        self.client.post(prefix + '/checkout/', get_step1_post_data(self.US))
        self.assertEqual(user.contact_set.count(), 1)

    def test_logout(self):
        """The logout view should remove the user and contact id from the
        session.
        """
        User.objects.create_user('teddy', 'sometester@example.com', 'guz90tyc')
        self.client.login(username='teddy', password='guz90tyc')
        response = self.client.get('/accounts/')  # test logged in status
        self.assertContains(
            response, "the user you've logged in as doesn't have any contact information.", status_code=200)
        CartTest().test_cart_adding()
        self.client.post(prefix + '/checkout/', get_step1_post_data(self.US))
        self.assertTrue(self.client.session.get(CUSTOMER_ID) is not None)
        response = self.client.get('/accounts/logout/')
        # self.assertRedirects(response, prefix + '/',
        #    status_code=302, target_status_code=200)
        self.assertTrue(self.client.session.get(CUSTOMER_ID) is None)
        response = self.client.get('/accounts/')  # test logged in status
        self.assertRedirects(response, '/accounts/login/?next=/accounts/',
                             status_code=302, target_status_code=200)

    def test_search(self):
        """
        Do some basic searches to make sure it all works as expected
        """
        response = self.client.get(prefix + '/search/', {'keywords': 'python'})
        self.assertContains(response, "Python Rocks shirt", count=5)
        response = self.client.get(prefix + '/search/', {'keywords': 'django+book'})
        self.assertContains(response, "Sorry, your search did not return any results.")
        response = self.client.get(prefix + '/search/', {'keywords': 'shirt'})
        self.assertContains(response, "Shirts", count=2)
        self.assertContains(response, "Short Sleeve", count=2)
        self.assertContains(response, "Django Rocks shirt", count=5)
        self.assertContains(response, "Python Rocks shirt", count=5)

    def test_custom_product(self):
        """
        Verify that the custom product is working as expected.
        """
        pm = config_get("PRODUCT", "PRODUCT_TYPES")
        pm.update(["product::ConfigurableProduct", "product::ProductVariation",
                   "product::CustomProduct", "product::SubscriptionProduct"])

        response = self.client.get(prefix + "/")
        self.assertContains(response, "Computer", count=1)
        response = self.client.get(prefix + "/product/satchmo-computer/")
        self.assertContains(response, "Memory", count=1)
        self.assertContains(response, "Case", count=1)
        self.assertContains(response, "Monogram", count=1)
        response = self.client.post(prefix + '/cart/add/', {"productname": "satchmo-computer",
                                                            "5": "1.5gb",
                                                            "6": "mid",
                                                            "custom_monogram": "CBM",
                                                            "quantity": 1
                                                            })
        self.assertRedirects(response, prefix + '/cart/',
                             status_code=302, target_status_code=200)
        response = self.client.get(prefix + '/cart/')
        self.assertContains(response, '/satchmo-computer/">satchmo computer', status_code=200)
        self.assertContains(response, smart_str("%s168.00" %
                                                config_value('CURRENCY', 'CURRENCY')), count=4)
        self.assertContains(response, smart_str("Monogram: CBM  %s10.00" %
                                                config_value('CURRENCY', 'CURRENCY')), count=1)
        self.assertContains(response, smart_str("Case - External Case: Mid  %s10.00" %
                                                config_value('CURRENCY', 'CURRENCY')), count=1)
        self.assertContains(response, smart_str(
            "Memory - Internal RAM: 1.5 GB  %s25.00" % config_value('CURRENCY', 'CURRENCY')), count=1)
        response = self.client.post(url('satchmo_checkout-step1'), get_step1_post_data(self.US))
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step2'),
                             status_code=302, target_status_code=200)
        data = {
            'credit_type': 'Visa',
            'credit_number': '4485079141095836',
            'month_expires': '1',
            'year_expires': '2012',
            'ccv': '552',
            'shipping': 'FlatRate'}
        response = self.client.post(url('DUMMY_satchmo_checkout-step2'), data)
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-step3'),
                             status_code=302, target_status_code=200)
        response = self.client.get(url('DUMMY_satchmo_checkout-step3'))
        self.assertContains(response, smart_str("satchmo computer - %s168.00" %
                                                config_value('CURRENCY', 'CURRENCY')), count=1, status_code=200)
        response = self.client.post(url('DUMMY_satchmo_checkout-step3'), {'process': 'True'})
        self.assertRedirects(response, url('DUMMY_satchmo_checkout-success'),
                             status_code=302, target_status_code=200)
        self.assertEqual(len(mail.outbox), 1)


def make_test_order(country, state, include_non_taxed=False, site=None):
    warnings.warn("make_test_order is deprecated - Use TestOrderFactory instead", DeprecationWarning)
    if not site:
        site = Site.objects.get_current()
    c = Contact(first_name="Tax", last_name="Tester",
                role="Customer", email="tax@example.com")
    c.save()
    if not isinstance(country, Country):
        country = Country.objects.get(iso2_code__iexact=country)

    ad = AddressBook(contact=c, description="home",
                     street1="test", state=state, city="Portland",
                     country=country, is_default_shipping=True,
                     is_default_billing=True)
    ad.save()
    o = Order(contact=c, shipping_cost=Decimal('10.00'), site=site)
    o.save()

    p = Product.objects.get(slug='dj-rocks-s-b')
    price = p.unit_price
    item1 = OrderItem(order=o, product=p, quantity=5,
                      unit_price=price, line_item_price=price * 5)
    item1.save()

    if include_non_taxed:
        p = Product.objects.get(slug='neat-book-hard')
        price = p.unit_price
        item2 = OrderItem(order=o, product=p, quantity=1,
                          unit_price=price, line_item_price=price)
        item2.save()

    return o
