import json
from unittest import mock

from django.http import Http404
from django.test import TestCase, RequestFactory
from django.urls import reverse

from satchmo.configuration.functions import config_get_group
from satchmo.payment.modules.paypal.views import execute_payment
from satchmo.payment.utils import create_pending_payment
from satchmo.shop.factories import TestOrderFactory


class ExecutePaymentTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_order_unavailable(self):
        request = self.factory.get('/shop/checkout/paypal/execute-payment/')
        request.session = {}

        with self.assertRaises(Http404):
            execute_payment(request)

    @mock.patch('satchmo.payment.modules.paypal.views.get_access_token')
    @mock.patch('satchmo.payment.modules.paypal.views.requests.get')
    def test_order_available__approved(self, mock_requests_get, mock_get_access_token):
        mock_requests_get.return_value = mock.MagicMock()
        mock_requests_get.return_value.status_code = 200
        data = {
            "id": "8RU61172JS455403V",
            "gross_total_amount": {
                "value": "1.44",
                "currency": "USD"
            },
            "purchase_units": [
                {
                    "reference_id": "store_mobile_world_order_1234",
                    "description": "Mobile World Store order-1234",
                    "amount": {
                        "currency": "USD",
                        "details": {
                            "subtotal": "1.09",
                            "shipping": "0.02",
                            "tax": "0.33"
                        },
                        "total": "1.44"
                    },
                    "payee": {
                        "email": "seller@example.com"
                    },
                    "items": [
                        {
                            "name": "NeoPhone",
                            "sku": "sku03",
                            "price": "0.54",
                            "currency": "USD",
                            "quantity": "1"
                        },
                        {
                            "name": "Fitness Watch",
                            "sku": "sku04",
                            "price": "0.55",
                            "currency": "USD",
                            "quantity": "1"
                        }
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
                        "phone": "(123) 456-7890"
                    },
                    "shipping_method": "United Postal Service",
                    "partner_fee_details": {
                        "receiver": {
                            "email": "partner@example.com"
                        },
                        "amount": {
                            "value": "0.01",
                            "currency": "USD"
                        }
                    },
                    "payment_linked_group": 1,
                    "custom": "custom_value_2388",
                    "invoice_number": "invoice_number_2388",
                    "payment_descriptor": "Payment Mobile World",
                    "status": "CAPTURED"
                }
            ],
            "redirect_urls": {
                "return_url": "https://example.com/return",
                "cancel_url": "https://example.com/cancel"
            },
            "create_time": "2017-04-26T21:18:49Z",
            "links": [
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "self",
                    "method": "GET"
                },
                {
                    "href": "https://www.paypal.com/webapps/hermes?token=8RU61172JS455403V",
                    "rel": "approval_url",
                    "method": "GET"
                },
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "cancel",
                    "method": "DELETE"
                }
            ],
            "status": "APPROVED"
        }

        mock_requests_get.return_value.json = lambda: data
        mock_get_access_token.return_value = "test-access-token"
        payment_module = config_get_group('PAYMENT_PAYPAL')
        order = TestOrderFactory()
        order_payment = create_pending_payment(order, payment_module)
        order_payment.transaction_id = data['id']
        order_payment.save()

        request = self.factory.post(
            '/shop/checkout/paypal/execute-payment/',
            {'orderID': data['id']}
        )
        request.session = {
            "orderID": order.id,
        }

        response = execute_payment(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            json.loads(response.content),
            {
                'status': 'success',
                'url': reverse('paypal:satchmo_checkout-success')
            }
        )

        order.refresh_from_db()
        self.assertTrue(order.frozen)

        self.assertEqual(order.payments.all().count(), 1)
        self.assertEqual(
            order.payments.all()[0].transaction_id,
            data['id']
        )

        self.assertEqual(order.status.status.status, "Accepted")
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, 0)
            self.assertEqual(item.product.total_sold, item.quantity)

    @mock.patch('satchmo.payment.modules.paypal.views.get_access_token')
    @mock.patch('satchmo.payment.modules.paypal.views.requests.get')
    def test_order_available__created(self, mock_requests_get, mock_get_access_token):
        mock_requests_get.return_value = mock.MagicMock()
        mock_requests_get.return_value.status_code = 200
        data = {
            "id": "8RU61172JS455403V",
            "gross_total_amount": {
                "value": "1.44",
                "currency": "USD"
            },
            "purchase_units": [
                {
                    "reference_id": "store_mobile_world_order_1234",
                    "description": "Mobile World Store order-1234",
                    "amount": {
                        "currency": "USD",
                        "details": {
                            "subtotal": "1.09",
                            "shipping": "0.02",
                            "tax": "0.33"
                        },
                        "total": "1.44"
                    },
                    "payee": {
                        "email": "seller@example.com"
                    },
                    "items": [
                        {
                            "name": "NeoPhone",
                            "sku": "sku03",
                            "price": "0.54",
                            "currency": "USD",
                            "quantity": "1"
                        },
                        {
                            "name": "Fitness Watch",
                            "sku": "sku04",
                            "price": "0.55",
                            "currency": "USD",
                            "quantity": "1"
                        }
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
                        "phone": "(123) 456-7890"
                    },
                    "shipping_method": "United Postal Service",
                    "partner_fee_details": {
                        "receiver": {
                            "email": "partner@example.com"
                        },
                        "amount": {
                            "value": "0.01",
                            "currency": "USD"
                        }
                    },
                    "payment_linked_group": 1,
                    "custom": "custom_value_2388",
                    "invoice_number": "invoice_number_2388",
                    "payment_descriptor": "Payment Mobile World",
                    "status": "CAPTURED"
                }
            ],
            "redirect_urls": {
                "return_url": "https://example.com/return",
                "cancel_url": "https://example.com/cancel"
            },
            "create_time": "2017-04-26T21:18:49Z",
            "links": [
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "self",
                    "method": "GET"
                },
                {
                    "href": "https://www.paypal.com/webapps/hermes?token=8RU61172JS455403V",
                    "rel": "approval_url",
                    "method": "GET"
                },
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "cancel",
                    "method": "DELETE"
                }
            ],
            "status": "CREATED"
        }

        mock_requests_get.return_value.json = lambda: data
        mock_get_access_token.return_value = "test-access-token"
        payment_module = config_get_group('PAYMENT_PAYPAL')
        order = TestOrderFactory()
        order_payment = create_pending_payment(order, payment_module)
        order_payment.transaction_id = data['id']
        order_payment.save()

        request = self.factory.post(
            '/shop/checkout/paypal/execute-payment/',
            {'orderID': data['id']}
        )
        request.session = {
            "orderID": order.id,
        }

        response = execute_payment(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            json.loads(response.content),
            {
                'status': 'success',
                'url': reverse('paypal:satchmo_checkout-success')
            }
        )

        order.refresh_from_db()
        self.assertTrue(order.frozen)

        self.assertEqual(order.payments.all().count(), 1)
        self.assertEqual(
            order.payments.all()[0].transaction_id,
            data['id']
        )

        self.assertEqual(order.status.status.status, "Accepted")
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, 0)
            self.assertEqual(item.product.total_sold, item.quantity)

    @mock.patch('satchmo.payment.modules.paypal.views.get_access_token')
    @mock.patch('satchmo.payment.modules.paypal.views.requests.get')
    def test_order_available__processed(self, mock_requests_get, mock_get_access_token):
        mock_requests_get.return_value = mock.MagicMock()
        mock_requests_get.return_value.status_code = 200
        data = {
            "id": "8RU61172JS455403V",
            "gross_total_amount": {
                "value": "1.44",
                "currency": "USD"
            },
            "purchase_units": [
                {
                    "reference_id": "store_mobile_world_order_1234",
                    "description": "Mobile World Store order-1234",
                    "amount": {
                        "currency": "USD",
                        "details": {
                            "subtotal": "1.09",
                            "shipping": "0.02",
                            "tax": "0.33"
                        },
                        "total": "1.44"
                    },
                    "payee": {
                        "email": "seller@example.com"
                    },
                    "items": [
                        {
                            "name": "NeoPhone",
                            "sku": "sku03",
                            "price": "0.54",
                            "currency": "USD",
                            "quantity": "1"
                        },
                        {
                            "name": "Fitness Watch",
                            "sku": "sku04",
                            "price": "0.55",
                            "currency": "USD",
                            "quantity": "1"
                        }
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
                        "phone": "(123) 456-7890"
                    },
                    "shipping_method": "United Postal Service",
                    "partner_fee_details": {
                        "receiver": {
                            "email": "partner@example.com"
                        },
                        "amount": {
                            "value": "0.01",
                            "currency": "USD"
                        }
                    },
                    "payment_linked_group": 1,
                    "custom": "custom_value_2388",
                    "invoice_number": "invoice_number_2388",
                    "payment_descriptor": "Payment Mobile World",
                    "status": "CAPTURED"
                }
            ],
            "redirect_urls": {
                "return_url": "https://example.com/return",
                "cancel_url": "https://example.com/cancel"
            },
            "execute_time": "2017-04-26T21:18:49Z",
            "links": [
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "self",
                    "method": "GET"
                },
                {
                    "href": "https://www.paypal.com/webapps/hermes?token=8RU61172JS455403V",
                    "rel": "approval_url",
                    "method": "GET"
                },
                {
                    "href": "https://api.paypal.com/v1/checkout/orders/8RU61172JS455403V",
                    "rel": "cancel",
                    "method": "DELETE"
                }
            ],
            "status": "COMPLETED"
        }
        mock_requests_get.return_value.json = lambda: data
        mock_get_access_token.return_value = "test-access-token"
        payment_module = config_get_group('PAYMENT_PAYPAL')
        order = TestOrderFactory()
        order_payment = create_pending_payment(order, payment_module)
        order_payment.transaction_id = data['id']
        order_payment.save()

        request = self.factory.post(
            '/shop/checkout/paypal/execute-payment/',
            {'orderID': data['id']}
        )
        request.session = {
            "orderID": order.id,
        }

        response = execute_payment(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            json.loads(response.content),
            {
                'status': 'success',
                'url': reverse('paypal:satchmo_checkout-success')
            }
        )

        order.refresh_from_db()
        self.assertTrue(order.frozen)

        self.assertEqual(order.payments.all().count(), 2)
        self.assertEqual(
            order.payments.last().transaction_id,
            data['id']
        )
        self.assertEqual(float(order.payments.last().amount), 1.44)

        self.assertEqual(order.status.status.status, "Processing")
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, 0)
            self.assertEqual(item.product.total_sold, item.quantity)

    @mock.patch('satchmo.payment.modules.paypal.views.get_access_token')
    @mock.patch('satchmo.payment.modules.paypal.views.requests.get')
    def test_order_available__invalid_token(self, mock_requests_get, mock_get_access_token):
        mock_requests_get.return_value = mock.MagicMock()
        mock_requests_get.return_value.status_code = 401
        mock_get_access_token.return_value = "test-access-token"
        order = TestOrderFactory()

        request = self.factory.post('/shop/checkout/paypal/execute-payment/')
        request.session = {
            "orderID": order.id,
        }

        response = execute_payment(request)
        self.assertEqual(response.status_code, 401)

    @mock.patch('satchmo.payment.modules.paypal.views.get_access_token')
    @mock.patch('satchmo.payment.modules.paypal.views.requests.get')
    def test_order_available__api_error(self, mock_requests_get, mock_get_access_token):
        mock_requests_get.return_value = mock.MagicMock()
        mock_requests_get.return_value.status_code = 400
        mock_get_access_token.return_value = "test-access-token"
        order = TestOrderFactory()

        request = self.factory.post('/shop/checkout/paypal/execute-payment/')
        request.session = {
            "orderID": order.id,
        }

        response = execute_payment(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b'{"message": "Something went wrong with your PayPal payment.\\n\\nPlease try again.\\n\\nIf the problem persists, please contact us."}'
        )
