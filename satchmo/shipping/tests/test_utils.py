import mock

from decimal import Decimal

from django.test import TransactionTestCase

from satchmo.configuration.models import Setting
from satchmo.currency.factories import (
    EURCurrencyFactory,
    ExchangeRateFactory,
    GBPCurrencyFactory,
)
from satchmo.shipping.models import ECONOMY, STANDARD
from satchmo.shipping.modules.tieredweightzone.factories import WeightTierFactory
from satchmo.shipping.modules.tieredweightzone.models import Shipper
from satchmo.shipping.utils import update_shipping
from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import Cart, CartItem


class UpdateShippingTest(TransactionTestCase):

    @mock.patch("satchmo.shipping.utils.shipping_method_by_key")
    def test_updates_from_shipper(self, mock_shipping_method_by_key):
        currency = EURCurrencyFactory(primary=True)
        order = TestOrderFactory(currency=currency)
        cart = Cart.objects.create(currency=currency)
        for item in order.orderitem_set.all():
            CartItem.objects.create(
                cart=cart,
                product=item.product,
                quantity=item.quantity,
            )
        tier = WeightTierFactory()

        mock_shipping_method_by_key.return_value = Shipper(tier.carrier)

        update_shipping(order, tier.carrier.key, order.contact, cart)

        self.assertEqual(order.shipping_cost, Decimal("1.00"))
        self.assertTrue(order.shipping_signed_for)
        self.assertTrue(order.shipping_tracked)
        self.assertEqual(order.shipping_postage_speed, ECONOMY)
        self.assertTrue(order.shipping_signed_for)
        self.assertEqual(order.estimated_delivery_min_days, 2)
        self.assertEqual(order.estimated_delivery_expected_days, 4)
        self.assertEqual(order.estimated_delivery_max_days, 15)

    def test_updates_from_carrier(self):
        order = TestOrderFactory()
        cart = Cart.objects.create()
        for item in order.orderitem_set.all():
            CartItem.objects.create(
                cart=cart,
                product=item.product,
                quantity=item.quantity,
            )

        update_shipping(order, "per", order.contact, cart)

        self.assertEqual(order.shipping_cost, Decimal("20.00"))
        self.assertFalse(order.shipping_signed_for)
        self.assertFalse(order.shipping_tracked)
        self.assertEqual(order.shipping_postage_speed, STANDARD)
        self.assertFalse(order.shipping_signed_for)
        self.assertEqual(order.estimated_delivery_min_days, 1)
        self.assertEqual(order.estimated_delivery_expected_days, 7)
        self.assertEqual(order.estimated_delivery_max_days, 25)

    def test_converts_currency(self):
        Setting.objects.create(
            group='CURRENCY',
            key='BUFFER',
            value=Decimal("0.00"),
        )
        EURCurrencyFactory(primary=True)
        currency = GBPCurrencyFactory()
        currency.accepted = True
        currency.save()

        order = TestOrderFactory(currency=currency)
        cart = Cart.objects.create(currency=currency)
        for item in order.orderitem_set.all():
            CartItem.objects.create(
                cart=cart,
                product=item.product,
                quantity=item.quantity,
            )
        ExchangeRateFactory(
            rate=Decimal("0.5"),
            currency=currency
        )

        update_shipping(order, "per", order.contact, cart)

        self.assertEqual(order.shipping_cost, Decimal("10.00"))
