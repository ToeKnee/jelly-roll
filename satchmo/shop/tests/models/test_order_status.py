import mock

from django.test import TestCase

from satchmo.shop.factories import OrderStatusFactory, OrderFactory, StatusFactory


class OrderStatusTest(TestCase):
    @mock.patch("satchmo.shop.models.send_order_update")
    def test_unicode(self, mock_send_order_update):
        order_status = OrderStatusFactory()
        self.assertEqual(str(order_status), "Test")

    @mock.patch("satchmo.shop.models.send_order_update")
    def test_sets_the_order_status(self, mock_send_order_update):
        # Test that it sets the shortcut to the orders latest status
        # TODO: We should just get the latest status, instead of this
        # weirdness.
        order = OrderFactory()
        status = StatusFactory(notify=True)
        order_status = OrderStatusFactory.build(order=order, status=status)
        order_status.save()
        self.assertEqual(order.status, order_status)
