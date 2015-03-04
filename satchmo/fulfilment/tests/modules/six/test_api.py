import json
from decimal import Decimal

from django.test import TestCase

from satchmo.shop.factories import TestOrderFactory
from satchmo.fulfilment.modules.six.api import (
    float_price,
    order_payload,
)


class OrderPayload(TestCase):
    def test_float_price(self):
        self.assertEqual(15.25, float_price(Decimal("15.25")))

    def test_float_price__zero(self):
        self.assertEqual(0.0, float_price(Decimal("0.00")))

    def test_float_price__none(self):
        self.assertEqual(0.0, float_price(None))

    def test_order_payload(self):
        self.maxDiff = None
        order = TestOrderFactory()

        callback_url = "https://example.com/shop/fulfilment/six/{id}/{hash}/".format(
            id=order.id,
            hash=order.verification_hash
        )

        self.assertEqual(json.loads(order_payload(order)), {
            u"api_key": u"",
            u"test": True,
            u"allow_preorder": False,
            u"update_stock": True,

            u"order": {
                u"client_ref": order.id,
                u"po_number": order.id,
                u"date_placed": unicode(order.time_stamp),
                u"callback_url": callback_url,
                u"postage_speed": 2,
                u"postage_cost": float_price(order.shipping_cost),
                u"total_amount": float_price(order.sub_total),
                u"signed_for": False,
                u"tracked": False,
                u"ShippingContact": {
                    u"dear": order.contact.user.first_name,
                    u"name": order.ship_addressee,
                    u"email": order.contact.user.email,
                    u"phone": order.contact.primary_phone or u"",
                    u"address": order.ship_street1,
                    u"address_contd": order.ship_street2,
                    u"city": order.ship_city,
                    u"county": order.ship_state,
                    u"country": unicode(order.ship_country),
                    u"postcode": order.ship_postal_code,
                },
                u"BillingContact": {
                    u"name": order.bill_addressee,
                    u"email": order.contact.user.email,
                    u"phone": order.contact.primary_phone or u"",
                    u"address": order.bill_street1,
                    u"address_contd": order.bill_street2,
                    u"city": order.bill_city,
                    u"county": order.bill_state,
                    u"country": unicode(order.bill_country),
                    u"postcode": order.bill_postal_code,
                },
                u"items": [
                    {
                        u"client_ref": order.orderitem_set.all()[0].product.slug,
                        u"quantity": order.orderitem_set.all()[0].quantity,
                        u"price": float_price(order.orderitem_set.all()[0].unit_price),
                    }
                ]
            }
        })
