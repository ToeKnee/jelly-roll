"""Simple wrapper for standard checkout as implemented in satchmo.payment.views"""

from django import http
from .forms import PurchaseorderPayShipForm
from satchmo.configuration import config_get_group
from satchmo.payment.views import confirm, payship
from satchmo.utils.dynamic import lookup_url
from satchmo.shop.models import Cart
from django.core import urlresolvers
from django.http import HttpResponseRedirect
import logging

log = logging.getLogger(__name__)

settings = config_get_group('PAYMENT_PURCHASEORDER')
    
def pay_ship_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))

    return payship.base_pay_ship_info(
        request, 
        settings, 
        purchaseorder_process_form, 
        'checkout/purchaseorder/pay_ship.html')
        
def confirm_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))

    return confirm.credit_confirm_info(
        request, 
        settings, 
        template='checkout/purchaseorder/confirm.html')

def purchaseorder_process_form(request, contact, working_cart, payment_module):
    log.debug('purchaseorder_process_form')
    if request.method == "POST":
        log.debug('handling POST')
        new_data = request.POST.copy()
        form = PurchaseorderPayShipForm(request, payment_module, new_data)
        if form.is_valid():
            form.save(request, working_cart, contact, payment_module)
            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
    else:
        log.debug('new form')
        form = PurchaseorderPayShipForm(request, payment_module)

    return (False, form)
