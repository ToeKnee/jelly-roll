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
    _('Paypal Payment Module Settings'),
    requires=PAYMENT_MODULES,
    ordering=101
)

config_register_list(
    StringValue(
        PAYMENT_GROUP,
        'POST_URL',
        description=_('Post URL'),
        help_text=_('The Paypal URL for real transaction posting.'),
        default="https://www.paypal.com/cgi-bin/webscr"
    ),

    StringValue(
        PAYMENT_GROUP,
        'POST_TEST_URL',
        description=_('Post URL'),
        help_text=_('The Paypal URL for test transaction posting.'),
        default="https://www.sandbox.paypal.com/cgi-bin/webscr"
    ),

    StringValue(
        PAYMENT_GROUP,
        'BUSINESS',
        description=_('Paypal account email'),
        help_text=_('The email address for your paypal account'),
        default=""
    ),

    StringValue(
        PAYMENT_GROUP,
        'BUSINESS_TEST',
        description=_('Paypal test account email'),
        help_text=_('The email address for testing your paypal account'),
        default=""
    ),

    StringValue(
        PAYMENT_GROUP,
        'RETURN_ADDRESS',
        description=_('Return URL'),
        help_text=_('Where Paypal will return the customer after the purchase is complete.  This can be a named url and defaults to the standard checkout success.'),
        default="PAYPAL_satchmo_checkout-success"
    ),

    BooleanValue(
        PAYMENT_GROUP,
        'SSL',
        description=_("Use SSL for the module checkout pages?"),
        default=False
    ),

    BooleanValue(
        PAYMENT_GROUP,
        'LIVE',
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode"),
        default=False
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
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default='PayPal',
        help_text=_('This will be passed to the translation utility')
    ),

    StringValue(
        PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default='paypal/'
    )
)
