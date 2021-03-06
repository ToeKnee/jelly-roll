from django.utils.translation import ugettext_lazy as _
from satchmo.configuration.functions import (
    config_get,
    config_get_group,
    config_register,
)

from satchmo.configuration.values import DecimalValue, BooleanValue


TAX_MODULE = config_get("TAX", "MODULE")
TAX_MODULE.add_choice(("satchmo.tax.modules.percent", _("Percent Tax")))
TAX_GROUP = config_get_group("TAX")

config_register(
    DecimalValue(
        TAX_GROUP,
        "PERCENT",
        description=_("Percent tax"),
        requires=TAX_MODULE,
        requiresvalue="satchmo.tax.modules.percent",
    )
)

config_register(
    BooleanValue(
        TAX_GROUP,
        "TAX_SHIPPING",
        description=_("Tax Shipping?"),
        requires=TAX_MODULE,
        requiresvalue="satchmo.tax.modules.percent",
        default=False,
    )
)
