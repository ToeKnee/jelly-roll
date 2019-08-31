""" PayPal API v1 integration

https://developer.paypal.com/docs/checkout/how-to/server-integration/

"""
import json
import logging
import pprint

from decimal import Decimal

import paypalrestsdk
from paypalrestsdk.notifications import WebhookEvent

from django.contrib.sites.models import Site
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
from satchmo.payment.utils import create_pending_payment
from satchmo.payment.views import payship
from satchmo.payment.views.checkout import complete_order
from satchmo.payment.config import payment_live
from satchmo.shop.models import Cart
from satchmo.utils.dynamic import lookup_url, lookup_template

log = logging.getLogger(__name__)


def configure_api():
    """ Configure PayPal api """
    payment_module = config_get_group("PAYMENT_PAYPAL")
    if payment_module.LIVE.value:
        MODE = "live"
        CLIENT = payment_module.CLIENT_ID.value
        SECRET = payment_module.SECRET_KEY.value
    else:
        MODE = "sandbox"
        CLIENT = payment_module.SANDBOX_CLIENT_ID.value
        SECRET = payment_module.SANDBOX_SECRET_KEY.value

    paypalrestsdk.configure(
        {"mode": MODE, "client_id": CLIENT, "client_secret": SECRET}
    )


def pay_ship_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(reverse("satchmo_cart"))

    return payship.base_pay_ship_info(
        request,
        config_get_group("PAYMENT_PAYPAL"),
        payship.simple_pay_ship_process_form,
        "checkout/paypal/pay_ship.html",
    )


@transaction.atomic
def confirm_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(reverse("satchmo_cart"))

    payment_module = config_get_group("PAYMENT_PAYPAL")

    # Get the order,
    # if there is no order, return to checkout step 1
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, "satchmo_checkout-step1")
        return HttpResponseRedirect(url)

    # Check that the cart has items in it.
    if cart.numItems == 0:
        template = lookup_template(payment_module, "checkout/empty_cart.html")
        return render(request, template)

    # Check if the order is still valid
    if not order.validate(request):
        context = {"message": _("Your order is no longer valid.")}
        return render(request, "shop_404.html", context)

    # Set environment
    if payment_module.LIVE.value:
        environment = "production"
    else:
        environment = "sandbox"

    context = {
        "order": order,
        "environment": environment,
        "PAYMENT_LIVE": payment_live(payment_module),
    }
    template = lookup_template(payment_module, "checkout/paypal/confirm.html")
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
        raise Http404

    # Contact PayPal to create the payment
    configure_api()
    payment_module = config_get_group("PAYMENT_PAYPAL")
    site = Site.objects.get_current()

    data = {
        "intent": "order",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": lookup_url(
                payment_module, "paypal:satchmo_checkout-success", include_server=True
            ),
            "cancel_url": lookup_url(
                payment_module, "satchmo_checkout-step1", include_server=True
            ),
        },
        "transactions": [
            {
                "amount": {
                    "currency": order.currency.iso_4217_code,
                    "total": str(order.total),
                    "details": {
                        "subtotal": str(order.sub_total - order.discount),
                        "tax": str(order.tax),
                        "shipping": str(order.shipping_cost),
                        "shipping_discount": str(order.shipping_discount),
                    },
                },
                "description": "Your {site} order.".format(site=site.name),
                "invoice_number": str(order.id),
                "payment_options": {"allowed_payment_method": "UNRESTRICTED"},
                "item_list": {
                    "items": [
                        {
                            "name": item.product.name,
                            "description": item.product.meta,
                            "quantity": item.quantity,
                            "currency": order.currency.iso_4217_code,
                            "price": "{price:.2f}".format(
                                price=(item.unit_price - item.discount)
                            ),
                            "tax": str(item.unit_tax),
                            "sku": item.product.sku,
                        }
                        for item in order.orderitem_set.all()
                    ],
                    "shipping_address": {
                        "recipient_name": order.ship_addressee,
                        "line1": order.ship_street1,
                        "line2": order.ship_street2,
                        "city": order.ship_city,
                        "country_code": order.ship_country.iso2_code,
                        "postal_code": order.ship_postal_code,
                        "state": order.ship_state,
                    },
                    "shipping_method": order.shipping_description,
                },
            }
        ],
    }

    # Send it to PayPal
    payment = paypalrestsdk.Payment(data)

    if payment.create():
        order.notes += _("--- Paypal Payment Created ---") + "\n"
        order.notes += str(timezone.now()) + "\n"
        order.notes += pprint.pformat(payment.to_dict()) + "\n\n"
        order.freeze()
        order.save()
        # Create a pending payment in our system
        order_payment = create_pending_payment(order, payment_module)
        order_payment.transaction_id = payment["id"]
        order_payment.save()

        # Return JSON to client
        return JsonResponse(payment.to_dict(), status=201)

    else:
        subject = "PayPal API error"
        message = "\n".join(
            "{key}: {value}".format(key=key, value=value)
            for key, value in payment.error.items()
        )
        # Add the posted data
        message += "\n\n" + pprint.pformat(data) + "\n"

        mail_admins(subject, message)
        log.error(payment.error)
        log.error(pprint.pformat(data))
        if payment.error["name"] == "VALIDATION_ERROR":
            data = payment.error["details"]
        else:
            data = {
                "message": _(
                    """Something went wrong with your PayPal payment.

Please try again.

If the problem persists, please contact us."""
                )
            }
        # Because we are returning a list of dicts, we must mark it as unsafe
        return JsonResponse(data, status=400, safe=False)


@transaction.atomic
@csrf_exempt
def execute_payment(request, retries=0):
    if request.method != "POST":
        raise Http404
    configure_api()

    payment = paypalrestsdk.Payment.find(request.POST.get("paymentID"))
    if payment.execute({"payer_id": request.POST.get("payerID")}):
        # Get Order Payment and order
        order_payment = get_object_or_404(
            OrderPayment, transaction_id=request.POST.get("paymentID")
        )
        order = order_payment.order

        order.notes += "\n" + _("--- Paypal Payment Executed ---") + "\n"
        order.notes += str(timezone.now()) + "\n"
        order.notes += pprint.pformat(payment.to_dict()) + "\n"
        order.save()

        pp_order_id = payment.transactions[0].related_resources[0].order.id
        pp_order = paypalrestsdk.Order.find(pp_order_id)
        authorize = pp_order.authorize(
            {
                "amount": {
                    "currency": order.currency.iso_4217_code,
                    "total": str(order.total),
                }
            }
        )
        order.notes += "\n" + _("--- Paypal Payment Authorise ---") + "\n"
        order.notes += str(timezone.now()) + "\n"
        order.notes += str(authorize) + "\n"
        order.save()

        if pp_order.success():  # Hmm?
            capture = pp_order.capture(
                {
                    "amount": {
                        "currency": order.currency.iso_4217_code,
                        "total": str(order.total),
                    },
                    "is_final_capture": True,
                }
            )

            order.notes += "\n" + _("--- Paypal Payment Capture ---") + "\n"
            order.notes += str(timezone.now()) + "\n"
            order.notes += pprint.pformat(capture.to_dict()) + "\n"
            order.save()

            if capture.success():
                state = capture["state"]
                if state == "completed":
                    # Update order payment values
                    order_payment.amount = capture["amount"]["total"]
                    order_payment.transaction_id = payment["id"]
                    order_payment.save()

                    # Set Order to Processing
                    order.add_status(
                        status="Processing", notes=_("Paid by PayPal. Thank you.")
                    )
                elif state == "pending":
                    order.add_status(
                        status="Pending",
                        notes=_(
                            "Payment pending with PayPal.\n\nWe are waiting for funds to clear before shipping your order.\n\nThank you."
                        ),
                    )
                else:
                    order.add_status(status=state.capitalize(), notes="")

                # Freeze the order as payment has now been taken
                complete_order(order)
                if "cart" in request.session:
                    del request.session["cart"]

                response_data = {
                    "status": "success",
                    "url": reverse("paypal:satchmo_checkout-success"),
                }

                return JsonResponse(data=response_data, status=201)

            else:
                subject = "PayPal API Capture error"
                message = "\n".join(
                    "{key}: {value}".format(key=key, value=value)
                    for key, value in capture.error.items()
                )
                mail_admins(subject, message)
                log.error(message)
        else:
            subject = "PayPal API Order error"
            message = "\n".join(
                "{key}: {value}".format(key=key, value=value)
                for key, value in pp_order.error.items()
            )
            mail_admins(subject, message)
            log.error(message)
    else:
        subject = "PayPal API Payment error"
        message = "\n".join(
            "{key}: {value}".format(key=key, value=value)
            for key, value in payment.error.items()
        )
        mail_admins(subject, message)
        log.error(message)

    data = {
        "message": _(
            """Something went wrong with your PayPal payment.

Please try again.

If the problem persists, please contact us."""
        )
    }
    return JsonResponse(data, status=400)


@transaction.atomic
def success(request):
    """When the order has been successfully processed, the user will be
    redirected here.

    This doesn't mean that the payment has been fully processed yet,
    the servers will talk to each other and confirm the payment.
    """

    try:
        order = Order.objects.get(id=request.session.get("orderID"))
        del request.session["orderID"]
    except Order.DoesNotExist:
        return HttpResponseRedirect(reverse("satchmo_order_history"))

    template = "checkout/success.html"
    context = {"order": order}
    return render(request, template, context)


@transaction.atomic
@csrf_exempt
def webhook(request):
    """Handle PayPal webhooks.

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
    """
    if request.method != "POST":
        raise Http404

    data = json.loads(request.body.decode("utf-8"))

    payment_module = config_get_group("PAYMENT_PAYPAL")
    if payment_module.LIVE.value:
        webhook_id = payment_module.WEBHOOK_ID.value
    else:
        webhook_id = payment_module.SANDBOX_WEBHOOK_ID.value

    transmission_id = request.META["HTTP_PAYPAL_TRANSMISSION_ID"]
    timestamp = request.META["HTTP_PAYPAL_TRANSMISSION_TIME"]
    event_body = request.body.decode("utf-8")
    cert_url = request.META["HTTP_PAYPAL_CERT_URL"]
    actual_signature = request.META["HTTP_PAYPAL_TRANSMISSION_SIG"]
    auth_algo = request.META["HTTP_PAYPAL_AUTH_ALGO"]
    verified = WebhookEvent.verify(
        transmission_id,
        timestamp,
        webhook_id,
        event_body,
        cert_url,
        actual_signature,
        auth_algo,
    )

    if verified is False:
        subject = "PayPal API webhook verification error"
        message = pprint.pformat(data)
        mail_admins(subject, message)
        log.error("PayPal API webhook verification error")
        log.error(pprint.pformat(data))
        return JsonResponse(
            {"error": "PayPal API webhook verification error"}, status=400
        )

    event_type = data.get("event_type")
    if event_type is not None:
        if event_type.startswith("CUSTOMER.DISPUTE") or event_type.startswith(
            "RISK.DISPUTE"
        ):
            # Customer dispute
            # Add a note, but don't do anything else
            order_payment = get_object_or_404(
                OrderPayment,
                transaction_id=data["resource"]["disputed_transactions"][0][
                    "seller_transaction_id"
                ],
            )
            order = order_payment.order
            order.notes += "\n" + _("--- Paypal Customer Dispute ---") + "\n"
            order.add_status(
                status="Customer Dispute",
                notes=data["resource"]["messages"][0]["content"],
            )

        elif event_type == "PAYMENTS.PAYMENT.CREATED":
            try:
                order_id = data["resource"]["transactions"][0]["invoice_number"]
            except KeyError:
                response_data = {"status": "not found"}
                return JsonResponse(data=response_data, status=404)

            order = get_object_or_404(Order, id=order_id)
            # Set Order to Processing
            order.add_status(
                status="Payment Created", notes=_("PayPal payment created. Thank you.")
            )
        elif event_type.endswith("COMPLETED"):
            # Payment complete
            order = get_object_or_404(Order, id=data["resource"]["invoice_number"])
            if order.order_states.filter(status__status="Processing").exists() is False:
                order.notes += "\n" + _("--- Paypal Payment Complete ---") + "\n"
                # Update order payment values
                order_payment = get_object_or_404(
                    OrderPayment, transaction_id=data["resource"]["parent_payment"]
                )
                order_payment.amount = data["resource"]["amount"]["total"]
                order_payment.transaction_id = data["id"]
                order_payment.save()

                # Set Order to Processing
                order.add_status(
                    status="Processing", notes=_("Paid by PayPal. Thank you.")
                )
            else:
                log.info(
                    "Already processed {payment}".format(
                        payment=data["resource"]["parent_payment"]
                    )
                )
        elif event_type.endswith("DENIED"):
            order_payment = get_object_or_404(
                OrderPayment, transaction_id=data["resource"]["parent_payment"]
            )
            order = order_payment.order
            order.notes += "\n" + _("--- Paypal Payment Denied ---") + "\n"
            order.add_status(status="Denied", notes=_("PayPal Payment Denied."))
        elif event_type.endswith("PENDING"):
            order_payment = get_object_or_404(
                OrderPayment, transaction_id=data["resource"]["parent_payment"]
            )
            order = order_payment.order
            order.notes += "\n" + _("--- Paypal Payment Pending ---") + "\n"
            order.add_status(status="Pending", notes=_("PayPal Payment Pending."))
        elif event_type.endswith("REFUNDED"):
            order = get_object_or_404(Order, id=data["resource"]["invoice_number"])
            order.notes += "\n" + _("--- Paypal Payment Refunded ---") + "\n"
            order.add_status(status="Refunded", notes=_("PayPal Refund"))
            OrderRefund.objects.create(
                payment="PAYPAL",
                order=order,
                amount=Decimal(data["resource"]["amount"]["total"]),
                exchange_rate=order.exchange_rate,
                transaction_id=data["id"],
            )
        elif event_type == "PAYMENT.SALE.REVERSED":
            order_payment = get_object_or_404(
                OrderPayment, transaction_id=data["resource"]["id"]
            )
            order = order_payment.order
            order.notes += "\n" + _("--- Paypal Payment Reversed ---") + "\n"
            order.add_status(status="Reversed", notes=_("PayPal Payment Reversed."))
            OrderPayment.objects.create(
                order=order,
                amount=data["resource"]["amount"]["total"],  # Minus amount for reversal
                exchange_rate=order.exchange_rate,
                payment="PAYPAL",
                transaction_id=data["id"],
            )
        else:
            order_payment = get_object_or_404(
                OrderPayment, transaction_id=data["resource"]["parent_payment"]
            )
            order = order_payment.order
            order.notes += (
                "\n"
                + _("--- Paypal {event_type} ---".format(event_type=event_type))
                + "\n"
            )

    order.notes += str(timezone.now()) + "\n"
    order.notes += pprint.pformat(data) + "\n"
    order.save()

    response_data = {"status": "success"}

    return JsonResponse(data=response_data, status=201)
