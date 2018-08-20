from django import template

from satchmo.currency.models import Currency
from satchmo.currency.utils import money_format
from satchmo.shop.models import Status

register = template.Library()


@register.inclusion_tag('admin/_ordercount_list.html')
def order_lists():
    """ Show all orders that are in status' that have display set to True """
    status = []
    primary_currency = Currency.objects.get_primary()

    for s in Status.objects.filter(display=True):
        value = 0
        for order in s.orders():
            value += order.total_in_primary_currency()

        if value:
            status.append((s, money_format(value, primary_currency.iso_4217_code)))

    return {
        'status': status,
    }
