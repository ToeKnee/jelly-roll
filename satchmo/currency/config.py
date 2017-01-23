# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from satchmo.configuration import (
    ConfigurationGroup,
    StringValue,
    config_register,
)

CURRENCY_GROUP = ConfigurationGroup('CURRENCY', _('Currency Settings'), ordering=1)

CURRENCY = config_register(
    StringValue(
        CURRENCY_GROUP,
        'CURRENCY',
        description=_("Default currency symbol"),
        help_text=_("Use a '_' character to force a space."),
        default="$")
)
