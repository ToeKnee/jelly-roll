from django.conf import settings
from django.test import TestCase, RequestFactory

from satchmo.currency.factories import EURCurrencyFactory
from satchmo.payment.modules.ingenico.views import pay_ship_info
from satchmo.shop.factories import CartFactory


class PayShipInfoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        EURCurrencyFactory(primary=True)

    def test_has_enough_stock(self):
        cart = CartFactory()
        # Make sure the items are in stock
        for item in cart.cartitem_set.all():
            item.product.items_in_stock = item.quantity
            item.product.save()

        request = self.factory.get('/shop/checkout/ingenico/')
        request.user = cart.customer.user
        request.session = {
            "cart": cart.id,
            "custID": cart.customer.id,
        }

        response = pay_ship_info(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Your cart is empty".encode("utf-8"), response.content)

    def test_not_enough_stock(self):
        cart = CartFactory()

        request = self.factory.get('/shop/checkout/ingenico/')
        request.user = cart.customer.user
        request.session = {
            "cart": cart.id,
            "custID": cart.customer.id,
        }

        response = pay_ship_info(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response._headers['location'],
            ('Location', '{}/cart/'.format(
                getattr(settings, "SHOP_BASE", "/store")
            ))
        )
