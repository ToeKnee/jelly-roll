from django.conf import settings
from django.test import TestCase, RequestFactory

from satchmo.payment.modules.ingenico.views import declined
from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import Order


class DeclinedTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_order_unavailable(self):
        request = self.factory.get("/shop/checkout/ingenico/declined/")
        request.session = {}

        response = declined(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers["location"],
            ("Location", "{}/".format(getattr(settings, "SHOP_BASE", "/store"))),
        )

    def test_order_available(self):
        order = TestOrderFactory()

        request = self.factory.get("/shop/checkout/ingenico/declined/")
        request.user = order.contact.user
        request.session = {"orderID": order.id}

        response = declined(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("declined".encode("utf-8"), response.content)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.status.status.status, "Declined")
