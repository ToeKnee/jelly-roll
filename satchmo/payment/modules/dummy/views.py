"""Simple wrapper for standard checkout as implemented in satchmo.payment.views"""

from django.urls import reverse
from django.http import HttpResponseRedirect

from satchmo.configuration.functions import config_get_group
from satchmo.payment.views import confirm, payship
from satchmo.shop.models import Cart

dummy = config_get_group("PAYMENT_DUMMY")


def pay_ship_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(reverse("satchmo_cart"))

    return payship.credit_pay_ship_info(request, dummy)


def confirm_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(reverse("satchmo_cart"))

    return confirm.credit_confirm_info(request, dummy)
