import datetime
import mock

from django.test import TestCase
from django.utils import timezone

from satchmo.shop.factories import (
    OrderFactory,
    PaidOrderFactory,
    ShippedOrderFactory,
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


class EsitmatedDeliveryMinDateTest(TestCase):

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


class EsitmatedDeliveryExpectedDateTest(TestCase):

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


class EsitmatedDeliveryMaxDateTest(TestCase):

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
