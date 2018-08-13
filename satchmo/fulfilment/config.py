from django.utils.translation import ugettext_lazy as _
from satchmo.configuration.functions import config_register
from satchmo.configuration.values import (
    ConfigurationGroup,
    MultipleStringValue,
)

import logging
log = logging.getLogger(__name__)

FULFILMENT_SETTINGS = ConfigurationGroup('FULFILMENT', _('Fulfilment Settings'))

ACTIVE_FULILMENT_HOUSE = config_register(
    MultipleStringValue(
        FULFILMENT_SETTINGS,
        'MODULES',
        description=_("Active fulfilment houses"),
        help_text=_(
            "Select the active fulfilment house, save and reload to set any module-specific fulilment settings."),
        default=[],
        choices=[]
    )
)
