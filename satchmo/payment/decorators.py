# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext"
from django.shortcuts import render

from satchmo.utils import is_string_like
from satchmo.shop.models import Cart


def cart_has_minimum_order(
    template="product/minimum_order.html", min_order="PAYMENT.MINIMUM_ORDER"
):
    """
    Decorator for checkout views that ensures the active cart meets the minimum order
    requirements.  If not, then it shows the user the minimum order required.

    Params:
    - template: defaults to satchmo/product/minimum_order.html
    - min_order: If this is a string, it wil be used to look up the value from Satchmo's configuration
      system, if it is a decimal, it will be used directly as the minimum required.
    """

    def _decorate(view_func):
        def _checkorder(
            request, template=template, min_order=min_order, *args, **kwargs
        ):
            # resolve the min order
            if is_string_like(min_order):
                from satchmo.configuration.functions import config_value

                min_order = config_value(*min_order.split("."))

            cart = Cart.objects.from_request(request)
            if cart.total >= min_order:
                return view_func(request, *args, **kwargs)
            else:
                return render(request, template, {"minimum_order": min_order})

        _checkorder.__doc__ = view_func.__doc__
        _checkorder.__dict__ = view_func.__dict__

        return _checkorder

    return _decorate
