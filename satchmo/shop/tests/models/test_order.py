# -*- coding: utf-8 -*-

import datetime
import mock

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from satchmo.currency.factories import (
    EURCurrencyFactory,
    GBPCurrencyFactory,
    USDCurrencyFactory,
)
from satchmo.shop.factories import (
    OrderFactory,
    PaidOrderFactory,
    ShippedOrderFactory,
    StatusFactory,
    TestOrderFactory
)
from satchmo.shop.models import Order, OrderRefund


class OrderManagerTest(TestCase):
    def test_live__unfrozen(self):
        order = OrderFactory(frozen=False)
        self.assertIn(order, Order.objects.live())

    def test_live__frozen(self):
        order = OrderFactory(frozen=True)
        self.assertNotIn(order, Order.objects.live())

    def test_unfulfilled(self):
        order = OrderFactory(
            frozen=True,
            fulfilled=False,
        )
        order.add_status('Processing')
        self.assertIn(order, Order.objects.unfulfilled())

    def test_unfulfilled__fulfilled(self):
        order = OrderFactory(
            frozen=True,
            fulfilled=True,
        )
        order.add_status('Processing')
        self.assertNotIn(order, Order.objects.unfulfilled())

    def test_by_status__no_status(self):
        order = OrderFactory()
        status = StatusFactory()
        self.assertNotIn(order, list(Order.objects.by_latest_status(status.status)))

    def test_by_status__only_status(self):
        order = OrderFactory()
        order.add_status('test')
        self.assertIn(order, Order.objects.by_latest_status('test'))

    def test_by_status__last_status(self):
        order = OrderFactory()
        order.add_status('other')
        order.add_status('test')
        self.assertIn(order, Order.objects.by_latest_status('test'))

    def test_by_status__not_last_status(self):
        order = OrderFactory()
        order.add_status('test')
        order.add_status('other')
        self.assertNotIn(order, Order.objects.by_latest_status('test'))


class OrderShippedTest(TestCase):
    def test_shipped(self):
        order = ShippedOrderFactory()
        self.assertTrue(order.shipped)

    def test_not_shipped(self):
        order = PaidOrderFactory()
        self.assertFalse(order.shipped)


class OrderShippingDateTest(TestCase):

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_not_frozen__business_day__before_midday(self, now):
        now.return_value = timezone.datetime(2016, 7, 25, 11, 58)  # Monday
        order = OrderFactory()
        self.assertEqual(order.shipping_date(), datetime.date(2016, 7, 25))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_not_frozen__business_day__after_midday(self, now):
        now.return_value = timezone.datetime(2016, 7, 25, 14, 14)  # Monday
        order = OrderFactory()
        self.assertEqual(order.shipping_date(), datetime.date(2016, 7, 26))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_not_frozen__weekend(self, now):
        # Don't care about the time of day, it won't ship until the
        # next business day.
        now.return_value = timezone.datetime(2016, 7, 30, 10, 00)  # Saturday
        order = OrderFactory()
        self.assertEqual(order.shipping_date(), datetime.date(2016, 8, 1))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_frozen__shipped(self, now):
        # Orders might be posted on a Saturday, but we don't guarantee it
        now.return_value = timezone.datetime(2016, 7, 30, 12, 15)  # Saturday
        order = PaidOrderFactory()
        order.add_status('Shipped', "Test Order Shipped")
        self.assertEqual(order.shipping_date(), datetime.date(2016, 7, 30))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_frozen__business_day__not_shipped__before_midday(self, now):
        now.return_value = timezone.datetime(2016, 7, 25, 11, 58)  # Monday
        order = PaidOrderFactory()
        self.assertEqual(order.shipping_date(), datetime.date(2016, 7, 25))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_frozen__business_day__not_shipped__after_midday(self, now):
        now.return_value = timezone.datetime(2016, 7, 25, 14, 14)  # Monday
        order = PaidOrderFactory()
        self.assertEqual(order.shipping_date(), datetime.date(2016, 7, 26))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_frozen__weekend__not_shipped(self, now):
        now.return_value = timezone.datetime(2016, 7, 30, 15, 15)  # Saturday
        order = PaidOrderFactory()
        self.assertEqual(order.shipping_date(), datetime.date(2016, 8, 1))


class EstimatedDeliveryMinDateTest(TestCase):

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_monday(self, now):
        now.return_value = timezone.datetime(2016, 7, 25)  # Monday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_min_date(), datetime.date(2016, 7, 26))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_friday(self, now):
        now.return_value = timezone.datetime(2016, 7, 29)  # Friday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_min_date(), datetime.date(2016, 8, 1))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_saturday(self, now):
        now.return_value = timezone.datetime(2016, 7, 30)  # Saturday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_min_date(), datetime.date(2016, 8, 1))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_sunday(self, now):
        # Unlikely to ever be posted on a Sunday, but best to check
        # anyway
        now.return_value = timezone.datetime(2016, 7, 31)  # Sunday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_min_date(), datetime.date(2016, 8, 1))


class EstimatedDeliveryExpectedDateTest(TestCase):

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_monday(self, now):
        now.return_value = timezone.datetime(2016, 7, 25)  # Monday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_expected_date(), datetime.date(2016, 8, 4))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_friday(self, now):
        now.return_value = timezone.datetime(2016, 7, 29)  # Friday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_expected_date(), datetime.date(2016, 8, 10))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_saturday(self, now):
        now.return_value = timezone.datetime(2016, 7, 30)  # Saturday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_expected_date(), datetime.date(2016, 8, 10))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_sunday(self, now):
        # Unlikely to ever be posted on a Sunday, but best to check
        # anyway
        now.return_value = timezone.datetime(2016, 7, 31)  # Sunday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_expected_date(), datetime.date(2016, 8, 10))


class EstimatedDeliveryMaxDateTest(TestCase):

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_monday(self, now):
        now.return_value = timezone.datetime(2016, 7, 25)  # Monday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_max_date(), datetime.date(2016, 8, 30))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_friday(self, now):
        now.return_value = timezone.datetime(2016, 7, 29)  # Friday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_max_date(), datetime.date(2016, 9, 5))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_saturday(self, now):
        now.return_value = timezone.datetime(2016, 7, 30)  # Saturday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_max_date(), datetime.date(2016, 9, 5))

    @mock.patch("satchmo.shop.models.timezone.now")
    def test_posted_on_sunday(self, now):
        # Unlikely to ever be posted on a Sunday, but best to check
        # anyway
        now.return_value = timezone.datetime(2016, 7, 31)  # Sunday
        order = ShippedOrderFactory()
        self.assertEqual(order.estimated_delivery_max_date(), datetime.date(2016, 9, 5))


class AddStatusTest(TestCase):
    @mock.patch("satchmo.shop.models.send_order_update")
    def test_sends_notification(self, mock_send_order_update):
        order = OrderFactory()
        status = StatusFactory(notify=True)
        order_status = order.add_status(status.status, "Test Order Shipped")
        self.assertEqual(len(mock_send_order_update.call_args_list), 1)
        self.assertEqual(
            mock_send_order_update.call_args_list,
            [mock.call(order_status)]
        )


class SubTotalInPrimaryCurrencyTest(TestCase):
    def test_in_primary_currency(self):
        primary_currency = EURCurrencyFactory(primary=True)
        order = TestOrderFactory(currency=primary_currency)
        self.assertEqual(order.sub_total_in_primary_currency(), Decimal("25.00"))

    def test_in_alternative_currency__more(self):
        primary_currency = EURCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = USDCurrencyFactory()

        order = TestOrderFactory(currency=alternative_currency, exchange_rate=Decimal("1.06649"))
        self.assertEqual(order.sub_total_in_primary_currency().quantize(
            Decimal('.01')), Decimal("23.44"))

    def test_in_alternative_currency__less(self):
        primary_currency = USDCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = EURCurrencyFactory()

        order = TestOrderFactory(currency=alternative_currency, exchange_rate=Decimal("0.937658"))
        self.assertEqual(order.sub_total_in_primary_currency().quantize(
            Decimal('.01')), Decimal("26.66"))


class ShippingCostInPrimaryCurrencyTest(TestCase):
    def test_in_primary_currency(self):
        primary_currency = EURCurrencyFactory(primary=True)
        order = TestOrderFactory(currency=primary_currency)
        self.assertEqual(order.shipping_cost_in_primary_currency(), Decimal("10.00"))

    def test_in_alternative_currency__more(self):
        primary_currency = EURCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = USDCurrencyFactory()

        order = TestOrderFactory(currency=alternative_currency, exchange_rate=Decimal("1.06649"))
        self.assertEqual(order.shipping_cost_in_primary_currency().quantize(
            Decimal('.01')), Decimal("9.38"))

    def test_in_alternative_currency__less(self):
        primary_currency = USDCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = EURCurrencyFactory()

        order = TestOrderFactory(currency=alternative_currency, exchange_rate=Decimal("0.937658"))
        self.assertEqual(order.shipping_cost_in_primary_currency().quantize(
            Decimal('.01')), Decimal("10.66"))


class RefundInPrimaryCurrencyTest(TestCase):
    def test_in_primary_currency(self):
        primary_currency = EURCurrencyFactory(primary=True)
        order = TestOrderFactory(
            currency=primary_currency
        )
        OrderRefund.objects.create(
            order=order,
            amount=Decimal("5.00"),
        )

        self.assertEqual(order.refund_in_primary_currency(), Decimal("5.00"))

    def test_in_alternative_currency__more(self):
        primary_currency = EURCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = USDCurrencyFactory()

        order = TestOrderFactory(
            currency=alternative_currency,
        )
        OrderRefund.objects.create(
            order=order,
            amount=Decimal("5.00"),
            exchange_rate=Decimal("1.06649"),
        )
        self.assertEqual(order.refund_in_primary_currency().quantize(
            Decimal('.01')), Decimal("4.69"))

    def test_in_alternative_currency__less(self):
        primary_currency = USDCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = EURCurrencyFactory(primary=False)
        alternative_currency.accepted = True
        alternative_currency.save()

        order = TestOrderFactory(
            currency=alternative_currency,
        )
        OrderRefund.objects.create(
            order=order,
            amount=Decimal("5.00"),
            exchange_rate=Decimal("0.937658")
        )
        self.assertEqual(order.refund_in_primary_currency().quantize(
            Decimal('.01')), Decimal("5.33"))

    def test_multiple_refunds(self):
        primary_currency = EURCurrencyFactory(primary=True)
        order = TestOrderFactory(
            currency=primary_currency
        )
        OrderRefund.objects.create(
            order=order,
            amount=Decimal("1.00"),
        )
        OrderRefund.objects.create(
            order=order,
            amount=Decimal("1.00"),
        )

        self.assertEqual(order.refund_in_primary_currency(), Decimal("2.00"))

    def test_multiple_refunds_different_exhange_rates(self):
        primary_currency = USDCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = EURCurrencyFactory()
        order = TestOrderFactory(
            currency=alternative_currency
        )
        OrderRefund.objects.create(
            order=order,
            amount=Decimal("1.00"),
            exchange_rate=Decimal("1.5555"),
        )
        OrderRefund.objects.create(
            order=order,
            amount=Decimal("1.00"),
            exchange_rate=Decimal("0.95")
        )

        self.assertEqual(order.refund_in_primary_currency(), Decimal("1.69"))


class TotalInPrimaryCurrencyTest(TestCase):
    def test_in_primary_currency(self):
        primary_currency = EURCurrencyFactory(primary=True)
        order = TestOrderFactory(currency=primary_currency)
        self.assertEqual(order.total_in_primary_currency(), Decimal("35.00"))

    def test_in_alternative_currency__more(self):
        primary_currency = EURCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = USDCurrencyFactory()

        order = TestOrderFactory(currency=alternative_currency, exchange_rate=Decimal("1.06649"))
        self.assertEqual(order.total_in_primary_currency().quantize(
            Decimal('.01')), Decimal("32.82"))

    def test_in_alternative_currency__less(self):
        primary_currency = USDCurrencyFactory()
        primary_currency.primary = True
        primary_currency.save()
        alternative_currency = EURCurrencyFactory()

        order = TestOrderFactory(currency=alternative_currency, exchange_rate=Decimal("0.937658"))
        self.assertEqual(order.total_in_primary_currency().quantize(
            Decimal('.01')), Decimal("37.33"))


class DisplayTotalTest(TestCase):
    def test_GBP(self):
        currency = GBPCurrencyFactory()

        order = TestOrderFactory(currency=currency)
        self.assertEqual(order.display_total, '£35.00 (GBP)')

    def test_EUR(self):
        currency = EURCurrencyFactory()

        order = TestOrderFactory(currency=currency)
        self.assertEqual(order.display_total, '€35.00 (EUR)')

    def test_USD(self):
        currency = USDCurrencyFactory()

        order = TestOrderFactory(currency=currency)
        self.assertEqual(order.display_total, '$35.00 (USD)')


class DisplayMethodsTest(TestCase):
    def setUp(self):
        self.currency = USDCurrencyFactory()
        self.currency.primary = True
        self.currency.accepted = True
        self.currency.save()
        self.order = TestOrderFactory(currency=self.currency)

    def test_total(self):
        self.assertEqual(self.order.display_total, '$35.00 (USD)')

    def test_tax(self):
        self.assertEqual(self.order.display_tax, '$0.00 (USD)')

    def test_refund(self):
        self.order.refund = Decimal("5.00")
        self.assertEqual(self.order.display_refund, '$5.00 (USD)')

    def test_sub_total(self):
        self.assertEqual(self.order.display_sub_total, '$25.00 (USD)')

    def test_sub_total_with_tax(self):
        self.assertEqual(self.order.display_sub_total_with_tax, '$25.00 (USD)')

    def test_balance(self):
        self.assertEqual(self.order.display_balance, '$35.00 (USD)')

    def test_balance_paid(self):
        self.assertEqual(self.order.display_balance_paid, '$0.00 (USD)')

    def test_shipping_sub_total(self):
        self.assertEqual(self.order.display_shipping_sub_total, '$10.00 (USD)')

    def test_shipping_with_tax(self):
        self.assertEqual(self.order.display_shipping_with_tax, '$10.00 (USD)')

    def test_shipping_cost(self):
        self.assertEqual(self.order.display_shipping_cost, '$10.00 (USD)')

    def test_discount(self):
        self.order.discount = Decimal("5.00")
        self.assertEqual(self.order.display_discount, '$5.00 (USD)')

    def test_shipping_discount(self):
        self.order.shipping_discount = Decimal("5.00")
        self.assertEqual(self.order.display_shipping_discount, '$5.00 (USD)')

    def test_item_discount(self):
        self.order.discount = Decimal("5.00")
        self.assertEqual(self.order.display_item_discount, '$5.00 (USD)')
