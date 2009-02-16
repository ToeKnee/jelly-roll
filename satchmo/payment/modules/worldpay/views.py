from satchmo.configuration import config_get_group
from satchmo.payment.views import confirm, payship

from django import http
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from satchmo.configuration import config_get_group
from satchmo.contact.models import Contact
from satchmo.configuration import config_value 
from satchmo.payment.config import payment_live
from satchmo.shop.models import Cart, Order, OrderPayment
from satchmo.utils.dynamic import lookup_url, lookup_template
from satchmo.payment.views.checkout import success as generic_success
from satchmo.shop.notification import send_order_confirmation
from satchmo.payment.utils import pay_ship_save, record_payment
from django.contrib.sessions.backends.db import SessionStore


import base64
import hmac
import logging
import sha, md5
import time
from datetime import datetime

payment_module = config_get_group('PAYMENT_WORLDPAY')

def pay_ship_info(request):
    return payship.simple_pay_ship_info(request, payment_module, template='checkout/worldpay/pay_ship.html')

def confirm_info(request):
    "Create form to send to WorldPay"
    
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        order = None

    if not (order and order.validate(request)):
        context = RequestContext(request,
            {'message': _('Your order is no longer valid.')})
        return render_to_response('shop_404.html', context)

    template = lookup_template(payment_module, 'checkout/worldpay/confirm.html')
    
    
    live = payment_module.LIVE.value
    currency = payment_module.CURRENCY_CODE.value
    inst_id = payment_module.INSTID.value
    default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if live:
        post_url = payment_module.CONNECTION.value
    else:
        post_url = payment_module.CONNECTION_TEST.value

    if payment_module.MD5.value > "":
        # Doing the MD5 Signature dance
        # Generating secret "secret:amount:currency:cartId"
        signature = "%s:%s:%s:%s" % (payment_module.MD5.value, order.balance, currency, order.id)
        MD5 = md5.new(signature).hexdigest()
    else:
        MD5 = False
        
    ctx = RequestContext(request, {
        'order': order,
        'inst_id': inst_id,
        'currency': currency,
        'post_url': post_url,
        'default_view_tax': default_view_tax,
        'PAYMENT_LIVE' : live,
        'MD5' : MD5,
        'session' : request.session.session_key
    })
    return render_to_response(template, ctx)


def success(request):
    """
    The order has been succesfully processed.
    """
    
    session = SessionStore(session_key=request.POST['M_session'])
    request.session = session
    
    if request.POST['transStatus'] == 'Y':
        return generic_success(request)
    else:
        context = RequestContext(request,
            {'message': _('Your transaction was rejected.')})
        return render_to_response('shop_404.html', context)
    
