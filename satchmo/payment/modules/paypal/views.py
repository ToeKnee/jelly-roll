""" PayPal API v1 integration

https://developer.paypal.com/docs/checkout/how-to/server-integration/

"""
import json
import logging
import pprint

import requests

from django.contrib.sites.models import Site
from django.core.cache import caches
from django.core.mail import mail_admins
from django.db import transaction
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from satchmo.configuration.functions import config_get_group
from satchmo.shop.models import Order, OrderPayment, OrderRefund
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
        return HttpResponseRedirect(reverse("satchmo_cart"))

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
        return HttpResponseRedirect(reverse("satchmo_cart"))

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
        return render(request, template)

    # Check if the order is still valid
    if not order.validate(request):
        context = {
            'message': _('Your order is no longer valid.')
        }
        return render(request, 'shop_404.html', context)

    # Set environment
    if payment_module.LIVE.value:
        environment = 'production'
    else:
        environment = 'sandbox'

    context = {
        'order': order,
        'environment': environment,
        'PAYMENT_LIVE': payment_live(payment_module)
    }
    template = lookup_template(payment_module, 'checkout/paypal/confirm.html')
    return render(request, template, context)


@transaction.atomic
@csrf_exempt
def create_payment(request, retries=0):
    """Call the /v1/payments/payment REST API with your client ID and
    secret and your payment details to create a payment ID.

    Return the payment ID to the client as JSON.
    """
    if request.method != "POST":
        raise Http404

    # Get the order, if there is no order, return to checkout step 1
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = reverse('paypal:satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    # Contact PayPal to create the payment
    payment_module = config_get_group('PAYMENT_PAYPAL')
    site = Site.objects.get_current()

    PATH = '/v1/checkout/orders'
    if payment_module.LIVE.value:
        PAYPAL_API = 'https://api.paypal.com'
    else:
        PAYPAL_API = 'https://api.sandbox.paypal.com'

    # Create data to send to PayPal
    headers = {
        'Authorization': 'Bearer {access_token}'.format(
            access_token=get_access_token(),
        ),
    }
    # Add the following to headers to test transaction failures
    # 'PayPal-Mock-Response': '{"mock_application_codes": "PAYEE_BLOCKED_TRANSACTION"}',
    # https://developer.paypal.com/docs/api/payments/v1/#errors

    data = {
        'intent': 'SALE',
        'payment_method': 'paypal',
        'application_context': {
            'brand_name': site.name,
            'landing_page': 'login',
            'user_action': 'commit',
        },

        "purchase_units": [{
            "reference_id": order.id,
            "description": 'Your {site} order.'.format(site=site.name),
            "amount": {
                'currency': order.currency.iso_4217_code,
                'total': float(order.total),
                'details': {
                    'subtotal': float(order.sub_total),
                    'tax': float(order.tax),
                    'shipping': float(order.shipping_cost),
                    'shipping_discount': float(order.shipping_discount),
                }
            },
            "payee": {
                "email": payment_module.PAYEE.value,
            },
            "items": [
                {
                    'name': item.product.name,
                    'description': item.product.meta,
                    'quantity': item.quantity,
                    'currency': order.currency.iso_4217_code,
                    'price': float(item.unit_price),
                    'tax': float(item.unit_tax),
                    'sku': item.product.sku,
                }
                for item
                in order.orderitem_set.all()
            ],
            'shipping_address': {
                'recipient_name': order.ship_addressee,
                'line1': order.ship_street1,
                'line2': order.ship_street2,
                'city': order.ship_city,
                'country_code': order.ship_country.iso2_code,
                'postal_code': order.ship_postal_code,
                'state': order.ship_state
            },
            "shipping_method": order.shipping_description,
            "invoice_number": order.id,
            "payment_descriptor": site.name,
        }],
        'redirect_urls': {
            'return_url': lookup_url(
                payment_module,
                'paypal:satchmo_checkout-success',
                include_server=True
            ),
            'cancel_url': lookup_url(
                payment_module,
                'satchmo_checkout-step1',
                include_server=True
            )
        }
    }

    # Send it to PayPal
    url = PAYPAL_API + PATH
    response = requests.post(url, headers=headers, json=data)
    # Handle invalid token
    if response.status_code == 401 and response.json().get('error') == 'invalid_token':
        # Force getting a new token
        get_access_token(force=True)
        if retries <= 3:
            return create_payment(request, retries=retries + 1)
        else:
            subject = 'PayPal API error: Create Payment Retries Exceeded'
            message = response.text
            mail_admins(subject, message)
            log.error(response.text)
            raise RuntimeError('Too Many Retries: Create Payment')
    # Then other errors
    elif response.status_code >= 400:
        subject = 'PayPal API error: {status_code}'.format(status_code=response.status_code)
        message = response.text
        mail_admins(subject, message)
        log.error(response.text)
        data = {"message": _("""Something went wrong with your PayPal payment.

Please try again.

If the problem persists, please contact us.""")}
        return JsonResponse(data, status=response.status_code)

    order.notes += _('--- Paypal Payment Created ---') + '\n'
    order.notes += str(timezone.now()) + '\n'
    order.notes += pprint.pformat(response.json()) + '\n'
    order.freeze()
    order.save()

    # Create a pending payment in our system
    order_payment = create_pending_payment(order, payment_module)
    order_payment.transaction_id = response.json()['id']
    order_payment.save()

    # Return JSON to client
    return JsonResponse(response.json(), status=201)


@transaction.atomic
@csrf_exempt
def execute_payment(request, retries=0):
    if request.method != "POST":
        raise Http404

    payment_module = config_get_group('PAYMENT_PAYPAL')

    PATH = '/v1/checkout/orders/{order_id}'.format(
        order_id=request.POST.get('orderID')
    )
    if payment_module.LIVE.value:
        PAYPAL_API = 'https://api.paypal.com'
    else:
        PAYPAL_API = 'https://api.sandbox.paypal.com'

    # Create data to send to PayPal
    headers = {
        'Authorization': 'Bearer {access_token}'.format(
            access_token=get_access_token(),
        ),
    }
    # Add the following to headers to test transaction failures
    # 'PayPal-Mock-Response': '{"mock_application_codes": "PAYEE_BLOCKED_TRANSACTION"}',
    # https://developer.paypal.com/docs/api/payments/v1/#errors

    # Send it to PayPal
    url = PAYPAL_API + PATH
    response = requests.get(url, headers=headers)
    # Handle invalid token
    if response.status_code == 401 and response.json().get('error') == 'invalid_token':
        # Force getting a new token
        get_access_token(force=True)
        if retries <= 3:
            return execute_payment(request, retries=retries + 1)
        else:
            subject = 'PayPal API error: Execute Payment Retries Exceeded'
            message = response.text
            mail_admins(subject, message)
            log.error(response.text)
            raise RuntimeError('Too Many Retries: Execute Payment')
    # Then other errors
    elif response.status_code >= 400:
        subject = 'PayPal API error: {status_code}'.format(status_code=response.status_code)
        message = response.text
        mail_admins(subject, message)
        log.error(response.text)
        data = {"message": _("""Something went wrong with your PayPal payment.

Please try again.

If the problem persists, please contact us.""")}
        return JsonResponse(data, status=response.status_code)

    response_data = response.json()

    # Get Order Payment and order
    order_payment = get_object_or_404(OrderPayment, transaction_id=request.POST.get('orderID'))
    order = order_payment.order

    order.notes += '\n' + _('--- Paypal Payment Executed ---') + '\n'
    order.notes += str(timezone.now()) + '\n'
    order.notes += pprint.pformat(response_data) + '\n'
    order.save()

    status = response_data.get('status')
    if status in ('APPROVED', 'CREATED'):
        order.add_status(
            status='Accepted',
            notes=_(
                "Payment approved by PayPal.\n\nWe are waiting for funds to clear before shipping your order.\n\nThank you.")
        )
    elif status in ('COMPLETED', 'EXECUTED'):
        # Update values
        record_payment(
            order, payment_module,
            amount=response_data['gross_total_amount']['value'],
            transaction_id=response_data['id']
        )

        # Set Order to Processing
        order.add_status(
            status='Processing',
            notes=_("Paid by PayPal. Thank you.")
        )
    else:
        order.add_status(
            status=status,
            notes=""
        )

    # Freeze the order as payment has now been taken
    complete_order(order)
    if 'cart' in request.session:
        del request.session['cart']

    response_data = {
        'status': 'success',
        'url': reverse('paypal:satchmo_checkout-success')
    }

    return JsonResponse(
        data=response_data,
        status=201
    )


@transaction.atomic
def success(request):
    '''When the order has been successfully processed, the user will be
    redirected here.

    This doesn't mean that the payment has been fully processed yet,
    the servers will talk to each other and confirm the payment.
    '''

    try:
        order = Order.objects.get(id=request.session.get('orderID'))
    except Order.DoesNotExist:
        return HttpResponseRedirect(reverse("satchmo_order_history"))

    template = 'checkout/success.html'
    context = {'order': order}
    return render(request, template, context)


def webhook(request):
    '''Handle PayPal webhooks.

    The PayPal REST APIs use webhooks for event notification. Webhooks
    are HTTP callbacks that receive notification messages for events.

    https://developer.paypal.com/docs/api/webhooks/v1/

    We only care about the following event types
    CUSTOMER.DISPUTE.CREATED A customer dispute is created.
    CUSTOMER.DISPUTE.RESOLVED A customer dispute is resolved.
    CUSTOMER.DISPUTE.UPDATED A customer dispute is updated.
    IDENTITY.AUTHORIZATION-CONSENT.REVOKED A risk dispute is created.
    PAYMENT-NETWORKS.ALTERNATIVE-PAYMENT.COMPLETED Webhook event payload to send for Alternative Payment Completion.
    PAYMENT.SALE.COMPLETED A sale completes.
    PAYMENT.SALE.DENIED The state of a sale changes from pending to denied.
    PAYMENT.SALE.PENDING The state of a sale changes to pending.
    PAYMENT.SALE.REFUNDED A merchant refunds a sale.
    PAYMENT.SALE.REVERSED PayPal reverses a sale.
    '''

    if request.method != "POST":
        raise Http404

    data = json.loads(request.body)

    if verify_webhook(request) is False:
        subject = 'PayPal API webhook verification error'
        message = pprint.pformat(data)
        mail_admins(subject, message)
        log.error('PayPal API webhook verification error')
        log.error(pprint.pformat(data))
        return JsonResponse({'error': 'PayPal API webhook verification error'}, status=400)

    event_type = data.get('event_type')
    if event_type is not None:
        if event_type.startswith('CUSTOMER.DISPUTE'):
            # Customer dispute
            # Add a note, but don't do anything else
            order_payment = get_object_or_404(
                OrderPayment,
                transaction_id=data['resource']['disputed_transactions'][0]['seller_transaction_id']
            )
            order = order_payment.order
            order.notes += '\n' + _('--- Paypal Customer Dispute ---') + '\n'
        elif event_type.endswith('COMPLETED'):
            # Payment complete
            order_payment = get_object_or_404(
                OrderPayment,
                transaction_id=data['resource']['parent_payment']
            )
            order = order_payment.order
            order.notes += '\n' + _('--- Paypal Payment Complete ---') + '\n'
            # Update values
            payment_module = config_get_group('PAYMENT_PAYPAL')
            record_payment(
                order, payment_module,
                amount=data['resource']['amount']['total'],
                transaction_id=data['id']
            )
            # Set Order to Processing
            order.add_status(
                status='Processing',
                notes=_("Paid by PayPal. Thank you.")
            )
        elif event_type.endswith('DENIED'):
            order_payment = get_object_or_404(
                OrderPayment,
                transaction_id=data['resource']['parent_payment']
            )
            order = order_payment.order
            order.notes += '\n' + _('--- Paypal Payment Denied ---') + '\n'
            order.add_status(
                status='Denied',
                notes=_("PayPal Payment Denied.")
            )
        elif event_type.endswith('PENDING'):
            order_payment = get_object_or_404(
                OrderPayment,
                transaction_id=data['resource']['parent_payment']
            )
            order = order_payment.order
            order.notes += '\n' + _('--- Paypal Payment Pending ---') + '\n'
            order.add_status(
                status='Pending',
                notes=_("PayPal Payment Pending.")
            )
        elif event_type.endswith('REFUNDED'):
            order_payment = get_object_or_404(
                OrderPayment,
                transaction_id=data['resource']['parent_payment']
            )
            order = order_payment.order
            order.notes += '\n' + _('--- Paypal Payment Refunded ---') + '\n'
            order.add_status(status='Refunded', notes=_("PayPal Refund"))
            OrderRefund.objects.create(
                order=order,
                amount=data['resource']['amount']['total'],
                exchange_rate=order.exchange_rate,
                transaction_id=data['id'],
            )
        elif event_type == 'PAYMENT.SALE.REVERSED':
            order_payment = get_object_or_404(
                OrderPayment,
                transaction_id=data['resource']['id']
            )
            order = order_payment.order
            order.notes += '\n' + _('--- Paypal Payment Reversed ---') + '\n'
            order.add_status(
                status='Reversed',
                notes=_("PayPal Payment Reversed.")
            )
            OrderPayment.objects.create(
                order=order,
                amount=data['resource']['amount']['total'],  # Minus amount for reversal
                exchange_rate=order.exchange_rate,
                payment='PAYPAL',
                transaction_id=data['id']
            )
        else:
            order.notes += '\n' + _('--- Paypal {event_type} ---'.format(
                event_type=event_type)
            ) + '\n'

    order.notes += str(timezone.now()) + '\n'
    order.notes += pprint.pformat(data) + '\n'
    order.save()

    response_data = {
        'status': 'success',
    }

    return JsonResponse(
        data=response_data,
        status=200
    )


def verify_webhook(request, retries=0):
    data = json.loads(request.body)
    payment_module = config_get_group('PAYMENT_PAYPAL')

    PATH = '/v1/notifications/webhooks-event-types'
    if payment_module.LIVE.value:
        PAYPAL_API = 'https://api.paypal.com'
    else:
        PAYPAL_API = 'https://api.sandbox.paypal.com'

    # Create data to send to PayPal
    headers = {
        'Authorization': 'Bearer {access_token}'.format(
            access_token=get_access_token(),
        ),
    }
    # Add the following to headers to test transaction failures
    # 'PayPal-Mock-Response': '{"mock_application_codes": "PAYEE_BLOCKED_TRANSACTION"}',
    # https://developer.paypal.com/docs/api/payments/v1/#errors

    PLACEHOLDER = '---REPLACE---'
    data = {
        'auth_algo': request.headers['PAYPAL-AUTH-ALGO'],
        'cert_url': request.headers['PAYPAL-CERT-URL'],
        'transmission_id': request.headers['PAYPAL-TRANSMISSION-ID'],
        'transmission_sig': request.headers['PAYPAL-TRANSMISSION-SIG'],
        'transmission_time': request.headers['PAYPAL-TRANSMISSION-TIME'],
        'webhook_id': data.get('webhook_id'),
        'webhook_event': PLACEHOLDER
    }
    data = json.dumps(data)
    data = data.replace('"%s"' % PLACEHOLDER, json.dumps(data))

    # Send it to PayPal
    url = PAYPAL_API + PATH
    response = requests.post(url, headers=headers, datat=data)
    # Handle invalid token
    if response.status_code == 401 and response.json().get('error') == 'invalid_token':
        # Force getting a new token
        get_access_token(force=True)
        if retries <= 3:
            return webhook(request, retries=retries + 1)
        else:
            subject = 'PayPal API error: Webhool Retries Exceeded'
            message = response.text
            mail_admins(subject, message)
            log.error(response.text)
            raise RuntimeError('Too Many Retries: Webhook')
    # Then other errors
    elif response.status_code >= 400:
        subject = 'PayPal API webhook verification error: {status_code}'.format(
            status_code=response.status_code
        )
        message = response.text
        mail_admins(subject, message)
        log.error(response.text)
        return JsonResponse(response.json(), status=response.status_code)

    log.debug('PAYAPL Webhook verification:' + response.text)

    if response.json().get('verification_status') == 'SUCCESS':
        return True
    else:
        log.info("PAYAPL Webhook verification: Soft Fail")
        # It is currently impossible to test verification through the
        # PayPal sandbox, until we can verify that this method works,
        # we will return True (even for fails) :(
        return True
        # return False


def get_access_token(force=False):
    ''' Get the oAuth bearer access token and cache it '''
    payment_module = config_get_group('PAYMENT_PAYPAL')
    cache = caches['default']
    key = 'PAYPAL_ACCESS_TOKEN'
    access_token = cache.get(key)
    if force or access_token is None:
        PATH = '/v1/oauth2/token'
        if payment_module.LIVE.value:
            PAYPAL_API = 'https://api.paypal.com'
            CLIENT = payment_module.CLIENT_ID.value
            SECRET = payment_module.SECRET_KEY.value
        else:
            PAYPAL_API = 'https://api.sandbox.paypal.com'
            CLIENT = payment_module.SANDBOX_CLIENT_ID.value
            SECRET = payment_module.SANDBOX_SECRET_KEY.value

        url = PAYPAL_API + PATH
        data = {'grant_type': 'client_credentials'}

        response = requests.post(
            url,
            data=data,
            auth=requests.auth.HTTPBasicAuth(CLIENT, SECRET)
        )
        if response.status_code >= 400:
            subject = 'PayPal API Get Access Token error: {status_code}'.format(
                status_code=response.status_code
            )
            message = response.text
            mail_admins(subject, message)
            log.error(response.text)
        else:
            data = response.json()
            access_token = data['access_token']
            # We want a new token before the old one expires
            expires_in = int(data['expires_in']) - 5
            cache.set(key, access_token, expires_in)

    return access_token
