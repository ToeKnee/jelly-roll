from satchmo.shop import signals
from satchmo.shop.listeners import veto_out_of_stock

import logging
log = logging.getLogger(__name__)

signals.satchmo_cart_add_verify.connect(veto_out_of_stock)

default_app_config = 'satchmo.shop.apps.ShopConfig'
