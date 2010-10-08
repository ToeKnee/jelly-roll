from django import template
from satchmo.shop.models import Status
from satchmo.shop.utils import is_multihost_enabled

register = template.Library()

def order_lists():
    """ Show all orders that are in status' that have display set to True """
    status = []
    for s in Status.objects.filter(display=True):
        value = 0
        for order in s.orders():
            value += order.total
        status.append((s, value))
    return {
        'status': status,
        'multihost' : is_multihost_enabled()
    }
register.inclusion_tag('admin/_ordercount_list.html')(order_lists)
