from decimal import Decimal

from django.test import TestCase

from satchmo.caching import cache_delete
from satchmo.configuration import config_value
from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import (
    Order,
    OrderPayment,
)


class OrderTest(TestCase):
    def tearDown(self):
        cache_delete()

    def testBalanceMethods(self):
        order = TestOrderFactory()
        order.recalculate_total(save=False)
        price = order.total
        subtotal = order.sub_total

        self.assertEqual(subtotal, Decimal('25.00'))
        self.assertEqual(price, Decimal('35.00'))
        self.assertEqual(order.balance, price)

        paytype = config_value('PAYMENT', 'MODULES')[0]
        pmt = OrderPayment(order=order, payment=paytype, amount=Decimal("5.00"))
        pmt.save()

        self.assertEqual(order.balance, Decimal("30.00"))
        self.assertEqual(order.balance_paid, Decimal("5.00"))

        self.assertTrue(order.is_partially_paid)

        pmt = OrderPayment(order=order, payment=paytype, amount=Decimal("30.00"))
        pmt.save()

        self.assertEqual(order.balance, Decimal("0.00"))
        self.assertFalse(order.is_partially_paid)
        self.assertTrue(order.paid_in_full)

    def testSmallPayment(self):
        order = TestOrderFactory()
        order.recalculate_total(save=False)

        paytype = config_value('PAYMENT', 'MODULES')[0]
        pmt = OrderPayment(order=order, payment=paytype, amount=Decimal("0.000001"))
        pmt.save()

        self.assertTrue(order.is_partially_paid)

    def test_verification_hash(self):
        with self.settings(SECRET_KEY="123"):
            order = Order(id=1, contact_id=1)
            self.assertEqual(order.verification_hash, "97f97b0cd887f1b61e6f7e136aa752b1")

    def test_verify_hash__match(self):
        order = Order(id=1, contact_id=1)
        # Pass the orders hash back into itself
        self.assertTrue(order.verify_hash(order.verification_hash))

    def test_verify_hash__no_match(self):
        order = Order(id=1, contact_id=1)
        # Pass the reverse of the orders hash back into itself
        self.assertFalse(order.verify_hash(order.verification_hash[::-1]))
