from django.conf import settings
from django.template import Library, Node
from satchmo.l10n.utils import money_format
from satchmo.product.models import Option

register = Library()

def option_price(option_item):
    """
    Returns the price as (+$1.00)
    or (-$1.00) depending on the sign of the price change
    The currency format is base upon locale
    """
    output = ""
    if option_item.price_change != 0:
        amount = money_format(abs(option_item.price_change))
    if option_item.price_change < 0:
        output = "(- %s)" % amount
    if option_item.price_change > 0:
        output = "(+ %s)" % amount
    return output

register.simple_tag(option_price)

def option_total_price(product, option_item):
    """
    Returns the price as (+$1.00)
    or (-$1.00) depending on the sign of the price change
    The currency format is base upon locale
    """
    if option_item.price_change:
        val = product.unit_price + option_item.price_change
    else:
        val = product.unit_price
    return money_format(val)

register.simple_tag(option_total_price)
