"""Provides the ability to overload forms to provide multiple possible
responses to a form.

For example, the product add form.  You can add to the cart, or to the
wishlist.  The view here just looks in the formdata to determine whether
 to send the request to the cart_add or the wishlist_add view.
"""
from satchmo.shop.views import cart
from satchmo.wishlist.views import wishlist_add
import logging

log = logging.getLogger(__name__)


def smart_add(request):
    """Redirect the request to cart_add (default) or satchmo_wishlist_add
    (overridden) view"""

    if request.POST.get('addwish', '') != '' or request.POST.get('addwish.x', '') != '':
        log.debug("Found addwish in post, returning the wishlist add view")
        return wishlist_add(request)

    return cart.add(request)
