"""
Each shipping option uses the data in an Order object to calculate the
shipping cost and return the value
"""
import math
from decimal import Decimal, ROUND_UP
from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import config_value
from satchmo.shipping.modules.base import BaseShipper


class Shipper(BaseShipper):
    id = "RoyalMailContract"

    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return _("Airmail (Tracking not available)")

    def cost(self):
        """
        Complex calculations can be done here as long as the return value is a dollar figure
        """
        fee = Decimal("0.00")
        weight = Decimal("0.00")

        packing_fee = config_value('satchmo.shipping.modules.royalmailcontract', 'PACKING_FEE')
        # An Item is Royal Mail's name for a packet.  Not a singular
        # product.
        max_weight_per_item = config_value('satchmo.shipping.modules.royalmailcontract', 'MAX_WEIGHT_PER_ITEM')
        if self.shipping_to_eu():
            per_item_rate = config_value('satchmo.shipping.modules.royalmailcontract', 'PER_RATE_EU')
            per_kg_rate = config_value('satchmo.shipping.modules.royalmailcontract', 'PER_KG_EU')
        else:
            per_item_rate = config_value('satchmo.shipping.modules.royalmailcontract', 'PER_RATE_ROW')
            per_kg_rate = config_value('satchmo.shipping.modules.royalmailcontract', 'PER_KG_ROW')

        for cartitem in self.cart.cartitem_set.all():
            if cartitem.product.is_shippable:
                weight += cartitem.product.weight * cartitem.quantity

        # Round weight up to nearest 100g
        weight = weight * 10  # Kgs to tens of grams
        weight = math.ceil(weight)  # Round to nearest 100g
        weight = weight / 10  # Tens of grams to Kgs
        fee += Decimal(str(weight)) * per_kg_rate

        # If the weight is > MAX_WEIGHT_PER_ITEM split the order in to multiple items (packets)
        # Round up to nearest Kg
        weight = int(math.ceil(weight))
        # Times to apply per_item_rate
        items = int(math.ceil(weight / max_weight_per_item))
        fee += per_item_rate * items

        # Add TAX
        if self.shipping_to_eu():
            fee = fee * Decimal(str(1.2))  # 20% VAT - Not happy about
                                           #this, but this is the only
                                           #module that is charging
                                           #VAT atm :(

        # Add packing fee
        fee += packing_fee

        # Round to nearest penny
        fee = fee.quantize(Decimal('.01'), rounding=ROUND_UP)

        return fee

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return _("Royal Mail")

    def expectedDelivery(self):
        """
        Can be a plain string or complex calcuation returning an actual date
        """
        if self.shipping_to_eu():
            days = _("3 - 7 working days")
        else:
            days = _("5 - 10 working days")
        return days

    def valid(self, order=None):
        """
        Exclude countries that we don't want to ship to, also exclude
        the United Kingdom as this shipping module doesn't support GB.
        """
        excluded_countries = config_value('satchmo.shipping.modules.royalmailcontract', 'EXCLUDE_COUNTRY')
        excluded_countries.append(u'GB')
        return self.contact.shipping_address.country.iso2_code not in excluded_countries

    def shipping_to_eu(self):
        """
        If the contact's shipping address is in an EU country
        """
        return self.contact.shipping_address.country.eu
