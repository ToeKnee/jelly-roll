from decimal import Decimal

from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from satchmo.configuration.functions import config_get_group, config_value
from satchmo.payment.forms import PaymentMethodForm, CustomChargeForm
from satchmo.shop.models import Order, OrderItem
from satchmo.shop.views.utils import bad_or_missing
from satchmo.utils.dynamic import lookup_url

import logging
log = logging.getLogger(__name__)


def balance_remaining_order(request, order_id=None):
    """Load the order into the session, so we can charge the remaining amount"""
    # this will create an "OrderCart" - a fake cart to allow us to check out
    request.session['cart'] = 'order'
    request.session['orderID'] = order_id
    return balance_remaining(request)


def balance_remaining(request):
    """Allow the user to pay the remaining balance."""
    order = None
    orderid = request.session.get('orderID')
    if orderid:
        try:
            order = Order.objects.get(pk=orderid)
        except Order.DoesNotExist:
            # TODO: verify user against current user
            pass

    if not order:
        url = reverse('satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    if request.method == "POST":
        new_data = request.POST.copy()
        form = PaymentMethodForm(new_data, order=order)
        if form.is_valid():
            data = form.cleaned_data
            modulename = data['paymentmethod']
            if not modulename.startswith('PAYMENT_'):
                modulename = 'PAYMENT_' + modulename

            paymentmodule = config_get_group(modulename)
            url = lookup_url(paymentmodule, 'satchmo_checkout-step2')
            return HttpResponseRedirect(url)

    else:
        form = PaymentMethodForm(order=order)

    ctx = {
        'form': form,
        'order': order,
        'paymentmethod_ct': len(config_value('PAYMENT', 'MODULES'))
    }
    return render(request, 'checkout/balance_remaining.html', ctx)


def charge_remaining(request, orderitem_id):
    """Given an orderitem_id, this returns a confirmation form."""

    try:
        orderitem = OrderItem.objects.get(pk=orderitem_id)
    except OrderItem.DoesNotExist:
        return bad_or_missing(request, _("The orderitem you have requested doesn't exist, or you don't have access to it."))

    amount = orderitem.product.customproduct.full_price

    data = {
        'orderitem': orderitem_id,
        'amount': amount,
    }
    form = CustomChargeForm(data)
    ctx = {'form': form}
    return render(request, 'admin/charge_remaining_confirm.html', ctx)


def charge_remaining_post(request):
    if not request.method == 'POST':
        return bad_or_missing(request, _("No form found in request."))

    data = request.POST.copy()

    form = CustomChargeForm(data)
    if form.is_valid():
        data = form.cleaned_data
        try:
            orderitem = OrderItem.objects.get(pk=data['orderitem'])
        except OrderItem.DoesNotExist:
            return bad_or_missing(request, _("The orderitem you have requested doesn't exist, or you don't have access to it."))

        price = data['amount']
        line_price = price * orderitem.quantity
        orderitem.unit_price = price
        orderitem.line_item_price = line_price
        orderitem.save()

        order = orderitem.order

        if not order.shipping_cost:
            order.shipping_cost = Decimal("0.00")

        if data['shipping']:
            order.shipping_cost += data['shipping']

        order.recalculate_total()

        messages.add_message(request, messages.INFO, _(
            'Charged for custom product and recalculated totals.'))

        notes = data['notes']
        if not notes:
            notes = 'Updated total price'

        order.add_status(notes=notes)

        return HttpResponseRedirect('/admin/shop/order/%i' % order.id)
    else:
        ctx = {'form': form}
        return render(request, 'admin/charge_remaining_confirm.html', ctx)
