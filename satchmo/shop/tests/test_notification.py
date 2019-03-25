from django.core import mail
from django.test import TestCase
from django.template.defaultfilters import date

from satchmo.shop.factories import OrderStatusFactory, StatusFactory
from satchmo.shop.models import Config
from satchmo.shop.notification import send_order_update


class SendOrderUpdateTest(TestCase):
    def test_send_generic_status_email(self):
        order_status = OrderStatusFactory()

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        shop_config = Config.objects.get_current()
        self.assertEqual(
            mail.outbox[0].subject,
            "Your {store_name} order #{id} has been updated - {status}".format(
                store_name=shop_config.store_name.encode("utf-8"),
                id=order_status.order_id,
                status=order_status,
            ),
        )
        self.assertIn(shop_config.store_name.encode("utf-8"), mail.outbox[0].body)
        self.assertIn(str(order_status.order_id), mail.outbox[0].body)
        self.assertIn(order_status.status.status, mail.outbox[0].body)

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        alternative, content_type = mail.outbox[0].alternatives[0]
        self.assertEqual(content_type, "text/html")
        self.assertIn(str(order_status.order_id), alternative)
        self.assertIn(order_status.status.status, alternative)

    def test_send_specific_status_email__processing(self):
        order_status = OrderStatusFactory(status__status="Processing")

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        shop_config = Config.objects.get_current()
        self.assertEqual(
            mail.outbox[0].subject,
            "Your {store_name} order #{id} has been updated - {status}".format(
                store_name=shop_config.store_name.encode("utf-8"),
                id=order_status.order_id,
                status=order_status,
            ),
        )
        self.assertIn(shop_config.store_name.encode("utf-8"), mail.outbox[0].body)
        self.assertIn(str(order_status.order_id), mail.outbox[0].body)
        self.assertIn("processing", mail.outbox[0].body)
        self.assertIn(
            "We are hoping to post it on {ship_date}.".format(
                ship_date=date(order_status.order.shipping_date())
            ),
            mail.outbox[0].body,
        )
        self.assertIn(
            "It should be with you between {min} and {max}.".format(
                min=date(order_status.order.estimated_delivery_expected_date()),
                max=date(order_status.order.estimated_delivery_max_date()),
            ),
            mail.outbox[0].body,
        )

        self.assertEqual(len(mail.outbox[0].alternatives), 1)
        alternative, content_type = mail.outbox[0].alternatives[0]
        self.assertEqual(content_type, "text/html")
        self.assertIn(str(order_status.order_id), alternative)
        self.assertIn("processing", alternative)
        self.assertIn(
            "We are hoping to post it on {ship_date}.".format(
                ship_date=date(order_status.order.shipping_date())
            ),
            alternative,
        )
        self.assertIn(
            "It should be with you between {min} and {max}.".format(
                min=date(order_status.order.estimated_delivery_expected_date()),
                max=date(order_status.order.estimated_delivery_max_date()),
            ),
            alternative,
        )

    def test_ignores_notify_false_status(self):
        status = StatusFactory(notify=False)

        order_status = OrderStatusFactory(status=status)
        send_order_update(order_status)

        # Test that no messages have been sent.
        self.assertEqual(len(mail.outbox), 0)

    def test_saving_status_doesnt_notify_again(self):
        order_status = OrderStatusFactory()
        self.assertEqual(len(mail.outbox), 1)

        order_status.save()
        # No more emails
        self.assertEqual(len(mail.outbox), 1)
