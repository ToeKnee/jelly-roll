from decimal import Decimal

from django.test import TestCase

from satchmo.currency.factories import EURCurrencyFactory, USDCurrencyFactory
from satchmo.currency.models import ExchangeRate
from satchmo.shop.factories import OrderRefundFactory, TestOrderFactory
from satchmo.shop.models import OrderRefund


class UnicodeTest(TestCase):
    def test_unsaved(self):
        refund = OrderRefund()
        self.assertEqual(str(refund), "Order refund (unsaved)")

    def test_saved(self):
        refund = OrderRefundFactory()
        self.assertEqual(
            str(refund),
            "Order refund #{id} - {amount}".format(
                id=refund.id, amount=refund.display_amount
            ),
        )


class SaveTest(TestCase):
    def test_set_exchange_rate__primary_currency(self):
        refund = OrderRefundFactory()
        self.assertEqual(refund.exchange_rate, Decimal("1.0000"))

    def test_set_exchange_rate__alternative_currency(self):
        primary_currency = USDCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = EURCurrencyFactory()
        ExchangeRate.objects.create(currency=alternative_currency, rate="0.1234")

        order = TestOrderFactory(currency=alternative_currency)
        refund = OrderRefundFactory(order=order)
        self.assertEqual(refund.exchange_rate, Decimal("0.1234"))

    def test_set_order_refund_amount(self):
        refund = OrderRefundFactory()
        self.assertEqual(refund.order.refund, refund.amount)

    def test_update_order_defund_amount(self):
        order = TestOrderFactory(refund=Decimal("5.00"))
        refund = OrderRefundFactory(order=order)
        self.assertEqual(refund.order.refund, Decimal("22.50"))


class CurrenctTest(TestCase):
    def test_returns_order_currency(self):
        refund = OrderRefundFactory(amount=Decimal("0.00"))
        self.assertEqual(refund.currency, refund.order.currency)


class DisplayAmountTest(TestCase):
    def test_returns_amount_formatted_correctly(self):
        refund = OrderRefundFactory()
        self.assertEqual(refund.display_amount, "€17.50 (EUR)")


class AmountInPrimaryCurrencyTest(TestCase):
    def test_amount_is_zero(self):
        refund = OrderRefundFactory(amount=Decimal("0.00"))
        self.assertEqual(refund.amount_in_primary_currency(), Decimal("0.00"))

    def test_in_primary_currency(self):
        refund = OrderRefundFactory()
        self.assertEqual(refund.amount_in_primary_currency(), Decimal("17.50"))

    def test_in_alternative_currency(self):
        primary_currency = USDCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = EURCurrencyFactory()
        order = TestOrderFactory(currency=alternative_currency)
        refund = OrderRefundFactory(order=order, exchange_rate=Decimal("1.5555"))

        self.assertEqual(refund.amount_in_primary_currency(), Decimal("11.25"))
