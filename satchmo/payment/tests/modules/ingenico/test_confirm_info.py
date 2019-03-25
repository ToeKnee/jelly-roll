import hashlib

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from satchmo.caching import cache_delete
from satchmo.configuration.models import Setting
from satchmo.currency.factories import EURCurrencyFactory
from satchmo.payment.modules.ingenico.views import confirm_info
from satchmo.shop.factories import CartFactory, TestOrderFactory


class ConfirmInfoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        EURCurrencyFactory(primary=True)

    def tearDown(self):
        cache_delete()

    def test_order_unavailable(self):
        request = self.factory.get("/shop/checkout/ingenico/confirm/")
        request.user = AnonymousUser()
        request.session = {}

        response = confirm_info(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers["location"],
            ("Location", "{}/".format(getattr(settings, "SHOP_BASE", "/store"))),
        )

    def test_not_enough_stock(self):
        cart = CartFactory()
        order = TestOrderFactory()
        # Make all items out of stock
        for item in cart.cartitem_set.all():
            item.product.items_in_stock = 0
            item.product.save()

        request = self.factory.get("/shop/checkout/ingenico/confirm/")
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

    def test_form_includes_shasign(self):
        order = TestOrderFactory()

        request = self.factory.get("/shop/checkout/ingenico/confirm/")
        request.user = order.contact.user
        request.session = {"orderID": order.id}

        response = confirm_info(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("SHASIGN".encode("utf-8"), response.content)
        self.assertNotIn("ALIAS".encode("utf-8"), response.content)
        self.assertNotIn("ALIASUSAGE".encode("utf-8"), response.content)

    def test_form_includes_alias__if_enabled(self):
        # Enable Aliasing
        Setting.objects.create(key="ALIAS", group="PAYMENT_INGENICO", value=True)

        order = TestOrderFactory()

        request = self.factory.get("/shop/checkout/ingenico/confirm/")
        request.user = order.contact.user
        request.session = {"orderID": order.id}

        response = confirm_info(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("ALIAS".encode("utf-8"), response.content)
        self.assertIn(
            hashlib.sha512(order.contact.user.username.encode("utf-8"))
            .hexdigest()[:50]
            .encode("utf-8"),
            response.content,
        )
        self.assertIn("ALIASUSAGE".encode("utf-8"), response.content)
