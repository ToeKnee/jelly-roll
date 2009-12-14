from satchmo.configuration import config_get_group
from satchmo.payment.views import confirm, payship
from satchmo.shop.models import Cart
from django.core import urlresolvers
from django.http import HttpResponseRedirect
    
def pay_ship_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))

    return payship.credit_pay_ship_info(request, config_get_group('PAYMENT_TRUSTCOMMERCE'))

def confirm_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))

    return confirm.credit_confirm_info(request, config_get_group('PAYMENT_TRUSTCOMMERCE'))
