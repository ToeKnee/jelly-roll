import json

from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase, RequestFactory
from django.utils import timezone

from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import Order
from satchmo.fulfilment.modules.six.views import despatch
from satchmo.fulfilment.modules.six.api import float_price


class DespatchTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_order_not_found(self):
        request = self.factory.post("/")

        with self.assertRaises(Http404):
            despatch(request, order_id=1234, verification_hash="abcdef1234567890")

    def test_verification_does_not_match(self):
        order = TestOrderFactory()
        request = self.factory.post("/")
        response = despatch(request, order_id=order.id, verification_hash="abcdef1234567890")

        self.assertEqual(response.content, '{"success": false}')

    def test_invalid_json(self):
        order = TestOrderFactory()
        request = self.factory.post("/", data="{Invalid-Json;'", content_type="application/json")
        response = despatch(request, order_id=order.id, verification_hash=order.verification_hash)
        self.assertEqual(response.content, '{"success": false}')

    def test_despatch__no_tracking(self):
        order = TestOrderFactory()
        data = {
            "type": "despatch",
            "client_ref": str(order.id),
            "date_despatched": str(timezone.now()),
            "client_area_link": "http://subdomain.sixworks.co.uk/order/101",
            "postage_method": "1st Class Packet",
            "boxed_weight": 645,
            "items": [{
                "client_ref": order.orderitem_set.all()[0].product.slug,
                "quantity": order.orderitem_set.all()[0].quantity,
                "batches_used": [
                    {
                        "client_ref": order.orderitem_set.all()[0].product.slug,
                        "batch": "0014",
                        "quantity": order.orderitem_set.all()[0].quantity
                    },
                ]
            }],
        }
        request = self.factory.post("/", data=json.dumps(data), content_type="application/json")
        response = despatch(request, order_id=order.id, verification_hash=order.verification_hash)
        self.assertEqual(response.content, '{"success": true}')
        order = Order.objects.get(id=order.id)
        self.assertIn(data["date_despatched"], order.notes)
        self.assertIn(data["client_area_link"], order.notes)
        self.assertIn(data["postage_method"], order.notes)
        self.assertIn(str(data["boxed_weight"]), order.notes)

        self.assertIsNone(order.tracking_number)
        self.assertIsNone(order.tracking_url)

        self.assertEqual(order.status.notes, "Thanks for your order!\n")

    def test_despatch__with_tracking(self):
        order = TestOrderFactory()
        data = {
            "type": "despatch",
            "client_ref": str(order.id),
            "date_despatched": str(timezone.now()),
            "client_area_link": "http://subdomain.sixworks.co.uk/order/101",
            "postage_method": "1st Class Packet",
            "boxed_weight": 645,
            "tracking_number": "GB1010101010A",
            "tracking_link": "http://royalmail.com/track?tracking_number=GB1010101010A",
            "items": [{
                "client_ref": order.orderitem_set.all()[0].product.slug,
                "quantity": order.orderitem_set.all()[0].quantity,
                "batches_used": [
                    {
                        "client_ref": order.orderitem_set.all()[0].product.slug,
                        "batch": "0014",
                        "quantity": order.orderitem_set.all()[0].quantity
                    },
                ]
            }],
        }
        request = self.factory.post("/", data=json.dumps(data), content_type="application/json")
        response = despatch(request, order_id=order.id, verification_hash=order.verification_hash)
        self.assertEqual(response.content, '{"success": true}')
        order = Order.objects.get(id=order.id)
        self.assertIn(data["date_despatched"], order.notes)
        self.assertIn(data["client_area_link"], order.notes)
        self.assertIn(data["postage_method"], order.notes)
        self.assertIn(str(data["boxed_weight"]), order.notes)

        self.assertEqual(order.tracking_number, data["tracking_number"])
        self.assertEqual(order.tracking_url, data["tracking_link"])

        order_status = """Thanks for your order!\nYou can track your order at {tracking_url}\n"""
        self.assertEqual(order.status.notes, order_status.format(
            tracking_number=order.tracking_number,
            tracking_url=order.tracking_url,
        ))

    def test__web_client(self):
        order = TestOrderFactory()
        data = {
            "type": "despatch",
            "client_ref": str(order.id),
            "date_despatched": str(timezone.now()),
            "client_area_link": "http://subdomain.sixworks.co.uk/order/101",
            "postage_method": "1st Class Packet",
            "postage_cost": str(float_price(order.shipping_cost)),
            "boxed_weight": 645,
            "tracking_number": "GB1010101010A",
            "tracking_link": "http://royalmail.com/track?tracking_number=GB1010101010A",
            "items": [{
                "client_ref": order.orderitem_set.all()[0].product.slug,
                "quantity": order.orderitem_set.all()[0].quantity,
                "batches_used": [
                    {
                        "client_ref": order.orderitem_set.all()[0].product.slug,
                        "batch": "0014",
                        "quantity": order.orderitem_set.all()[0].quantity
                    },
                ]
            }],
        }
        response = self.client.post(reverse("six_despatch", kwargs={
            "order_id": str(order.id),
            "verification_hash": str(order.verification_hash),
        }), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.content, '{"success": true}')
        order = Order.objects.get(id=order.id)
        self.assertIn(data["date_despatched"], order.notes)
        self.assertIn(data["client_area_link"], order.notes)
        self.assertIn(data["postage_method"], order.notes)
        self.assertIn(data["postage_cost"], order.notes)
        self.assertIn(str(data["boxed_weight"]), order.notes)

        self.assertEqual(order.tracking_number, data["tracking_number"])
        self.assertEqual(order.tracking_url, data["tracking_link"])

        order_status = """Thanks for your order!\nYou can track your order at {tracking_url}\n"""
        self.assertEqual(order.status.notes, order_status.format(
            tracking_number=order.tracking_number,
            tracking_url=order.tracking_url,
        ))

    def test_despatch__replacement_order(self):
        # Replacement orders have "-a" or similar tacked onto the end
        # of the order number
        order = TestOrderFactory()
        data = {
            "type": "despatch",
            "client_ref": str(order.id),
            "date_despatched": str(timezone.now()),
            "client_area_link": "http://subdomain.sixworks.co.uk/order/101",
            "postage_method": "1st Class Packet",
            "boxed_weight": 645,
            "items": [{
                "client_ref": order.orderitem_set.all()[0].product.slug,
                "quantity": order.orderitem_set.all()[0].quantity,
                "batches_used": [
                    {
                        "client_ref": order.orderitem_set.all()[0].product.slug,
                        "batch": "0014",
                        "quantity": order.orderitem_set.all()[0].quantity
                    },
                ]
            }],
        }
        url = reverse("six_despatch_replacement", kwargs={
            "order_id": "{order_id}-a".format(order_id=order.id),
            "verification_hash": order.verification_hash,
        })
        request = self.factory.post(url, data=json.dumps(data), content_type="application/json")
        response = despatch(request, order_id="{order_id}-a".format(order_id=order.id), verification_hash=order.verification_hash)
        self.assertEqual(response.content, '{"success": true}')
        order = Order.objects.get(id=order.id)
        self.assertIn(data["date_despatched"], order.notes)
        self.assertIn(data["client_area_link"], order.notes)
        self.assertIn(data["postage_method"], order.notes)
        self.assertIn(str(data["boxed_weight"]), order.notes)

        self.assertIsNone(order.tracking_number)
        self.assertIsNone(order.tracking_url)

        self.assertEqual(order.status.notes, "Thanks for your order!\n")
