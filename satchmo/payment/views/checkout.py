from django.db import transaction
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from satchmo.shop.views.utils import bad_or_missing
from satchmo.shop.models import Order

import logging
log = logging.getLogger(__name__)


@csrf_exempt
@transaction.commit_on_success
def success(request, template='checkout/success.html'):
    """
    The order has been succesfully processed.  This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))

    # Track total sold for each product
    for item in order.orderitem_set.all():
        if item.stock_updated == False:
            product = item.product
            product.total_sold += item.quantity
            product.items_in_stock -= item.quantity
            product.save()

            item.stock_updated = True
            item.save()
            log.debug("Set quantities for %s to %s" % (product, product.items_in_stock))

    order.freeze()
    order.save()
    if 'cart' in request.session:
        del request.session['cart']
    del request.session['orderID']
    log.info("Successully processed " % (order))
    context = RequestContext(request, {'order': order})
    return render_to_response(template, context)
