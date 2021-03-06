####################################################################
# Last step in the order process - confirm the info and process it
#####################################################################

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

from satchmo.configuration.functions import config_value
from satchmo.shop.models import Order
from satchmo.payment.config import payment_live
from satchmo.utils.dynamic import lookup_url, lookup_template
from satchmo.shop.models import Cart
from satchmo.payment import signals

import logging

log = logging.getLogger(__name__)


class ConfirmController(object):
    """Centralizes and manages data used by the confirm views.

    Generally, this is used by initializing, then calling
    `confirm`.  If defaults need to be overridden, such as
    by setting different templates, or by overriding `viewTax`,
    then do that before calling `confirm`.
    """

    def __init__(self, request, payment_module):
        self.request = request
        self.paymentModule = payment_module
        processor_module = payment_module.MODULE.load_module("processor")
        self.processor = processor_module.PaymentProcessor(self.paymentModule)
        self.viewTax = config_value("TAX", "DEFAULT_VIEW_TAX")
        self.order = None
        self.cart = None
        self.extra_context = {}

        # To override the form_handler, set this
        # otherwise it will use the built-in `_onForm`
        self.onForm = self._onForm

        # To override the success method, set this
        # othewise it will use the built-in `_onSuccess`
        self.onSuccess = self._onSuccess

        # False on any "can not continue" error
        self.valid = False

        # The value to be returned from the view
        # an HttpResponse or a HttpRedirect
        self.response = None

        self.processorMessage = ""
        self.processorReasonCode = ""
        self.processorResults = None

        self.templates = {
            "CONFIRM": "checkout/confirm.html",
            "EMPTY_CART": "checkout/empty_cart",
            "404": "shop_404.html",
        }

    def confirm(self):
        """Handles confirming an order and processing the charges.

        If this is a POST, then tries to charge the order using the `payment_module`.`processor`
        On success, sets `response` to the result of the `success_handler`, returns True
        On failure, sets `response` to the result, the result of the `form_handler`, returns False

        If not a POST, sets `response` to the result, the result of the `form_handler`, returns True
        """
        if not self.sanity_check():
            return False

        status = False

        if self.request.method == "POST":
            self.processor.prepareData(self.order)

            if self.process():
                self.response = self.onSuccess(self)
                return True

        else:
            # not a post, so still a success
            status = True

        self.response = self.onForm(self)
        return status

    def invalidate(self, dest):
        """Mark the confirmation invalid, and set the response"""
        self.valid = False
        self.response = dest

    def lookup_template(self, key):
        """Shortcut method to the the proper template from the `paymentModule`"""
        return lookup_template(self.paymentModule, self.templates[key])

    def lookup_url(self, view):
        """Shortcut method to the the proper url from the `paymentModule`"""
        return lookup_url(self.paymentModule, view)

    def _onForm(self, controller):
        """Show the confirmation page for the order.  Looks up the proper template for the
        payment_module.
        """
        template = controller.lookup_template("CONFIRM")
        controller.order.recalculate_total()

        context = {
            "PAYMENT_LIVE": payment_live(controller.paymentModule),
            "default_view_tax": controller.viewTax,
            "order": controller.order,
            "errors": controller.processorMessage,
            "checkout_step2": controller.lookup_url("satchmo_checkout-step2"),
        }
        if controller.extra_context:
            context.update(controller.extra_context)

        return render(request, template, context)

    def _onSuccess(self, controller):
        """Handles a success in payment.  If the order is paid-off, sends success, else return page to pay remaining."""
        if controller.order.paid_in_full:
            controller.cart.empty()
            for item in controller.order.orderitem_set.all():
                if item.product.is_subscription:
                    item.completed = True
                    item.save()
            if not controller.order.status:
                controller.order.add_status(
                    status="Pending", notes="Order successfully submitted"
                )

            # Redirect to the success page
            url = controller.lookup_url("satchmo_checkout-success")
            return HttpResponseRedirect(url)

        else:
            log.debug(
                "Order #%i not paid in full, sending to pay rest of balance",
                controller.order.id,
            )
            url = controller.order.get_balance_remaining_url()
            return HttpResponseRedirect(url)

    def process(self):
        """Process a prepared payment"""
        self.processorResults, self.processorReasonCode, self.processorMessage = (
            self.processor.process()
        )

        log.info(
            """Processing %s transaction with %s
        Order %i
        Results=%s
        Response=%s
        Reason=%s""",
            self.paymentModule.LABEL.value,
            self.paymentModule.KEY.value,
            self.order.id,
            self.processorResults,
            self.processorReasonCode,
            self.processorMessage,
        )
        return self.processorResults

    def sanity_check(self):
        """Ensure we have a valid cart and order."""
        try:
            self.order = Order.objects.from_request(self.request)

        except Order.DoesNotExist:
            url = reverse("satchmo_checkout-step1")
            self.invalidate(HttpResponseRedirect(url))
            return False

        try:
            self.cart = Cart.objects.from_request(self.request)
            if self.cart.numItems == 0 and not self.order.is_partially_paid:
                template = self.lookup_template("EMPTY_CART")
                self.invalidate(render(request, template))
                return False

        except Cart.DoesNotExist:
            template = self.lookup_template("EMPTY_CART")
            self.invalidate(render(request, template))
            return False

        # Check if the order is still valid
        if not self.order.validate(self.request):
            context = {"message": _("Your order is no longer valid.")}
            self.invalidate(render(request, self.templates["404"], context))

        self.valid = True
        signals.confirm_sanity_check.send(self, controller=self)
        return True


def credit_confirm_info(request, payment_module, template=None):
    """A view which shows and requires credit card selection.
    This is the simplest confirmation flow, with no overrides."""

    controller = ConfirmController(request, payment_module)
    if template:
        controller.templates["CONFIRM"] = template
    controller.confirm()
    return controller.response
