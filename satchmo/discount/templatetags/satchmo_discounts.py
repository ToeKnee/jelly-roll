from decimal import Decimal
from django import template

from satchmo.currency.utils import (
    convert_to_currency,
    currency_for_request,
    money_format,
)
from satchmo.discount.utils import calc_by_percentage

register = template.Library()


@register.simple_tag(takes_context=True)
def discount_price(context, product, discount):
    """Returns the product price with the discount applied.

    Ex: {% discount_price product sale %}
    """

    request = context.get("request")
    currency = currency_for_request(request)
    unit_price = convert_to_currency(product.unit_price, currency)

    if discount and discount.valid_for_product(product):
        price = calc_by_percentage(unit_price, discount.percentage)
    else:
        price = unit_price
    return money_format(price, currency)


@register.simple_tag(takes_context=True)
def discount_saved(context, product, discount):
    """Returns the amount saved by the discount"""

    request = context.get("request")
    currency = currency_for_request(request)
    if discount and discount.valid_for_product(product):
        unit_price = convert_to_currency(product.unit_price, currency)
        discounted = calc_by_percentage(unit_price, discount.percentage)
        saved = unit_price - discounted
        cents = Decimal("0.01")
        price = saved.quantize(cents)
    else:
        price = Decimal('0.00')
    return money_format(price, currency)
