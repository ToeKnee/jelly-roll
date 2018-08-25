from satchmo.configuration.functions import (
    config_get,
    config_register_list,
)
from satchmo.configuration.values import (
    BooleanValue,
    ConfigurationGroup,
    ModuleValue,
    StringValue,
)
from django.utils.translation import ugettext_lazy as _

PAYMENT_MODULES = config_get('PAYMENT', 'MODULES')
PAYMENT_MODULES.add_choice(('PAYMENT_PAYPAL', _('Paypal Payment Settings')))

PAYMENT_GROUP = ConfigurationGroup(
    'PAYMENT_PAYPAL',
    _('Paypal Payment Settings'),
    requires=PAYMENT_MODULES,
    ordering=101
)

config_register_list(
    BooleanValue(
        PAYMENT_GROUP,
        'LIVE',
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode"),
        default=False
    ),
    StringValue(
        PAYMENT_GROUP,
        'WEBHOOK_ID',
        description=_("Live Webhook ID"),
        default='xxx'
    ),
    StringValue(
        PAYMENT_GROUP,
        'SANDBOX_WEBHOOK_ID',
        description=_("Sandbox Webhook ID"),
        default='xxx',
        help_text=_("This is used for asynchronous callbacks")
    ),
    StringValue(
        PAYMENT_GROUP,
        'SECRET_KEY',
        description=_("Live Secret key"),
        default='xxx'
    ),
    StringValue(
        PAYMENT_GROUP,
        'CLIENT_ID',
        description=_("Live Client ID"),
        default='xxx'
    ),
    StringValue(
        PAYMENT_GROUP,
        'SANDBOX_SECRET_KEY',
        description=_("Sandbox Secret key"),
        default='xxx'
    ),
    StringValue(
        PAYMENT_GROUP,
        'SANDBOX_CLIENT_ID',
        description=_("Sandbox Client ID"),
        default='xxx'
    ),
    StringValue(
        PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default='PayPal',
        help_text=_('This will be passed to the translation utility')
    ),

    ModuleValue(
        PAYMENT_GROUP,
        'MODULE',
        description=_('Implementation module'),
        hidden=True,
        default='satchmo.payment.modules.paypal'
    ),
    StringValue(
        PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default='PAYPAL'
    ),
    StringValue(
        PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default='paypal/',
        hidden=True,
    )
)
