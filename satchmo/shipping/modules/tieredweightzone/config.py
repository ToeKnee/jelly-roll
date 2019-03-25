from django.utils.translation import ugettext_lazy as _
from satchmo.shipping.config import SHIPPING_ACTIVE


import logging

logger = logging.getLogger(__name__)

SHIPPING_ACTIVE.add_choice(
    ("satchmo.shipping.modules.tieredweightzone", _("Tiered Weight Zone"))
)

logger.debug("Loaded tieredweightzone")
