from django.conf import settings
from django.test import TestCase, RequestFactory

from satchmo.payment.modules.ingenico.views import accepted
from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import Order


class AcceptedTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_order_unavailable(self):
        request = self.factory.get('/shop/checkout/ingenico/accepted/')
        request.session = {}

        response = accepted(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'], ('Location', '{}/'.format(getattr(settings, "SHOP_BASE", "/store"))))

    def test_order_available(self):
        order = TestOrderFactory()

        request = self.factory.get('/shop/checkout/ingenico/accepted/')
        request.user = order.contact.user
        request.session = {
            "orderID": order.id,
        }

        response = accepted(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Accepted", response.content)
        self.assertIn("Paid through Ingenico", response.content)
        for item in order.orderitem_set.all():
            self.assertIn(item.product.name, response.content.decode("utf-8"))

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.status.status.status, "Accepted")
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, 0)
            self.assertEqual(item.product.total_sold, item.quantity)
