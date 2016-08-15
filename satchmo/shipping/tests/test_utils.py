from django.test import TestCase

import mock

from satchmo.shipping.models import ECONOMY, STANDARD
from satchmo.shipping.modules.tieredweightzone.factories import WeightTierFactory
from satchmo.shipping.modules.tieredweightzone.models import Shipper
from satchmo.shipping.utils import update_shipping
from satchmo.shop.factories import OrderFactory
from satchmo.shop.models import Cart


class UpdateShippingTest(TestCase):

    @mock.patch("satchmo.shipping.utils.shipping_method_by_key")
    def test_updates_from_shipper(self, mock_shipping_method_by_key):
        order = OrderFactory()
        cart = Cart()
        tier = WeightTierFactory()

        mock_shipping_method_by_key.return_value = Shipper(tier.carrier)

        update_shipping(order, tier.carrier.key, order.contact, cart)

        self.assertTrue(order.shipping_signed_for)
        self.assertTrue(order.shipping_tracked)
        self.assertEqual(order.shipping_postage_speed, ECONOMY)
        self.assertTrue(order.shipping_signed_for)
        self.assertEqual(order.estimated_delivery_min_days, 2)
        self.assertEqual(order.estimated_delivery_expected_days, 4)
        self.assertEqual(order.estimated_delivery_max_days, 15)

    def test_updates_from_carrier(self):
        order = OrderFactory()
        cart = Cart()
        'satchmo.shipping.modules.per'

        update_shipping(order, "per", order.contact, cart)

        self.assertFalse(order.shipping_signed_for)
        self.assertFalse(order.shipping_tracked)
        self.assertEqual(order.shipping_postage_speed, STANDARD)
        self.assertFalse(order.shipping_signed_for)
        self.assertEqual(order.estimated_delivery_min_days, 1)
        self.assertEqual(order.estimated_delivery_expected_days, 7)
        self.assertEqual(order.estimated_delivery_max_days, 25)
