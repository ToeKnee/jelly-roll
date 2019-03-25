from unittest import mock

from django.test import TestCase, RequestFactory

from satchmo.payment.modules.paypal.views import webhook
from satchmo.shop.factories import PaidOrderFactory


class WebhookTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @mock.patch(
        "satchmo.payment.modules.paypal.views.paypalrestsdk.notifications.WebhookEvent.verify"
    )
    def test_customer_dispute(self, mock_paypal):
        "PayPal CUSTOMER.DISPUTE.CREATED A customer dispute is created."
        mock_paypal.return_value = True

        order = PaidOrderFactory()
        data = {
            "id": "WH-4M0448861G563140B-9EX36365822141321",
            "create_time": "2018-06-21T13:36:33.000Z",
            "resource_type": "dispute",
            "event_type": "CUSTOMER.DISPUTE.CREATED",
            "summary": "A new dispute opened with Case # PP-000-042-663-135",
            "resource": {
                "disputed_transactions": [
                    {
                        "seller_transaction_id": order.payments.first().transaction_id,
                        "seller": {
                            "merchant_id": "RD465XN5VS364",
                            "name": "Test Store",
                        },
                        "items": [],
                        "seller_protection_eligible": True,
                    }
                ],
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "dispute_channel": "INTERNAL",
                "update_time": "2018-06-21T13:35:44.000Z",
                "create_time": "2018-06-21T13:35:44.000Z",
                "messages": [
                    {
                        "posted_by": "BUYER",
                        "time_posted": "2018-06-21T13:35:52.000Z",
                        "content": "qwqwqwq",
                    }
                ],
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/customer/disputes/PP-000-042-663-135",
                        "rel": "self",
                        "method": "GET",
                    },
                    {
                        "href": "https://api.paypal.com/v1/customer/disputes/PP-000-042-663-135/send-message",
                        "rel": "send_message",
                        "method": "POST",
                    },
                ],
                "dispute_amount": {"currency_code": "USD", "value": "3.00"},
                "dispute_id": "PP-000-042-663-135",
                "dispute_life_cycle_stage": "INQUIRY",
                "status": "OPEN",
            },
            "links": [
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-4M0448861G563140B-9EX36365822141321",
                    "rel": "self",
                    "method": "GET",
                    "encType": "application/json",
                },
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-4M0448861G563140B-9EX36365822141321/resend",
                    "rel": "resend",
                    "method": "POST",
                    "encType": "application/json",
                },
            ],
            "event_version": "1.0",
        }

        request = self.factory.post(
            "/shop/checkout/paypal/webhook/", data=data, content_type="application/json"
        )
        request.META = {
            "HTTP_PAYPAL_AUTH_ALGO": "test",
            "HTTP_PAYPAL_CERT_URL": "test",
            "HTTP_PAYPAL_TRANSMISSION_ID": "test",
            "HTTP_PAYPAL_TRANSMISSION_SIG": "test",
            "HTTP_PAYPAL_TRANSMISSION_TIME": "test",
        }

        webhook(request)

        order.refresh_from_db()
        self.assertIn("--- Paypal Customer Dispute ---", order.notes)

    @mock.patch(
        "satchmo.payment.modules.paypal.views.paypalrestsdk.notifications.WebhookEvent.verify"
    )
    def test_pay_completed(self, mock_paypal):
        "PayPal PAYMENT.SALE.COMPLETED A sale completes."
        mock_paypal.return_value = True

        order = PaidOrderFactory()
        data = {
            "id": "WH-2WR32451HC0233532-67976317FL4543714",
            "create_time": "2014-10-23T17:23:52Z",
            "resource_type": "sale",
            "event_type": "PAYMENT.SALE.COMPLETED",
            "summary": "A successful sale payment was made for $ 0.48 USD",
            "resource": {
                "parent_payment": order.payments.first().transaction_id,
                "invoice_number": order.id,
                "update_time": "2014-10-23T17:23:04Z",
                "amount": {"total": "0.48", "currency": "USD"},
                "payment_mode": "ECHECK",
                "create_time": "2014-10-23T17:22:56Z",
                "clearing_time": "2014-10-30T07:00:00Z",
                "protection_eligibility_type": "ITEM_NOT_RECEIVED_ELIGIBLE,UNAUTHORIZED_PAYMENT_ELIGIBLE",
                "protection_eligibility": "ELIGIBLE",
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/80021663DE681814L",
                        "rel": "self",
                        "method": "GET",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/80021663DE681814L/refund",
                        "rel": "refund",
                        "method": "POST",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/payment/PAY-1PA12106FU478450MKRETS4A",
                        "rel": "parent_payment",
                        "method": "GET",
                    },
                ],
                "id": "80021663DE681814L",
                "state": "completed",
            },
            "links": [
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-2WR32451HC0233532-67976317FL4543714",
                    "rel": "self",
                    "method": "GET",
                    "encType": "application/json",
                },
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-2WR32451HC0233532-67976317FL4543714/resend",
                    "rel": "resend",
                    "method": "POST",
                    "encType": "application/json",
                },
            ],
            "event_version": "1.0",
        }
        request = self.factory.post(
            "/shop/checkout/paypal/webhook/", data=data, content_type="application/json"
        )
        request.META = {
            "HTTP_PAYPAL_AUTH_ALGO": "test",
            "HTTP_PAYPAL_CERT_URL": "test",
            "HTTP_PAYPAL_TRANSMISSION_ID": "test",
            "HTTP_PAYPAL_TRANSMISSION_SIG": "test",
            "HTTP_PAYPAL_TRANSMISSION_TIME": "test",
        }

        webhook(request)

        order.refresh_from_db()
        self.assertIn("--- Paypal Payment Complete ---", order.notes)
        self.assertEqual(float(order.payments.last().amount), 0.48)
        self.assertEqual(order.status.status.status, "Processing")

    @mock.patch(
        "satchmo.payment.modules.paypal.views.paypalrestsdk.notifications.WebhookEvent.verify"
    )
    def test_denied(self, mock_paypal):
        "PayPal PAYMENT.SALE.DENIED The state of a sale changes from pending to denied."
        mock_paypal.return_value = True

        order = PaidOrderFactory()
        data = {
            "id": "WH-4YP718828D2768154-96229356YL4818534",
            "create_time": "2015-10-07T16:45:17Z",
            "resource_type": "sale",
            "event_type": "PAYMENT.SALE.DENIED",
            "summary": "A EUR 17.47 EUR sale payment was denied",
            "resource": {
                "parent_payment": order.payments.first().transaction_id,
                "update_time": "2015-10-07T16:43:35Z",
                "amount": {"total": "17.47", "currency": "EUR"},
                "payment_mode": "INSTANT_TRANSFER",
                "create_time": "2015-10-07T16:43:35Z",
                "protection_eligibility": "INELIGIBLE",
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/0UV619993K905211J",
                        "rel": "self",
                        "method": "GET",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/0UV619993K905211J/refund",
                        "rel": "refund",
                        "method": "POST",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/payment/PAY-9SM48294F4717633YKYKUXNQ",
                        "rel": "parent_payment",
                        "method": "GET",
                    },
                ],
                "id": "0UV619993K905211J",
                "state": "denied",
            },
            "links": [
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-4YP718828D2768154-96229356YL4818534",
                    "rel": "self",
                    "method": "GET",
                    "encType": "application/json",
                },
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-4YP718828D2768154-96229356YL4818534/resend",
                    "rel": "resend",
                    "method": "POST",
                    "encType": "application/json",
                },
            ],
            "event_version": "1.0",
        }
        request = self.factory.post(
            "/shop/checkout/paypal/webhook/", data=data, content_type="application/json"
        )
        request.META = {
            "HTTP_PAYPAL_AUTH_ALGO": "test",
            "HTTP_PAYPAL_CERT_URL": "test",
            "HTTP_PAYPAL_TRANSMISSION_ID": "test",
            "HTTP_PAYPAL_TRANSMISSION_SIG": "test",
            "HTTP_PAYPAL_TRANSMISSION_TIME": "test",
        }

        webhook(request)

        order.refresh_from_db()
        self.assertIn("--- Paypal Payment Denied ---", order.notes)

    @mock.patch(
        "satchmo.payment.modules.paypal.views.paypalrestsdk.notifications.WebhookEvent.verify"
    )
    def test_pending(self, mock_paypal):
        "PayPal PAYMENT.SALE.PENDING The state of a sale changes to pending."
        mock_paypal.return_value = True

        order = PaidOrderFactory()
        data = {
            "id": "WH-6W4482673W002281V-61985753LP2332451",
            "create_time": "2015-05-11T21:45:15Z",
            "resource_type": "sale",
            "event_type": "PAYMENT.SALE.PENDING",
            "summary": "Payment pending for EUR 3.76 EUR",
            "resource": {
                "reason_code": "RECEIVING_PREFERENCE_MANDATES_MANUAL_ACTION",
                "parent_payment": order.payments.first().transaction_id,
                "update_time": "2015-05-11T21:44:29Z",
                "amount": {"total": "3.76", "currency": "EUR"},
                "payment_mode": "INSTANT_TRANSFER",
                "create_time": "2015-05-11T21:44:29Z",
                "protection_eligibility": "INELIGIBLE",
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/11139561TK568332L",
                        "rel": "self",
                        "method": "GET",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/11139561TK568332L/refund",
                        "rel": "refund",
                        "method": "POST",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/payment/PAY-13V79659LS5126423KVISFPI",
                        "rel": "parent_payment",
                        "method": "GET",
                    },
                ],
                "id": "11139561TK568332L",
                "state": "pending",
            },
            "links": [
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-6W4482673W002281V-61985753LP2332451",
                    "rel": "self",
                    "method": "GET",
                    "encType": "application/json",
                },
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-6W4482673W002281V-61985753LP2332451/resend",
                    "rel": "resend",
                    "method": "POST",
                    "encType": "application/json",
                },
            ],
            "event_version": "1.0",
        }
        request = self.factory.post(
            "/shop/checkout/paypal/webhook/", data=data, content_type="application/json"
        )
        request.META = {
            "HTTP_PAYPAL_AUTH_ALGO": "test",
            "HTTP_PAYPAL_CERT_URL": "test",
            "HTTP_PAYPAL_TRANSMISSION_ID": "test",
            "HTTP_PAYPAL_TRANSMISSION_SIG": "test",
            "HTTP_PAYPAL_TRANSMISSION_TIME": "test",
        }

        webhook(request)

        order.refresh_from_db()
        self.assertIn("--- Paypal Payment Pending ---", order.notes)
        self.assertEqual(order.status.status.status, "Pending")

    @mock.patch(
        "satchmo.payment.modules.paypal.views.paypalrestsdk.notifications.WebhookEvent.verify"
    )
    def test_refunded(self, mock_paypal):
        "PayPal PAYMENT.SALE.REFUNDED A merchant refunds a sale."
        mock_paypal.return_value = True

        order = PaidOrderFactory()
        data = {
            "id": "WH-2N242548W9943490U-1JU23391CS4765624",
            "create_time": "2014-10-31T15:42:24Z",
            "resource_type": "sale",
            "event_type": "PAYMENT.SALE.REFUNDED",
            "summary": "A 0.01 USD sale payment was refunded",
            "resource": {
                "sale_id": "9T0916710M1105906",
                "parent_payment": order.payments.first().transaction_id,
                "invoice_number": order.id,
                "update_time": "2014-10-31T15:41:51Z",
                "amount": {"total": "-0.01", "currency": "USD"},
                "create_time": "2014-10-31T15:41:51Z",
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/payments/refund/6YX43824R4443062K",
                        "rel": "self",
                        "method": "GET",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/payment/PAY-5437236047802405NKRJ22UA",
                        "rel": "parent_payment",
                        "method": "GET",
                    },
                    {
                        "href": "https://api.paypal.com/v1/payments/sale/9T0916710M1105906",
                        "rel": "sale",
                        "method": "GET",
                    },
                ],
                "id": "6YX43824R4443062K",
                "state": "completed",
            },
            "links": [
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-2N242548W9943490U-1JU23391CS4765624",
                    "rel": "self",
                    "method": "GET",
                    "encType": "application/json",
                },
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-2N242548W9943490U-1JU23391CS4765624/resend",
                    "rel": "resend",
                    "method": "POST",
                    "encType": "application/json",
                },
            ],
            "event_version": "1.0",
        }
        request = self.factory.post(
            "/shop/checkout/paypal/webhook/", data=data, content_type="application/json"
        )
        request.META = {
            "HTTP_PAYPAL_AUTH_ALGO": "test",
            "HTTP_PAYPAL_CERT_URL": "test",
            "HTTP_PAYPAL_TRANSMISSION_ID": "test",
            "HTTP_PAYPAL_TRANSMISSION_SIG": "test",
            "HTTP_PAYPAL_TRANSMISSION_TIME": "test",
        }

        webhook(request)

        order.refresh_from_db()
        self.assertIn("--- Paypal Payment Refunded ---", order.notes)
        self.assertEqual(float(order.refunds.last().amount), -0.01)
        self.assertEqual(order.status.status.status, "Refunded")

    @mock.patch(
        "satchmo.payment.modules.paypal.views.paypalrestsdk.notifications.WebhookEvent.verify"
    )
    def test_reversed(self, mock_paypal):
        "PayPal PAYMENT.SALE.REVERSED PayPal reverses a sale."
        mock_paypal.return_value = True

        order = PaidOrderFactory()
        data = {
            "id": "WH-3EC545679X386831C-3D038940937933201",
            "create_time": "2014-10-23T00:19:27Z",
            "resource_type": "sale",
            "event_type": "PAYMENT.SALE.REVERSED",
            "summary": "A $ 0.49 USD sale payment was reversed",
            "resource": {
                "amount": {
                    "total": "-0.49",
                    "currency": "USD",
                    "details": {"subtotal": "-0.64", "tax": "0.08", "shipping": "0.07"},
                },
                "create_time": "2014-10-23T00:19:12Z",
                "links": [
                    {
                        "href": "https://api.paypal.com/v1/payments/refund/77689802DL785834G",
                        "rel": "self",
                        "method": "GET",
                    }
                ],
                "id": order.payments.first().transaction_id,
                "state": "completed",
            },
            "links": [
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-3EC545679X386831C-3D038940937933201",
                    "rel": "self",
                    "method": "GET",
                    "encType": "application/json",
                },
                {
                    "href": "https://api.paypal.com/v1/notifications/webhooks-events/WH-3EC545679X386831C-3D038940937933201/resend",
                    "rel": "resend",
                    "method": "POST",
                    "encType": "application/json",
                },
            ],
            "event_version": "1.0",
        }
        request = self.factory.post(
            "/shop/checkout/paypal/webhook/", data=data, content_type="application/json"
        )
        request.META = {
            "HTTP_PAYPAL_AUTH_ALGO": "test",
            "HTTP_PAYPAL_CERT_URL": "test",
            "HTTP_PAYPAL_TRANSMISSION_ID": "test",
            "HTTP_PAYPAL_TRANSMISSION_SIG": "test",
            "HTTP_PAYPAL_TRANSMISSION_TIME": "test",
        }

        webhook(request)

        order.refresh_from_db()
        self.assertIn("--- Paypal Payment Reversed ---", order.notes)
        self.assertEqual(float(order.payments.last().amount), -0.49)
        self.assertEqual(order.status.status.status, "Reversed")
