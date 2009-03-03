from django.utils.translation import ugettext_lazy as _
from satchmo.shipping.config import SHIPPING_ACTIVE
from satchmo.configuration import *

import logging
log = logging.getLogger('tiered.config')

SHIPPING_ACTIVE.add_choice(('satchmo.shipping.modules.tieredweight', _('Tiered Weight')))

log.debug('loaded')