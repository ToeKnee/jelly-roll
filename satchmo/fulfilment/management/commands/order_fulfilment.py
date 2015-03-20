import importlib
from django.core.management.base import BaseCommand

from satchmo.configuration import config_value
from satchmo.shop.models import Order

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # args = ''
    help = 'Send orders to enabled fulfilment houses'

    def handle(self, *args, **options):
        for fulfilment_house in config_value("FULFILMENT", "MODULES"):
            logger.debug("Fulfilling with {house}".format(house=fulfilment_house))
            api_module = "{fulfilment_house}.api".format(
                fulfilment_house=fulfilment_house,
            )
            module = importlib.import_module(api_module)
            for order in Order.objects.unfulfilled().order_by("time_stamp"):
                if module.send_order(order):
                    logger.info(u'Order fulfilment processed "%s"' % order)
                else:
                    logger.warning(u'Order fulfilment not processed,  Something went wrong. "%s"' % order)
