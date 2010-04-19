from django import template
from satchmo.shop.models import Status
from satchmo.shop.utils import is_multihost_enabled

register = template.Library()

def order_lists():
    """ Show all orders that are in status' that have display set to True """
    return {
        'status': Status.objects.filter(display=True),
        'multihost' : is_multihost_enabled()
    }
register.inclusion_tag('admin/_ordercount_list.html')(order_lists)
