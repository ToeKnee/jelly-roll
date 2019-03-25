# -*- encoding: utf-8 -*-
"""
Ingenico Payments

https://payment-services.ingenico.com/int/en/ogone/support/guides/integration%20guides/e-commerce/introduction

"""


import hashlib
from decimal import Decimal

from .forms import IngenicoForm
from .status import TRANSACTION_STATUS
from .utils import verify_shasign

from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from satchmo.configuration.functions import config_get_group
from satchmo.payment.models import HttpResponsePaymentRequired
from satchmo.payment.views import payship
from satchmo.payment.views.checkout import (
    complete_order,
    restock_order,
    success as generic_success,
)
from satchmo.payment.utils import record_payment
from satchmo.shop.models import Cart, Order, OrderRefund
from satchmo.shop.utils import HttpResponseMethodNotAllowed
from satchmo.utils.case_insensitive_dict import CaseInsensitiveReadOnlyDict
from satchmo.utils.dynamic import lookup_template

import logging

logger = logging.getLogger(__name__)

payment_module = config_get_group("PAYMENT_INGENICO")


def pay_ship_info(request):
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(reverse("satchmo_cart"))

    return payship.simple_pay_ship_info(
        request, payment_module, template="checkout/ingenico/pay_ship.html"
    )


def confirm_info(request):
    "Create form to send to Ingenico"
    # Check that items are in stock
    cart = Cart.objects.from_request(request)
    if cart.not_enough_stock():
        return HttpResponseRedirect(reverse("satchmo_cart"))

    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return HttpResponseRedirect(reverse("satchmo_shop_home"))

    if order.validate(request) is False:
        context = {"message": _("Your order is no longer valid.")}

        return render(request, "shop_404.html", context)

    data = {
        "PSPID": payment_module.PSPID.value,
        "ORDERID": order.id,
        # Amount * 100
        # https://payment-services.ingenico.com/int/en/ogone/support/guides/integration%20guides/e-commerce#formparameters
        "AMOUNT": int(order.balance * 100),
        "CURRENCY": order.currency.iso_4217_code,
        "CN": order.bill_addressee,
        "EMAIL": order.contact.user.email,
        "OWNERADDRESS": ", ".join([order.bill_street1, order.bill_street2]),
        "OWNERZIP": order.bill_postal_code,
        "OWNERTOWN": ", ".join([order.bill_city, order.bill_state]),
        "OWNERCTY": order.bill_country.iso2_code,
    }

    if payment_module.ALIAS.value:
        data["ALIAS"] = hashlib.sha512(
            order.contact.user.username.encode("utf-8")
        ).hexdigest()[:50]
        data["ALIASUSAGE"] = payment_module.ALIASUSAGE.value

    form = IngenicoForm(data)
    template = lookup_template(payment_module, "checkout/ingenico/confirm.html")

    live = payment_module.LIVE.value

    if live:
        post_url = payment_module.CONNECTION.value
    else:
        post_url = payment_module.CONNECTION_TEST.value

    ctx = {"form": form, "order": order, "post_url": post_url, "PAYMENT_LIVE": live}
    return render(request, template, ctx)


@transaction.atomic
def accepted(request):
    """When the order has been successfully accepted, the user will be
    redirected here.

    This doesn't mean that the payment has been fully processed yet,
    the servers will talk to each other and confirm the payment.

    """
    # Accept the payment (but don't mark it as "Processing" yet)
    order_id = request.session.get("orderID")
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        if "cart" in request.session:
            del request.session["cart"]

        if order_id:
            return HttpResponseRedirect(
                reverse("satchmo_order_tracking", kwargs={"order_id": order_id})
            )
        else:
            return HttpResponseRedirect(reverse("satchmo_shop_home"))
    else:
        order.add_status(status="Accepted", notes=_("Paid through Ingenico."))
        return generic_success(request)


def declined(request):
    """When the order has been declined, the user will be redirected
    here.

    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return HttpResponseRedirect(reverse("satchmo_shop_home"))

    order.add_status(status="Declined", notes="")
    order.freeze()
    order.save()

    context = {"order": order}
    return render(request, "checkout/ingenico/declined.html", context)


@transaction.atomic
@csrf_exempt
def process(request):
    """`Direct HTTP server-to-server request` processing.

    Details returned according to https://payment-services.ingenico.com/int/en/ogone/support/guides/integration%20guides/e-commerce/transaction-feedback#feedbackparameters
    These can be customised, but we will assume that these ones are available.

    ACCEPTANCE Acceptance code returned by the acquirer
    AMOUNT Order amount (not multiplied by 100)
    BRAND Card brand (our system derives this from the card number)
    CARDNO Masked card number
    CN Cardholder/customer name
    CURRENCY Order currency
    ED Expiry date
    NCERROR Error code
    orderID Your order reference
    PAYID Payment reference in our system
    PM Payment method
    SHASIGN SHA signature calculated by our system (if SHA-OUT configured)
    STATUS Transaction status (see Status overview)
    TRXDATE Transaction date
    """
    logger.debug("Process: %s", request.POST)
    post_data = CaseInsensitiveReadOnlyDict(request.POST)
    if request.method == "POST":
        shasign = post_data.get("SHASIGN")
        # Verify the Shasign
        if verify_shasign(shasign, post_data):
            try:
                order = Order.objects.get(id=post_data.get("orderID"))
            except Order.DoesNotExist:
                raise Http404()

            amount = Decimal(post_data.get("AMOUNT"))
            transaction_id = post_data.get("ACCEPTANCE")

            if order.notes is None:
                order.notes = ""
            order.notes += "\n------------------ {now} ------------------\n\n".format(
                now=timezone.now()
            )

            if "STATUS" in post_data:
                status = TRANSACTION_STATUS[int(post_data["STATUS"])]["NAME"]
            else:
                status = "Unknown"

            notes = """
Status: {status}
Transaction date: {transaction_date}
Transaction ID: {acceptance}
Ingenico ID: {ingenico_id}
Amount: {amount}
Currency: {currency}

NC Error: {nc_error}
Payment method: {pm}
Cardholder name: {cn}
Card no: {cardno}
Brand: {brand}
Expiry date: {ed}
            """.format(
                status=status,
                transaction_date=post_data.get("TRXDATE"),
                acceptance=transaction_id,
                ingenico_id=post_data.get("PAYID"),
                amount=post_data.get("amount"),
                currency=post_data.get("CURRENCY"),
                nc_error=post_data.get("NCERROR"),
                pm=post_data.get("PM"),
                cn=post_data.get("CN"),
                cardno=post_data.get("CARDNO"),
                brand=post_data.get("BRAND"),
                ed=post_data.get("ED"),
            )
            order.notes += notes
            order.save()

            # Ensure the status is ok before recording payment
            # https://payment-services.ingenico.com/int/en/ogone/support/guides/user%20guides/statuses-and-errors
            if "STATUS" in post_data:
                status = int(post_data["STATUS"])
                if status == 9:  # Payment requested, ok to send package
                    record_payment(
                        order,
                        payment_module,
                        amount=amount,
                        transaction_id=transaction_id,
                    )
                    complete_order(order)
                    order.add_status(status="Processing", notes=_("Payment complete."))
                elif status == 1:  # Cancelled by customer
                    if order.frozen is False:
                        order.freeze()
                    restock_order(order)
                    order.save()
                    order.add_status(status="Cancelled", notes=_(""))
                elif status == 7 or status == 8:  # Payment Deleted or Refunded
                    if order.frozen is False:
                        order.freeze()
                    order.save()
                    order.add_status(status="Refunded", notes=_(""))
                    OrderRefund.objects.create(
                        order=order,
                        amount=amount,
                        exchange_rate=order.exchange_rate,
                        transaction_id=transaction_id,
                    )
                elif status == 2:  # Authorisation refused
                    if order.frozen is False:
                        order.freeze()
                    restock_order(order)
                    order.save()
                    order.add_status(
                        status="Authorisation refused",
                        notes=_("Please contact your bank or card issuer."),
                    )
            return HttpResponse()
        else:
            logger.warning("Verification failed: %s", post_data)
            return HttpResponsePaymentRequired()
    else:
        return HttpResponseMethodNotAllowed()
