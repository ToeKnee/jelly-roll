from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from hashlib import md5
from satchmo.configuration import config_get_group
from satchmo.configuration import config_value
from satchmo.payment.views import payship
from satchmo.payment.views.checkout import success as generic_success
from satchmo.payment.utils import record_payment
from satchmo.shop.models import Cart
from satchmo.shop.models import Order
from satchmo.utils.dynamic import lookup_template
from satchmo.utils import trunc_decimal
from django.core import urlresolvers
from django.http import HttpResponseRedirect

payment_module = config_get_group('PAYMENT_WORLDPAY')

def pay_ship_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))

    return payship.simple_pay_ship_info(request, payment_module, template='checkout/worldpay/pay_ship.html')

def confirm_info(request):
    "Create form to send to WorldPay"
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))
    
    try:
        order = Order.objects.from_request(request)
        if order.status:
            del request.session['orderID']
            raise Order.DoesNotExist
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
        # Generating secret "secret;amount;currency;cartId"
        balance = trunc_decimal(order.balance, 2)
        signature = "%s:%s:%s:%s" % (payment_module.MD5.value, balance, currency, order.id)
        MD5 = md5(signature).hexdigest()
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

@csrf_exempt
def success(request):
    """
    The order has been succesfully processed.
    """

    session = SessionStore(session_key = request.POST['M_session'])
    transaction_id = request.POST['cartId']
    amount = request.POST['authAmount']
    request.session = session
    
    if request.POST['transStatus'] == 'Y':
        order = Order.objects.get(pk=transaction_id)
        order.add_status(status='Processing', notes=_("Paid through WorldPay."))
        record_payment(order, payment_module, amount=amount, transaction_id=transaction_id)
        for cart in Cart.objects.filter(customer=order.contact):
            cart.empty()
        return generic_success(request, template='checkout/worldpay/success.html')
    else:
        context = RequestContext(request,
            {'message': _('Your transaction was rejected.')})
        return render_to_response('shop_404.html', context)
    
