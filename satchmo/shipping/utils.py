from decimal import Decimal

from satchmo.currency.utils import convert_to_currency
from satchmo.shipping.config import shipping_method_by_key
from satchmo.shipping.models import STANDARD


def update_shipping(order, shipping, contact, cart):
    """ In-place update of shipping details for this order"""
    # Set a default for when no shipping module is used
    order.shipping_cost = Decimal("0.00")

    # Save the shipping info
    shipper = shipping_method_by_key(shipping)
    shipper.calculate(cart, contact)
    order.shipping_description = shipper.description().encode("utf-8")
    order.shipping_method = shipper.method()
    order.shipping_cost = convert_to_currency(shipper.cost(), order.currency.iso_4217_code)
    order.shipping_model = shipping

    if hasattr(shipper, "carrier"):
        shipping_details = shipper.carrier
    else:
        shipping_details = shipper

    # If shipping details available, set the details for the order
    order.shipping_signed_for = getattr(shipping_details, "signed_for", False)
    order.shipping_tracked = getattr(shipping_details, "tracked", False)
    order.shipping_postage_speed = getattr(shipping_details, "postage_speed", STANDARD)
    order.estimated_delivery_min_days = getattr(shipping_details, "estimated_delivery_min_days", 1)
    order.estimated_delivery_expected_days = getattr(shipping_details, "estimated_delivery_expected_days", 7)
    order.estimated_delivery_max_days = getattr(shipping_details, "estimated_delivery_max_days", 25)
