from django import template
from django.utils.safestring import mark_safe

from satchmo.currency.utils import (
    convert_to_currency,
    currency_for_request,
    money_format,
)

import logging

log = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def currency(context, value, currency_code=None):
    """Convert a value to a money formatted string.

    If a currency is not supplied, one will selected based on the
    request.

    Usage:
        {% currency val %}

    """

    if value == "" or value is None:
        return value

    if currency_code is None:
        request = context.get("request")
        currency_code = currency_for_request(request)

    value = convert_to_currency(value, currency_code)

    return mark_safe(money_format(value, currency_code))


currency.is_safe = True
