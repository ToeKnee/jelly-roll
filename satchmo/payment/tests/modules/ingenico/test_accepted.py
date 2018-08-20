from django.urls import reverse
from django.test import TestCase, RequestFactory

from satchmo.payment.modules.ingenico.views import accepted
from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import Order, NullCart


class AcceptedTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_order_unavailable(self):
        request = self.factory.get('/shop/checkout/ingenico/accepted/')
        request.session = {}

        response = accepted(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', reverse("satchmo_shop_home")))

    def test_order_unavailable__deletes_cart_from_session(self):
        request = self.factory.get('/shop/checkout/ingenico/accepted/')
        request.session = {
            "cart": NullCart()
        }

        response = accepted(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', reverse("satchmo_shop_home")))
        self.assertNotIn("cart", request.session)

    def test_order_unavailable__deletes_frozen_order_from_session(self):
        order = TestOrderFactory(frozen=True)
        request = self.factory.get('/shop/checkout/ingenico/accepted/')
        request.session = {
            "orderID": order.id,
        }
        request.user = order.contact.user

        response = accepted(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers['location'],
            ('Location', reverse("satchmo_order_tracking", kwargs={"order_id": order.id}))
        )

    def test_order_available(self):
        order = TestOrderFactory()

        request = self.factory.get('/shop/checkout/ingenico/accepted/')
        request.user = order.contact.user
        request.session = {
            "orderID": order.id,
        }

        response = accepted(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accepted".encode("utf-8"), response.content)
        self.assertIn("Paid through Ingenico".encode("utf-8"), response.content)
        for item in order.orderitem_set.all():
            self.assertIn(item.product.name.encode("utf-8"), response.content)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.status.status.status, "Accepted")
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, 0)
            self.assertEqual(item.product.total_sold, item.quantity)
