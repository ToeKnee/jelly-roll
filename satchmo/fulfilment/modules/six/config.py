from django.utils.translation import ugettext_lazy as _

from satchmo.configuration import (
    ConfigurationGroup,
    config_register_list,
    StringValue,
    BooleanValue,
)
from satchmo.fulfilment.config import ACTIVE_FULILMENT_HOUSE

import logging
log = logging.getLogger(__name__)

ACTIVE_FULILMENT_HOUSE.add_choice(('satchmo.fulfilment.modules.six', _('Six')))

FULILMENT_HOUSE = ConfigurationGroup(
    'satchmo.fulfilment.modules.six',
    _('Six Fulfilment Settings'),
    requires=ACTIVE_FULILMENT_HOUSE,
    ordering=101
)

config_register_list(
    StringValue(
        FULILMENT_HOUSE,
        'API_KEY',
        description=_("API Key"),
        help_text=_("Client's API key, provided by fulfiller."),
        default=u""
    ),

    BooleanValue(
        FULILMENT_HOUSE,
        'TEST_MODE',
        description=_("Test mode"),
        help_text=_("Test identifier, must equal false for order to be processed."),
        default=True
    ),

    StringValue(
        FULILMENT_HOUSE,
        'URL',
        description=_("API URL"),
        help_text=_("URL of fulfillers API."),
        default=u"https://[client].sixworks.co.uk/api/1/"
    ),

    BooleanValue(
        FULILMENT_HOUSE,
        'UPDATE_STOCK',
        description=_("Update Stock"),
        help_text=_("Update stock based on the fulfilment houses stock levels."),
        default=True
    ),

    BooleanValue(
        FULILMENT_HOUSE,
        'ALLOW_PREORDER',
        description=_("Allow Preorder"),
        help_text=_("If true, permits acceptance of orders which contain lines currently out of stock. Disables Out-Of-Stock feedback in API response."),
        default=False
    ),
)
