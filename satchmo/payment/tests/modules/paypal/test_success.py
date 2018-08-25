from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse

from satchmo.caching import cache_delete
from satchmo.currency.factories import EURCurrencyFactory
from satchmo.payment.modules.paypal.views import success
from satchmo.shop.factories import TestOrderFactory


class ConfirmInfoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        EURCurrencyFactory(primary=True)

    def tearDown(self):
        cache_delete()

    def test_order_unavailable(self):
        request = self.factory.get('/shop/checkout/paypal/success/')
        request.user = AnonymousUser()
        request.session = {}

        response = success(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers['location'],
            (
                'Location',
                reverse('satchmo_order_history')
            )
        )

    def test_success(self):
        order = TestOrderFactory()
        request = self.factory.get('/shop/checkout/paypal/success/')
        request.user = order.contact.user
        request.session = {
            "orderID": order.id,
        }

        response = success(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(order.id), response.content.decode("utf-8"))
