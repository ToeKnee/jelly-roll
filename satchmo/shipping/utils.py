from decimal import Decimal

from satchmo.shipping.config import shipping_method_by_key
from satchmo.shipping.models import STANDARD


def update_shipping(order, shipping, contact, cart):
    """Set the shipping for this order"""
    # Set a default for when no shipping module is used
    order.shipping_cost = Decimal("0.00")

    # Save the shipping info
    shipper = shipping_method_by_key(shipping)
    shipper.calculate(cart, contact)
    order.shipping_description = shipper.description().encode("utf-8")
    order.shipping_method = shipper.method()
    order.shipping_cost = shipper.cost()
    order.shipping_model = shipping

    if shipper.carrier:
        # If shipping details available, set the details for the order
        if hasattr(shipper.carrier, "signed_for"):
            order.shipping_signed_for = shipper.carrier.signed_for
        else:
            order.shipping_signed_for = False

        if hasattr(shipper.carrier, "tracked"):
            order.shipping_tracked = shipper.carrier.tracked
        else:
            order.shipping_tracked = False

        if hasattr(shipper.carrier, "postage_speed"):
            order.shipping_postage_speed = shipper.carrier.postage_speed
        else:
            order.shipping_postage_speed = STANDARD
