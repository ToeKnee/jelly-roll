from satchmo.configuration import (
    BooleanValue,
    ConfigurationGroup,
    ModuleValue,
    StringValue,
    config_get,
    config_register_list,
)
from django.utils.translation import ugettext_lazy as _

PAYMENT_MODULES = config_get('PAYMENT', 'MODULES')
PAYMENT_MODULES.add_choice(('PAYMENT_INGENICO', _('Ingenico')))

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_INGENICO',
                                   _('Ingenico Payment Settings'),
                                   requires=PAYMENT_MODULES,
                                   ordering=101)

config_register_list(

    StringValue(PAYMENT_GROUP,
                'CONNECTION',
                description=_("URL to submit live transactions."),
                hidden=True,
                default='https://secure.ogone.com/ncol/prod/orderstandard_utf8.asp'),

    StringValue(PAYMENT_GROUP,
                'CONNECTION_TEST',
                description=_("URL to submit test transactions."),
                hidden=True,
                default='https://secure.ogone.com/ncol/test/orderstandard_utf8.asp'),

    StringValue(PAYMENT_GROUP,
                'PSPID',
                description=_('Your Ingenico affiliation name'),
                default=""),

    StringValue(PAYMENT_GROUP,
                'SECRET',
                description=_('Your Ingenico secret passphrase for transactions'),
                help_text=_('Uses SHA-512 to create the SHASIGN'),
                default=""),

    BooleanValue(PAYMENT_GROUP,
                 'LIVE',
                 description=_("Accept real payments"),
                 help_text=_("False if you want to be in test mode"),
                 default=False),

    ModuleValue(PAYMENT_GROUP,
                'MODULE',
                description=_('Implementation module'),
                hidden=True,
                default='satchmo.payment.modules.ingenico'),

    StringValue(PAYMENT_GROUP,
                'KEY',
                description=_("Module key"),
                hidden=True,
                default='INGENICO'),

    StringValue(PAYMENT_GROUP,
                'LABEL',
                description=_('English name for this group on the checkout screens'),
                default='Credit / Debit card (Ingenico)',
                help_text=_('This will be passed to the translation.')),

    StringValue(PAYMENT_GROUP,
                'URL_BASE',
                description=_('The url base used for constructing urlpatterns which will use this module'),
                default=r'^ingenico/'),

    BooleanValue(PAYMENT_GROUP,
                 'ALIAS',
                 description=_('Alias (Tokenisation) mode'),
                 help_text=_('Enable payment tokenisation (Alias Manager). If the alias exists, the cardholder name, masked credit card number (or account information) and expiry date will be initialised in the payment details page for validation.'),
                 default=False),

    StringValue(PAYMENT_GROUP,
                'ALIASUSAGE',
                description=_('Alias Usage'),
                help_text=_('A text explaining the reason for the Alias registration.'),
                default=_("Securely store your card details for faster checkout next time?")),
)
