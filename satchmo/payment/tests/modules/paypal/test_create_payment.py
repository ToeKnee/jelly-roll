import json
from unittest import mock

from django.http import Http404
from django.test import TestCase, RequestFactory

from satchmo.payment.modules.paypal.views import create_payment
from satchmo.shop.factories import TestOrderFactory


class CreatePaymentTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_order_unavailable(self):
        request = self.factory.get("/shop/checkout/paypal/create-payment/")
        request.session = {}

        with self.assertRaises(Http404):
            create_payment(request)

    @mock.patch("satchmo.payment.modules.paypal.views.paypalrestsdk.Payment")
    def test_order_available(self, mock_paypal):
        m = mock.MagicMock()
        data = {
            "id": "8RU61172JS455403V",
            "gross_total_amount": {"value": "1.44", "currency": "USD"},
            "purchase_units": [
                {
                    "reference_id": "store_mobile_world_order_1234",
                    "description": "Mobile World Store order-1234",
                    "amount": {
                        "currency": "USD",
                        "details": {
                            "subtotal": "1.09",
                            "shipping": "0.02",
                            "tax": "0.33",
                        },
                        "total": "1.44",
                    },
                    "payee": {"email": "seller@example.com"},
                    "items": [
                        {
                            "name": "NeoPhone",
                            "sku": "sku03",
                            "price": "0.54",
                            "currency": "USD",
                            "quantity": "1",
                        },
                        {
                            "name": "Fitness Watch",
                            "sku": "sku04",
                            "price": "0.55",
                            "currency": "USD",
                            "quantity": "1",
                        },
                    ],
                    "shipping_address": {
                        "recipient_name": "John Doe",
                        "default_address": False,
                        "preferred_address": False,
                        "primary_address": False,
                        "disable_for_transaction": False,
                        "line1": "2211 N First Street",
                        "line2": "Building 17",
                        "city": "San Jose",
                        "country_code": "US",
                        "postal_code": "95131",
                        "state": "CA",
                        "phone": "(123) 456-7890",
                    },
                    "shipping_method": "United Postal Service",
                    "partner_fee_details": {
                        "receiver": {"email": "partner@example.com"},
                        "amount": {"value": "0.01", "currency": "USD"},
                    },
                    "payment_linked_group": 1,
                    "custom": "custom_value_2388",
                    "invoice_number": "invoice_number_2388",
                    "payment_descriptor": "Payment Mobile World",
                    "status": "CAPTURED",
                }
            ],
            "redirect_urls": {
                "return_url": "https://example.com/return",
                "cancel_url": "https://example.com/cancel",
            },
            "create_time": "2017-04-26T21:18:49Z",
            "links": [
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "self",
                    "method": "GET",
                },
                {
                    "href": "https://www.paypal.com/webapps/hermes?token=8RU61172JS455403V",
                    "rel": "approval_url",
                    "method": "GET",
                },
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "cancel",
                    "method": "DELETE",
                },
            ],
            "status": "CREATED",
        }
        m.__getitem__.return_value = data["id"]
        m.to_dict = lambda: data
        m.status_code = 200
        mock_paypal.return_value = m

        order = TestOrderFactory()

        request = self.factory.post("/shop/checkout/paypal/create-payment/")
        request.user = order.contact.user
        request.session = {"orderID": order.id}

        response = create_payment(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content.decode("utf-8"))["id"], data["id"])

        order.refresh_from_db()
        self.assertTrue(order.frozen)
        self.assertEqual(order.payments.all().count(), 1)
        self.assertEqual(order.payments.all()[0].transaction_id, data["id"])

    @mock.patch("satchmo.payment.modules.paypal.views.paypalrestsdk.Payment")
    def test_order_available__api_error(self, mock_paypal):
        m = mock.MagicMock()
        data = {"name": "VALIDATION_ERROR", "details": [{"some": "error"}]}
        m.__getitem__.return_value = data
        m.to_dict = lambda: data
        m.status_code = 400
        m.create = lambda: False
        m.errors = data
        mock_paypal.return_value = m
        order = TestOrderFactory()

        request = self.factory.post("/shop/checkout/paypal/create-payment/")
        request.user = order.contact.user
        request.session = {"orderID": order.id}

        response = create_payment(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b'{"message": "Something went wrong with your PayPal payment.\\n\\nPlease try again.\\n\\nIf the problem persists, please contact us."}',
        )
