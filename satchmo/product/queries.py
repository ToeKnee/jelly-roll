from django.core.cache import cache
from satchmo.product.models import Product

def bestsellers(limit=10):
    """Look up the bestselling products and return in a list"""
    key = "bestsellers_%s" % limit
    if cache.has_key(key):
        products = cache.get(key)
    else:
        products = Product.objects.active_by_site().order_by("-total_sold").exclude(total_sold=0)[:limit]
        cache.set(key, products, 1800)
    return products
