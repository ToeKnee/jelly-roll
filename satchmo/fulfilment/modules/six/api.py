import json
import requests

from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext as _

from satchmo.configuration import config_value
from satchmo.product.models import Product
from satchmo.shop.models import Order
from satchmo.utils.urlhelper import external_url

import logging
logger = logging.getLogger(__name__)


def float_price(price):
    if price is None:
        price = 0
    return float(str(price))


def get_phone_number(order):
    if order.contact.primary_phone:
        phone = order.contact.primary_phone.phone
    else:
        phone = u""
    return phone


def order_payload(order):
    data = {}
    data["api_key"] = config_value("satchmo.fulfilment.modules.six", "API_KEY")
    data["test"] = config_value("satchmo.fulfilment.modules.six", "TEST_MODE")
    data["allow_preorder"] = config_value("satchmo.fulfilment.modules.six", "ALLOW_PREORDER")
    data["update_stock"] = config_value("satchmo.fulfilment.modules.six", "UPDATE_STOCK")
    data["order"] = {}

    despatch_url = external_url(reverse("six_despatch", kwargs={"order_id": order.id, "verification_hash": order.verification_hash}))

    data["order"]["client_ref"] = order.id
    data["order"]["po_number"] = order.id
    data["order"]["date_placed"] = unicode(order.time_stamp)
    data["order"]["callback_url"] = despatch_url
    data["order"]["postage_speed"] = order.shipping_postage_speed
    data["order"]["postage_cost"] = float_price(order.shipping_cost)
    data["order"]["total_amount"] = float_price(order.sub_total)
    data["order"]["signed_for"] = order.shipping_signed_for
    data["order"]["tracked"] = order.shipping_tracked
    data["order"]["ShippingContact"] = {
        "dear": order.contact.user.first_name,
        "name": order.ship_addressee,
        "email": order.contact.user.email,
        "phone": get_phone_number(order),
        "address": order.ship_street1,
        "address_contd": order.ship_street2,
        "city": order.ship_city,
        "county": order.ship_state,
        "country": unicode(order.ship_country),
        "postcode": order.ship_postal_code,
    }
    data["order"]["BillingContact"] = {
        "name": order.bill_addressee,
        "email": order.contact.user.email,
        "phone": get_phone_number(order),
        "address": order.bill_street1,
        "address_contd": order.bill_street2,
        "city": order.bill_city,
        "county": order.bill_state,
        "country": unicode(order.bill_country),
        "postcode": order.bill_postal_code,
    }
    data["order"]["items"] = [
        {
            "client_ref": item.product.slug,
            "quantity": item.quantity,
            "price": float_price(item.unit_price),

        }
        for item in order.orderitem_set.all()
    ]

    return json.dumps(data)


@transaction.atomic
def send_order(order):
    url = config_value("satchmo.fulfilment.modules.six", "URL")
    payload = order_payload(order)
    headers = {'content-type': 'application/json'}

    try:
        response = requests.post(url, data=payload, headers=headers)
    except requests.exceptions.RequestException as e:
        logger.exception(e)
    else:
        try:
            payload = response.json()
        except ValueError as e:
            logger.exception(e)
        else:
            logger.debug(payload)

            if payload["order_ref"] != order.id:
                logger.warning("Order id has changed.  Expecting %s, got %s.  Processing anyway.", order.id, payload["order_ref"])
                order = Order.objects.get(id=order.id)

            # Ensure that notes is a string, even when empty.
            if order.notes is None:
                order.notes = u""
            else:
                order.notes += u"\n\n------------------ {now} ------------------\n\n".format(
                    now=timezone.now()
                )

            if "client_area_link" in payload:
                order.notes += u"Client area: {url}\n".format(
                    url=payload["client_area_link"],
                )

            if payload["success"]:
                order.fulfilled = True
                order.save()
                order.add_status(
                    status=_("Pick & Pack"),
                    notes=_("Your order has been passed to the warehouse and is awaiting picking.")
                )
                logger.info("Successfully processed order #%s", order.id)
            else:
                logger.warning("Order #%s failed. %s", order.id, payload["error"])
                order.notes += "{error}\n".format(
                    error=payload["error"],
                )
                order.notes += u"Valid: {valid}\n".format(
                    valid=payload["valid"]
                )
                order.save()
                order.add_status(
                    status=_("Error"),
                    notes=_("Something went wrong with your order.  We are taking a look at it and will update you when we have resolved the issue.")
                )

            if payload.get("update_stock"):
                logger.info("Updating stock")
                for slug, stock in payload["stock_changes"].items():
                    try:
                        product = Product.objects.get(slug=slug)
                    except Product.DoesNotExist:
                        logger.warning("Could not find a product with slug %s.  Six truncates slugs to 32 characters.  Trying to find a product that starts with %s", slug, slug)
                        # Six truncates long slugs (32 characters) Try
                        # and look-up one that matches.  If more than
                        # one match, log an error.
                        try:
                            product = Product.objects.get(slug__startswith=slug)
                        except MultipleObjectsReturned:
                            logger.error("Could not find a product with slug %s", slug)
                            product = None

                    if product and product.items_in_stock != stock:
                        logger.warning("%s: Stock was %s, now %s", product, product.items_in_stock, stock)
                        product.items_in_stock = stock
                        product.save()
