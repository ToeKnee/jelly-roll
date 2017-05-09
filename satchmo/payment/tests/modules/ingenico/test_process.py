from datetime import date

from django.http import Http404
from django.test import TestCase, RequestFactory

from satchmo.configuration import config_get_group
from satchmo.payment.modules.ingenico.utils import shasign
from satchmo.payment.modules.ingenico.views import process
from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import Order, OrderRefund

payment_module = config_get_group('PAYMENT_INGENICO')


class ProcessTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_GET(self):
        request = self.factory.get('/shop/checkout/ingenico/success/')

        response = process(request)
        # Method Not Allowed
        self.assertEqual(response.status_code, 405)

    def test_invalid_shasign(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": str(order.id),
            "PAYID": "ingenico-1",
            "PM": "CC",
            "SHASIGN": "invalid-shasign",
            "STATUS": "9",
            "TRXDATE": date.today().isoformat(),
        }

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        response = process(request)
        # Payment required
        self.assertEqual(response.status_code, 402)

    def test_order_unavailable(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": "1234567890",  # Made up order number
            "PAYID": "ingenico-1",
            "PM": "CC",
            "STATUS": "9",
            "TRXDATE": date.today().isoformat(),
        }
        data["SHASIGN"] = shasign(data)

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        with self.assertRaises(Http404):
            process(request)

    def test_no_status(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": order.total,
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": order.id,
            "PAYID": "ingenico-1",
            "PM": "CC",
            # No Status - "STATUS": "9",
            "TRXDATE": date.today().isoformat(),
        }
        data["SHASIGN"] = shasign(data)

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        response = process(request)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(id=order.id)
        self.assertIn("Status: Unknown", order.notes)

    def test_status__accepted(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": str(order.id),
            "PAYID": "ingenico-1",
            "PM": "CC",
            "STATUS": "9",
            "TRXDATE": date.today().isoformat(),
        }
        data["SHASIGN"] = shasign(data)

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        response = process(request)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.status.status.status, "Processing")
        self.assertTrue(order.payments.filter(
            amount=order.total,
            payment="INGENICO",
            transaction_id=data["ACCEPTANCE"],
        ).exists())
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, 0)
            self.assertEqual(item.product.total_sold, item.quantity)

        self.assertIn("Status: Payment requested", order.notes)

    def test_status__cancelled(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": str(order.id),
            "PAYID": "ingenico-1",
            "PM": "CC",
            "STATUS": "1",
            "TRXDATE": date.today().isoformat(),
        }
        data["SHASIGN"] = shasign(data)

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        response = process(request)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.status.status.status, "Cancelled")
        self.assertFalse(order.payments.filter(
            amount=order.total,
            payment="INGENICO",
            transaction_id=data["ACCEPTANCE"],
        ).exists())
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, item.quantity)
            self.assertEqual(item.product.total_sold, 0)

        self.assertIn("Status: Cancelled", order.notes)

    def test_status__refused(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": str(order.id),
            "PAYID": "ingenico-1",
            "PM": "CC",
            "STATUS": "2",
            "TRXDATE": date.today().isoformat(),
        }
        data["SHASIGN"] = shasign(data)

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        response = process(request)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.status.status.status, "Authorisation refused")
        self.assertFalse(order.payments.filter(
            amount=order.total,
            payment="INGENICO",
            transaction_id=data["ACCEPTANCE"],
        ).exists())
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, item.quantity)
            self.assertEqual(item.product.total_sold, 0)
        self.assertIn("Status: Authorisation refused", order.notes)

    def test_status__refund(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": str(order.id),
            "PAYID": "ingenico-1",
            "PM": "CC",
            "STATUS": "8",
            "TRXDATE": date.today().isoformat(),
        }
        data["SHASIGN"] = shasign(data)

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        response = process(request)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.refund, order.total)
        self.assertEqual(order.status.status.status, "Refunded")
        self.assertFalse(order.payments.filter(
            amount=order.total,
            payment="INGENICO",
            transaction_id=data["ACCEPTANCE"],
        ).exists())
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, item.quantity)
            self.assertEqual(item.product.total_sold, 0)
        self.assertIn("Status: Refund", order.notes)
        self.assertTrue(OrderRefund.objects.filter(
            order=order,
            amount=order.refund,
            transaction_id="trans-1",
        ).exists())

    def test_status__refund__payment_deleted(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "amount": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": "",
            "orderID": str(order.id),
            "PAYID": "ingenico-1",
            "PM": "CC",
            "STATUS": "7",
            "TRXDATE": date.today().isoformat(),
        }
        data["SHASIGN"] = shasign(data)

        request = self.factory.post('/shop/checkout/ingenico/success/', data)

        response = process(request)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(id=order.id)
        self.assertTrue(order.frozen)
        self.assertEqual(order.refund, order.total)
        self.assertEqual(order.status.status.status, "Refunded")
        self.assertFalse(order.payments.filter(
            amount=order.total,
            payment="INGENICO",
            transaction_id=data["ACCEPTANCE"],
        ).exists())
        for item in order.orderitem_set.all():
            self.assertEqual(item.product.items_in_stock, item.quantity)
            self.assertEqual(item.product.total_sold, 0)
        self.assertIn("Status: Payment deleted", order.notes)
        self.assertTrue(OrderRefund.objects.filter(
            order=order,
            amount=order.refund,
            transaction_id="trans-1",
        ).exists())
