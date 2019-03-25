# -*- coding: utf-8 -*-
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from satchmo.shop.models import Order

import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def despatch(request, order_id, verification_hash):
    success = False

    # Orders duplicated by Six has -a (or whatever letter) append to
    # the order_id.  Drop the -a.
    if isinstance(order_id, str) and "-" in order_id:
        logging.info("Trimming order id: %s", order_id)
        order_id = order_id.split("-")[0]

    order = get_object_or_404(Order, id=order_id)
    if order.verify_hash(verification_hash):
        logging.info(request.POST)
        if request.method == "POST":
            # Yay, let's update the order
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except ValueError as e:
                logger.exception(e)
            else:
                # Ensure that notes is a string, even when empty.
                if order.notes is None:
                    order.notes = ""
                else:
                    order.notes += "\n\n"

                order.notes += "------------------ {now} ------------------\n\n".format(
                    now=payload.get("date_despatched")
                )

                order.notes += "Client area: {url}\n".format(
                    url=payload.get("client_area_link")
                )
                order.notes += "Postage Method: {method}\n".format(
                    method=payload.get("postage_method")
                )
                order.notes += "Postage Cost: £{cost}\n".format(
                    cost=payload.get("postage_cost")
                )
                order.notes += "Boxed Weight: {weight}g\n".format(
                    weight=payload.get("boxed_weight")
                )
                order.notes += "\nItems: {items}\n".format(items=payload.get("items"))

                # Store tracking information
                order.tracking_number = payload.get("tracking_number")
                order.tracking_url = payload.get("tracking_link")

                order.save()

                status_notes = "Thanks for your order!\n"
                if order.tracking_url:
                    status_notes += "You can track your order at {tracking_url}\n".format(
                        tracking_url=order.tracking_url
                    )

                order.add_status(status="Shipped", notes=status_notes)
                success = True
        else:
            logging.error(
                "Order (%s) hash (%s) does not verify", order_id, verification_hash
            )
    return JsonResponse({"success": success})
