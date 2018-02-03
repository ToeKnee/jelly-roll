from decimal import Decimal

from django.test import TestCase

from satchmo.currency.factories import USDCurrencyFactory
from satchmo.shop.factories import (
    OrderItemFactory,
    TestOrderFactory,
)


class CurrencyCode(TestCase):
    def test_currency_code(self):
        currency = USDCurrencyFactory()
        order = TestOrderFactory(currency=currency)
        order_item = OrderItemFactory(order=order)
        self.assertEqual(order_item.currency_code, currency.iso_4217_code)


class DisplayMethodsTest(TestCase):
    def setUp(self):
        self.currency = USDCurrencyFactory()
        self.order = TestOrderFactory(currency=self.currency)
        self.order_item = OrderItemFactory(order=self.order)

    def test_unit_price(self):
        self.assertEqual(self.order_item.display_unit_price, u'$5.00 (USD)')

    def test_unit_price_with_tax(self):
        self.assertEqual(self.order_item.display_unit_price_with_tax, u'$5.00 (USD)')

    def test_discount(self):
        self.order_item.discount = Decimal("3.00")
        self.assertEqual(self.order_item.display_discount, u'$3.00 (USD)')

    def test_sub_total(self):
        self.assertEqual(self.order_item.display_sub_total, u'$25.00 (USD)')

    def test_total_with_tax(self):
        self.assertEqual(self.order_item.display_total_with_tax, u'$25.00 (USD)')
