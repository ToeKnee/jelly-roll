# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from satchmo.configuration import (
    BooleanValue,
    ConfigurationGroup,
    DecimalValue,
    config_register_list,
)


CURRENCY_GROUP = ConfigurationGroup('CURRENCY', _('Currency Settings'), ordering=1)

CURRENCY = config_register_list(
    DecimalValue(
        CURRENCY_GROUP,
        'BUFFER',
        description=_("Exchange Rate Buffer"),
        help_text=_("Add a small buffer before calculating the exchange rate (to cover exchange fees etc.)"),
        default="0.20"),
    BooleanValue(
        CURRENCY_GROUP,
        'ROUND_UP',
        description=_("Round up"),
        help_text=_("Round currency exchanged prices up to the nearest whole unit"),
    ),
    BooleanValue(
        CURRENCY_GROUP,
        'PSYCHOLOGICAL_PRICING',
        description=_("Psychological pricing"),
        help_text=_("£1.00 would become £0.99. Applied after exchanged prices are rounded up"),
    ),
)
