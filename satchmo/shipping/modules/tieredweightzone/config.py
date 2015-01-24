from django.utils.translation import ugettext_lazy as _
from satchmo.shipping.config import SHIPPING_ACTIVE
from satchmo.configuration import *

import logging
log = logging.getLogger(__name__)

SHIPPING_ACTIVE.add_choice(('satchmo.shipping.modules.tieredweightzone', _('Tiered Weight Zone')))

log.debug('loaded')