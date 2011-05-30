try:
    from decimal import Decimal, InvalidOperation
except:
    from django.utils._decimal import Decimal, InvalidOperation

from django import template
from satchmo.l10n.utils import money_format
from django.utils.safestring import mark_safe

import logging

log = logging.getLogger("satchmo_currency")

register = template.Library()

def currency(value):
    """Convert a value to a money formatted string.

    Usage:
        val|currency
    """
    
    if value == '' or value is None:
        return value

    return mark_safe(money_format(value))

register.filter('currency', currency)
currency.is_safe = True
