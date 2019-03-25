from django.template import Library
from satchmo.currency.utils import money_format, currency_for_request

register = Library()


@register.simple_tag(takes_context=True)
def option_price(context, option_item):
    """
    Returns the price as (+$1.00)
    or (-$1.00) depending on the sign of the price change
    The currency format is base upon locale
    """
    output = ""
    if option_item.price_change != 0:
        request = context.get("request")
        currency_code = currency_for_request(request)
        amount = money_format(abs(option_item.price_change), currency_code)

    if option_item.price_change < 0:
        output = "(- %s)" % amount
    elif option_item.price_change > 0:
        output = "(+ %s)" % amount
    return output


@register.simple_tag(takes_context=True)
def option_total_price(context, product, option_item):
    """
    Returns the price as (+$1.00)
    or (-$1.00) depending on the sign of the price change
    The currency format is base upon locale
    """
    if option_item.price_change:
        val = product.unit_price + option_item.price_change
    else:
        val = product.unit_price

    request = context.get("request")
    currency_code = currency_for_request(request)

    return money_format(val, currency_code)
