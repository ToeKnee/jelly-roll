from django.core.mail import mail_admins
from django.db import transaction
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from satchmo.shop.views.utils import bad_or_missing
from satchmo.shop.models import Order

import logging
log = logging.getLogger(__name__)


@csrf_exempt
@transaction.atomic
def success(request, template='checkout/success.html'):
    """
    The order has been succesfully processed.  This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        subject = "ERROR Order processing - order not found"
        message = """Can't find order to process

User: {user}

Session:

{session}


GET:

{get}


POST:

{post}
        """.format(
            user=request.user,
            session="\n".join([
                "{key}={value}".format(key=key, value=value)
                for key, value
                in request.session.items()
            ]),
            get="\n".join([
                "{key}={value}".format(key=key, value=value)
                for key, value
                in request.GET.items()
            ]),
            post="\n".join([
                "{key}={value}".format(key=key, value=value)
                for key, value
                in request.POST.items()
            ]),
        )
        mail_admins(subject, message)
        return bad_or_missing(request, _('Your order has already been processed.'))

    complete_order(order)

    if 'cart' in request.session:
        del request.session['cart']

    del request.session['orderID']

    log.info("Successully processed %s" % (order))
    context = {'order': order}
    return render(request, template, context)


@transaction.atomic
def complete_order(order):
    # Track total sold for each product
    for item in order.orderitem_set.select_for_update():
        if item.stock_updated is False:
            product = item.product
            product.total_sold += item.quantity
            product.items_in_stock -= item.quantity
            product.save()

            item.stock_updated = True
            item.save()
            log.debug("Set quantities for %s to %s" %
                      (product, product.items_in_stock))

    order.freeze()
    order.save()


@transaction.atomic
def restock_order(order):
    # Restock the order
    for item in order.orderitem_set.all():
        if item.stock_updated:
            product = item.product
            product.total_sold -= item.quantity
            product.items_in_stock += item.quantity
            product.save()

            item.stock_updated = False
            item.save()
            log.debug("Set quantities for %s to %s" %
                      (product, product.items_in_stock))
