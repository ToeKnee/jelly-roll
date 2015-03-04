import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from satchmo.shop.models import Order

import logging
logger = logging.getLogger(__name__)


def despatch(request, order_id, verification_hash):
    success = False
    order = get_object_or_404(Order, id=order_id)
    if order.verify_hash(verification_hash):
        logging.info(request.POST)
        if request.method == "POST":
            # Yay, let's update the order
            try:
                payload = json.loads(request.body)
            except ValueError as e:
                logger.exception(e)
            else:
                # Ensure that notes is a string, even when empty.
                if order.notes is None:
                    order.notes = u""
                else:
                    order.notes += u"\n\n"

                order.notes += u"------------------ {now} ------------------\n\n".format(
                    now=payload.get("date_despatched")
                )

                order.notes += u"Client area: {url}\n".format(
                    url=payload.get("client_area_link"),
                )
                order.notes += u"Postage Method: {method}\n".format(
                    method=payload.get("postage_method"),
                )
                order.notes += u"Boxed Weight: {weight}g\n".format(
                    weight=payload.get("boxed_weight"),
                )
                order.notes += u"\nItems: {items}\n".format(
                    items=payload.get("items"),
                )

                # Store tracking information
                order.tracking_number = payload.get("tracking_number")
                order.tracking_url = payload.get("tracking_link")

                order.save()

                status_notes = u"Thanks for your order!\n"
                if order.tracking_number:
                    status_notes += u"Your tracking number is: {tracking_number}\n".format(
                        tracking_number=order.tracking_number,
                    )
                if order.tracking_url:
                    status_notes += u"You can track your order at {tracking_url}\n".format(
                        tracking_url=order.tracking_url,
                    )

                order.add_status(status="Shipped", notes=status_notes)
                success = True
        else:
            logging.error("Order (%s) hash (%s) does not verify", order_id, verification_hash)
    return JsonResponse({"success": success})
