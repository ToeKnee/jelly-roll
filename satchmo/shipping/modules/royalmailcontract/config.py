from django.utils.translation import ugettext_lazy as _
from satchmo.configuration import (
    config_get,
    config_register_list,
    ConfigurationGroup,
    DecimalValue,
    MultipleStringValue
)
from satchmo.l10n.models import Country

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('satchmo.shipping.modules.royalmailcontract', _('Royal Mail Contract')))

SHIPPING_GROUP = ConfigurationGroup('satchmo.shipping.modules.royalmailcontract',
                                    _('Royal Mail Contract Shipping Settings'),
                                    requires=SHIP_MODULES,
                                    ordering=101)


config_register_list(
    DecimalValue(SHIPPING_GROUP,
                 'PACKING_FEE',
                 description=_("Packing Fee"),
                 requires=SHIP_MODULES,
                 requiresvalue='satchmo.shipping.modules.royalmailcontract',
                 default="0.30"),

    DecimalValue(SHIPPING_GROUP,
                 'MAX_WEIGHT_PER_ITEM',
                 description=_("Max weight per item in Kgs (packet)"),
                 help_text=_("The orders weight is rounded up and divided by this and multiplied by the per item price"),
                 requires=SHIP_MODULES,
                 requiresvalue='satchmo.shipping.modules.royalmailcontract',
                 default="2.00"),

    DecimalValue(SHIPPING_GROUP,
                 'PER_RATE_EU',
                 description=_("Per item price E.U."),
                 requires=SHIP_MODULES,
                 requiresvalue='satchmo.shipping.modules.royalmailcontract',
                 default="1.09"),

    DecimalValue(SHIPPING_GROUP,
                 'PER_KG_EU',
                 description=_("Per Kg price E.U."),
                 requires=SHIP_MODULES,
                 requiresvalue='satchmo.shipping.modules.royalmailcontract',
                 default="4.33"),

    DecimalValue(SHIPPING_GROUP,
                 'PER_RATE_ROW',
                 description=_("Per item price R.o.W."),
                 requires=SHIP_MODULES,
                 requiresvalue='satchmo.shipping.modules.royalmailcontract',
                 default="1.14"),

    DecimalValue(SHIPPING_GROUP,
                 'PER_KG_ROW',
                 description=_("Per Kg price R.o.W."),
                 requires=SHIP_MODULES,
                 requiresvalue='satchmo.shipping.modules.royalmailcontract',
                 default="6.65"),

    MultipleStringValue(SHIPPING_GROUP,
                        'EXCLUDE_COUNTRY',
                        description=_("Countries excluded from Royal Mail Contract shipping."),
                        help_text=_("Select the countries that you want to exclude."),
                        default=[],
                        choices=[(c.iso2_code, c.printable_name) for c in Country.objects.exclude(iso2_code="GB")])
)
