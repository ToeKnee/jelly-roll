import hashlib

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse


from satchmo.caching import cache_delete
from satchmo.currency.factories import EURCurrencyFactory
from satchmo.payment.modules.paypal.views import confirm_info
from satchmo.shop.factories import CartFactory, ShopConfigFactory, TestOrderFactory


class ConfirmInfoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        EURCurrencyFactory(primary=True)

    def tearDown(self):
        cache_delete()

    def test_order_unavailable(self):
        request = self.factory.get("/shop/checkout/paypal/confirm/")
        request.user = AnonymousUser()
        request.session = {}

        response = confirm_info(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers["location"],
            ("Location", reverse("satchmo_checkout-step1")),
        )

    def test_not_enough_stock(self):
        ShopConfigFactory()
        cart = CartFactory()
        order = TestOrderFactory()
        # Make all items out of stock
        for item in cart.cartitem_set.all():
            item.product.items_in_stock = 0
            item.product.save()

        request = self.factory.get("/shop/checkout/paypal/confirm/")
        request.user = order.contact.user
        request.session = {
            "cart": cart.id,
            "custID": cart.customer.id,
            "orderID": order.id,
        }

        response = confirm_info(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers["location"],
            ("Location", "{}/cart/".format(getattr(settings, "SHOP_BASE", "/store"))),
        )
