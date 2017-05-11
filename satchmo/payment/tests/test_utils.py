from django.test import TestCase, RequestFactory

from satchmo.contact.factories import ContactFactory
from satchmo.currency.factories import EURCurrencyFactory, USDCurrencyFactory
from satchmo.shop.factories import CartFactory, TestOrderFactory
from satchmo.shop.models import Order
from satchmo.payment.utils import get_or_create_order


class GetOrCreateOrderTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        EURCurrencyFactory(primary=True)

    def test_creates_order(self):
        usd = USDCurrencyFactory()
        usd.accepted = True
        usd.save()
        cart = CartFactory()
        contact = ContactFactory()
        data = {
            "shipping": None,
            "discount": None,
        }

        request = self.request_factory.get("/")
        request.session = {
            "currency_code": "USD"
        }

        order = get_or_create_order(request, cart, contact, data)
        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(order.contact, contact)
        self.assertEqual(order.currency.iso_4217_code, "USD")
        for item in cart.cartitem_set.all():
            self.assertIn(item.product, (oi.product for oi in order.orderitem_set.all()))

    def test_updates_order(self):
        contact = ContactFactory()
        cart = CartFactory()
        data = {
            "shipping": None,
            "discount": None,
        }
        order = TestOrderFactory(contact=contact)

        request = self.request_factory.get("/")
        request.session = {
            "orderID": order.id,
        }
        request.user = contact.user

        test_order = get_or_create_order(request, cart, contact, data)
        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(test_order.contact, contact)
        self.assertEqual(test_order.currency, order.currency)
        for item in cart.cartitem_set.all():
            self.assertIn(item.product, (oi.product for oi in test_order.orderitem_set.all()))
