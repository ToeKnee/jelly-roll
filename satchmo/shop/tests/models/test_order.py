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


class OrderTotalTest(TestCase):
    def test_GBP(self):
        currency = GBPCurrencyFactory()

        order = TestOrderFactory(currency=currency)
        self.assertEqual(order.order_total, u'£35.00 (GBP)')

    def test_EUR(self):
        currency = EURCurrencyFactory()

        order = TestOrderFactory(currency=currency)
        self.assertEqual(order.order_total, u'€35.00 (EUR)')

    def test_USD(self):
        currency = USDCurrencyFactory()

        order = TestOrderFactory(currency=currency)
        self.assertEqual(order.order_total, u'$35.00 (USD)')


class DisplayMethodsTest(TestCase):
    def setUp(self):
        self.currency = USDCurrencyFactory()
        self.order = TestOrderFactory(currency=self.currency)

    def test_total(self):
        self.assertEqual(self.order.display_total, u'$35.00 (USD)')

    def test_tax(self):
        self.assertEqual(self.order.display_tax, u'$0.00 (USD)')

    def test_refund(self):
        self.order.refund = Decimal("5.00")
        self.assertEqual(self.order.display_refund, u'$5.00 (USD)')

    def test_sub_total(self):
        self.assertEqual(self.order.display_sub_total, u'$25.00 (USD)')

    def test_sub_total_with_tax(self):
        self.assertEqual(self.order.display_sub_total_with_tax, u'$25.00 (USD)')

    def test_balance(self):
        self.assertEqual(self.order.display_balance, u'$35.00 (USD)')

    def test_balance_paid(self):
        self.assertEqual(self.order.display_balance_paid, u'$0.00 (USD)')

    def test_shipping_sub_total(self):
        self.assertEqual(self.order.display_shipping_sub_total, u'$10.00 (USD)')

    def test_shipping_with_tax(self):
        self.assertEqual(self.order.display_shipping_with_tax, u'$10.00 (USD)')

    def test_shipping_cost(self):
        self.assertEqual(self.order.display_shipping_cost, u'$10.00 (USD)')

    def test_discount(self):
        self.order.discount = Decimal("5.00")
        self.assertEqual(self.order.display_discount, u'$5.00 (USD)')

    def test_shipping_discount(self):
        self.order.shipping_discount = Decimal("5.00")
        self.assertEqual(self.order.display_shipping_discount, u'$5.00 (USD)')

    def test_item_discount(self):
        self.order.discount = Decimal("5.00")
        self.assertEqual(self.order.display_item_discount, u'$5.00 (USD)')
