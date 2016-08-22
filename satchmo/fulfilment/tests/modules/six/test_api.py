import json
import httmock

from decimal import Decimal
from requests.exceptions import HTTPError

from django.conf import settings
from django.test import TestCase

from satchmo.shop.factories import TestOrderFactory, PaidOrderFactory
from satchmo.shop.models import Order, Product
from satchmo.fulfilment.modules.six.api import (
    float_price,
    order_payload,
    send_order,
)
from satchmo.utils.urlhelper import external_url


class FloatPriceTest(TestCase):
    def test_float_price(self):
        self.assertEqual(15.25, float_price(Decimal("15.25")))

    def test_float_price__zero(self):
        self.assertEqual(0.0, float_price(Decimal("0.00")))

    def test_float_price__none(self):
        self.assertEqual(0.0, float_price(None))


class OrderPayloadTest(TestCase):

    def test_order_payload(self):
        self.maxDiff = None
        order = TestOrderFactory()

        callback_url = external_url("{root}/fulfilment/six/{id}/{hash}/".format(
            root=settings.SATCHMO_SETTINGS['SHOP_BASE'],
            id=order.id,
            hash=order.verification_hash
        ))

        self.assertEqual(json.loads(order_payload(order)), {
            u"api_key": u"",
            u"test": True,
            u"allow_preorder": False,
            u"update_stock": True,

            u"order": {
                u"client_ref": order.id,
                u"po_number": order.id,
                u"date_placed": unicode(order.time_stamp),
                u"callback_url": callback_url,
                u"postage_speed": 2,
                u"postage_cost": float_price(order.shipping_cost),
                u"total_amount": float_price(order.sub_total),
                u"signed_for": False,
                u"tracked": False,
                u"ShippingContact": {
                    u"dear": order.contact.user.first_name,
                    u"name": order.ship_addressee,
                    u"email": order.contact.user.email,
                    u"phone": order.contact.primary_phone or u"",
                    u"address": order.ship_street1,
                    u"address_contd": order.ship_street2,
                    u"city": order.ship_city,
                    u"county": order.ship_state,
                    u"country": unicode(order.ship_country),
                    u"postcode": order.ship_postal_code,
                },
                u"BillingContact": {
                    u"name": order.bill_addressee,
                    u"email": order.contact.user.email,
                    u"phone": order.contact.primary_phone or u"",
                    u"address": order.bill_street1,
                    u"address_contd": order.bill_street2,
                    u"city": order.bill_city,
                    u"county": order.bill_state,
                    u"country": unicode(order.bill_country),
                    u"postcode": order.bill_postal_code,
                },
                u"items": [
                    {
                        u"client_ref": order.orderitem_set.all()[0].product.slug,
                        u"quantity": order.orderitem_set.all()[0].quantity,
                        u"price": float_price(order.orderitem_set.all()[0].unit_price),
                    }
                ]
            }
        })


class SendOrderTest(TestCase):
    def test_has_outstanding_balance(self):
        order = TestOrderFactory()
        self.assertFalse(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertFalse(order.fulfilled)

    def test_request_exception(self):
        @httmock.all_requests
        def response(url, request):
            raise HTTPError

        order = PaidOrderFactory()
        with httmock.HTTMock(response):
            self.assertFalse(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertFalse(order.fulfilled)

    def test_invalid_json(self):
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = "{sf"
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory()
        with httmock.HTTMock(response):
            self.assertFalse(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertFalse(order.fulfilled)

    def test_wrong_order_id(self):
        # Neither should be processed
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = {"order_ref": other_order.id}
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory()
        other_order = PaidOrderFactory()
        with httmock.HTTMock(response):
            self.assertFalse(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertFalse(order.fulfilled)
        other_order = Order.objects.get(id=other_order.id)
        self.assertFalse(other_order.fulfilled)

    def test_empty_order_notes(self):
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = {
                "order_ref": order.id,
                "success": True,
            }
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory()
        with httmock.HTTMock(response):
            self.assertTrue(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.fulfilled)
        self.assertEqual(order.notes, "")

    def test_existing_order_notes(self):
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = {
                "order_ref": order.id,
                "success": True,
            }
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory(notes="Test Notes")
        with httmock.HTTMock(response):
            self.assertTrue(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.fulfilled)
        self.assertTrue(order.notes.startswith("Test Notes\n\n------------------"))

    def test_client_area_link(self):
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = {
                "order_ref": order.id,
                "success": True,
                "client_area_link": "http://example.com/"
            }
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory(notes="Test Notes")
        with httmock.HTTMock(response):
            self.assertTrue(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.fulfilled)
        self.assertIn("Client area: http://example.com/\n", order.notes)

    def test_success(self):
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = {
                "order_ref": order.id,
                "success": True,
                "client_area_link": "http://example.com/"
            }
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory(notes="Test Notes")
        with httmock.HTTMock(response):
            self.assertTrue(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.fulfilled)
        self.assertIsNotNone(order.notes)
        self.assertEqual(order.status.status.status, "Pick & Pack")

    def test_failure(self):
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = {
                "order_ref": order.id,
                "success": False,
                "client_area_link": "http://example.com/",
                "error": "Test Error",
                "valid": True,
            }
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory(notes="Test Notes")
        with httmock.HTTMock(response):
            self.assertTrue(send_order(order))

        order = Order.objects.get(id=order.id)
        self.assertFalse(order.fulfilled)
        self.assertIn("Test Error\n", order.notes)
        self.assertIn("Valid: True\n", order.notes)
        self.assertEqual(order.status.status.status, "Error")

    def test_update_stock(self):
        @httmock.all_requests
        def response(url, request):
            headers = {'content-type': 'application/json'}
            content = {
                "order_ref": order.id,
                "success": True,
                "client_area_link": "http://example.com/",
                "update_stock": True,
                "stock_changes": {
                    product.slug: 5,
                    "does-not-exist": 0,
                }
            }
            return httmock.response(200, content, headers, request=request)

        order = PaidOrderFactory(notes="Test Notes")
        product = order.orderitem_set.all()[0].product
        with httmock.HTTMock(response):
            self.assertTrue(send_order(order))

        # Reload product
        product = Product.objects.get(slug=product.slug)
        self.assertEqual(product.items_in_stock, 5)
