import mock

from django.test import TestCase

from satchmo.shop.factories import (
    OrderStatusFactory,
    OrderFactory,
    StatusFactory,
)


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
        order_status = OrderStatusFactory.build(
            order=order,
            status=status,
        )
        order_status.save()
        self.assertEqual(order.status, order_status)

    @mock.patch("satchmo.shop.models.send_order_update")
    def test_sends_notification(self, mock_send_order_update):
        order = OrderFactory()
        status = StatusFactory(notify=True)
        order_status = OrderStatusFactory.build(
            order=order,
            status=status,
        )
        order_status.save()
        self.assertEqual(len(mock_send_order_update.call_args_list), 1)
        self.assertEqual(
            mock_send_order_update.call_args_list,
            [mock.call(order_status)]
        )

    @mock.patch("satchmo.shop.models.send_order_update")
    def test_doesnt_send_notification(self, mock_send_order_update):
        order = OrderFactory()
        status = StatusFactory(notify=False)
        order_status = OrderStatusFactory.build(
            order=order,
            status=status,
        )
        order_status.save()
        self.assertEqual(len(mock_send_order_update.call_args_list), 0)
