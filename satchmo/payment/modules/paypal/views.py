import logging
import urllib.request, urllib.error, urllib.parse

from django.core import urlresolvers
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import urlencode
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from sys import exc_info
from traceback import format_exception

from satchmo.configuration import config_get_group
from satchmo.configuration import config_value
from satchmo.shop.models import Order, OrderPayment
from satchmo.payment.utils import record_payment, create_pending_payment
from satchmo.payment.views import payship
from satchmo.payment.views.checkout import complete_order
from satchmo.payment.config import payment_live
from satchmo.shop.models import Cart
from satchmo.utils.dynamic import lookup_url, lookup_template

log = logging.getLogger(__name__)


def pay_ship_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))

    return payship.base_pay_ship_info(
        request,
        config_get_group('PAYMENT_PAYPAL'),
        payship.simple_pay_ship_process_form,
        'checkout/paypal/pay_ship.html'
    )


@transaction.atomic
def confirm_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(urlresolvers.reverse("satchmo_cart"))

    payment_module = config_get_group('PAYMENT_PAYPAL')

    # Get the order,
    # if there is no order, return to checkout step 1
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    # Check that the cart has items in it.
    if cart.numItems == 0:
        template = lookup_template(payment_module, 'checkout/empty_cart.html')
        return render_to_response(template, RequestContext(request))

    # Check if the order is still valid
    if not order.validate(request):
        context = RequestContext(
            request,
            {
                'message': _('Your order is no longer valid.')
            }
        )
        return render_to_response('shop_404.html', context)

    # Set URL and accounts based on whether the site is LIVE or not
    if payment_module.LIVE.value:
        log.debug("live order on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
        account = payment_module.BUSINESS.value
    else:
        url = payment_module.POST_TEST_URL.value
        account = payment_module.BUSINESS_TEST.value

    # Is there a custom return URL
    # Or will we use the default one?
    try:
        address = lookup_url(
            payment_module,
            payment_module.RETURN_ADDRESS.value,
            include_server=True
        )
    except urlresolvers.NoReverseMatch:
        address = payment_module.RETURN_ADDRESS.value

    # Create a pending payment
    create_pending_payment(order, payment_module)

    default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    recurring = None
    order_items = order.orderitem_set.all()
    for item in order_items:
        if item.product.is_subscription:
            recurring = {
                'product': item.product,
                'price': item.product.price_set.all()[0].price
            }
            trial0 = recurring['product'].subscriptionproduct.get_trial_terms(
                0
            )
            if len(order_items) > 1 or trial0 is not None or recurring['price'] < order.balance:
                recurring['trial1'] = {'price': order.balance}
                if trial0 is not None:
                    recurring['trial1']['expire_length'] = trial0.expire_length
                    recurring['trial1']['expire_unit'] = trial0.expire_unit[0]
                # else:
                #     recurring['trial1']['expire_length'] = recurring['product'].subscriptionproduct.get_trial_terms(0).expire_length
                trial1 = recurring['product'].subscriptionproduct.get_trial_terms(
                    1
                )
                if trial1 is not None:
                    recurring['trial2']['expire_length'] = trial1.expire_length
                    recurring['trial2']['expire_unit'] = trial1.expire_unit[0]
                    recurring['trial2']['price'] = trial1.price

    ctx = RequestContext(request, {
        'order': order,
        'post_url': url,
        'default_view_tax': default_view_tax,
        'business': account,
        'currency_code': order.currency.iso_4217_code,
        'return_address': address,
        'invoice': order.id,
        'subscription': recurring,
        'PAYMENT_LIVE': payment_live(payment_module)
    })

    template = lookup_template(payment_module, 'checkout/paypal/confirm.html')

    return render_to_response(template, ctx)


@csrf_exempt
@transaction.atomic
def ipn(request):
    """PayPal IPN (Instant Payment Notification)
    Cornfirms that payment has been completed and marks invoice as paid.
    Adapted from IPN cgi script provided at http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/456361"""

    payment_module = config_get_group('PAYMENT_PAYPAL')
    if payment_module.LIVE.value:
        log.debug("PayPal IPN: Live IPN on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
    else:
        log.debug("PayPal IPN: Test IPN on %s", payment_module.KEY.value)
        url = payment_module.POST_TEST_URL.value
    PP_URL = url

    try:
        data = request.POST
        log.debug("PayPal IPN: Data: " + repr(data))
        if not confirm_ipn_data(data, PP_URL):
            return HttpResponse()

        try:
            invoice = data['invoice']
        except KeyError:
            invoice = data['item_number']

        if 'payment_status' not in data or not data['payment_status'] == "Completed":
            # We want to respond to anything that isn't a payment - but we won't insert into our database.
            order = Order.objects.get(pk=invoice)
            if data['payment_status'] == "Pending":
                notes = "Pending Reason: %s" % (data['pending_reason'])
            else:
                notes = ""
            order.add_status(status=data['payment_status'], notes=(notes))
            log.info("PayPal IPN: Ignoring IPN data for non-completed payment.")
            return HttpResponse()

        gross = data['mc_gross']
        txn_id = data['txn_id']

        log.info("PayPal IPN: Set %s to Processing" % txn_id)
        if not OrderPayment.objects.filter(transaction_id=txn_id).count():
            # If the payment hasn't already been processed:
            order = Order.objects.get(pk=invoice)
            order.add_status(
                status='Processing',
                notes=_("Paid through PayPal.")
            )
            payment_module = config_get_group('PAYMENT_PAYPAL')
            record_payment(order, payment_module,
                           amount=gross, transaction_id=txn_id)
            complete_order(order)

            if 'memo' in data:
                if order.notes:
                    notes = order.notes + "\n"
                else:
                    notes = ""

                order.notes = notes + \
                    _('---Comment via Paypal IPN---') + '\n' + data['memo']
                log.debug("PayPal IPN: Saved order notes from Paypal")

            for item in order.orderitem_set.select_for_update().filter(
                    product__subscriptionproduct__recurring=True,
                    completed=False
            ):
                item.completed = True
                item.save()
            for cart in Cart.objects.select_for_update().filter(customer=order.contact):
                cart.empty()

            order.save()
    except:
        log.exception(''.join(format_exception(*exc_info())))

    return HttpResponse()


def confirm_ipn_data(data, PP_URL):
    # data is the form data that was submitted to the IPN URL.

    newparams = {}
    for key in list(data.keys()):
        newparams[key] = data[key]

    newparams['cmd'] = "_notify-validate"
    params = urlencode(newparams)

    req = urllib.request.Request(PP_URL)
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    fo = urllib.request.urlopen(req, params)

    ret = fo.read()
    if ret == "VERIFIED":
        log.info("PayPal IPN:  data verification was successful.")
    else:
        log.info("PayPal IPN: data verification failed.")
        log.info("PayPal IPN: %s" % ret)
        return False

    return True
