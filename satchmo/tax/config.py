from django.utils.translation import ugettext_lazy as _
from satchmo.configuration.functions import config_register
from satchmo.configuration.values import ConfigurationGroup, StringValue, BooleanValue
from satchmo.utils import load_module
from satchmo.shop.satchmo_settings import get_satchmo_setting

import logging

logger = logging.getLogger(__name__)


TAX_GROUP = ConfigurationGroup("TAX", _("Tax Settings"))
TAX_MODULE = config_register(
    StringValue(
        TAX_GROUP,
        "MODULE",
        description=_("Active tax module"),
        help_text=_(
            "Select a module, save and reload to set any module-specific settings."
        ),
        default="satchmo.tax.modules.no",
        choices=[("satchmo.tax.modules.no", _("No Tax"))],
    )
)
DEFAULT_VIEW_TAX = config_register(
    BooleanValue(
        TAX_GROUP,
        "DEFAULT_VIEW_TAX",
        description=_("Show with tax included"),
        help_text=_(
            "If yes, then all products and the cart will display with tax included."
        ),
        default=False,
    )
)

# --- Load default tax modules.  Ignore import errors, user may have deleted them. ---
_default_modules = ("percent", "area")
for module in _default_modules:
    try:
        load_module("satchmo.tax.modules.%s.config" % module)
    except ImportError as ie:
        logger.debug(
            "Could not load default tax module configuration: %s\n%s", module, ie
        )


# --- Load any extra tax modules. ---
extra_tax = get_satchmo_setting("CUSTOM_TAX_MODULES")
for extra in extra_tax:
    try:
        load_module("%s.config" % extra)
    except ImportError:
        logger.warn("Could not load tax module configuration: %s" % extra)
