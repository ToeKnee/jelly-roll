from unittest import mock

from django.http import Http404
from django.test import TestCase, RequestFactory

from satchmo.payment.modules.paypal.views import execute_payment


class ExecutePaymentTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_order_unavailable(self):
        request = self.factory.get('/shop/checkout/paypal/execute-payment/')
        request.session = {}

        with self.assertRaises(Http404):
            execute_payment(request)

    @mock.patch('satchmo.payment.modules.paypal.views.paypalrestsdk')
    def test_order_available__api_error(self, mock_paypal):
        m = mock.MagicMock()
        m.execute.return_value = False
        mock_paypal.Payment.find.return_value = m
        mock_paypal.return_value.status_code = 400

        request = self.factory.post('/shop/checkout/paypal/execute-payment/', {'paymentID': "test"})

        response = execute_payment(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            b'{"message": "Something went wrong with your PayPal payment.\\n\\nPlease try again.\\n\\nIf the problem persists, please contact us."}'
        )
