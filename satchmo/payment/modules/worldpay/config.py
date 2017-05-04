from satchmo.configuration import (
    BooleanValue,
    ConfigurationGroup,
    ModuleValue,
    MultipleStringValue,
    StringValue,
    config_get,
    config_register_list,
)

from django.utils.translation import ugettext_lazy as _

_strings = (_('CreditCard'), _('Credit Card'))

PAYMENT_MODULES = config_get('PAYMENT', 'MODULES')
PAYMENT_MODULES.add_choice(('PAYMENT_WORLDPAY', _('Worldpay')))

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_WORLDPAY',
                                   _('Worldpay Payment Settings'),
                                   requires=PAYMENT_MODULES,
                                   ordering=101)

config_register_list(

    StringValue(PAYMENT_GROUP,
                'CONNECTION',
                description=_("URL to submit live transactions."),
                hidden=True,
                default='https://secure.worldpay.com/wcc/purchase'),

    StringValue(PAYMENT_GROUP,
                'CONNECTION_TEST',
                description=_("URL to submit test transactions."),
                hidden=True,
                default='https://secure-test.worldpay.com/wcc/purchase'),

    StringValue(PAYMENT_GROUP,
                'INSTID',
                description=_('Your Worldpay installation ID'),
                default=""),

    StringValue(PAYMENT_GROUP,
                'MD5',
                description=_('Your Worldpay MD5 secret for transactions'),
                help_text=_('Ensure that you set the SignatureFields to amount:currency:cartId'),
                default=""),

    StringValue(PAYMENT_GROUP,
                'CURRENCY_CODE',
                description=_('Currency Code'),
                help_text=_('Default Currency code for Worldpay transactions.'),
                default='GBP'),

    BooleanValue(PAYMENT_GROUP,
                 'SSL',
                 description=_("Use SSL for the checkout pages?"),
                 default=False),

    BooleanValue(PAYMENT_GROUP,
                 'LIVE',
                 description=_("Accept real payments"),
                 help_text=_("False if you want to be in test mode"),
                 default=False),

    ModuleValue(PAYMENT_GROUP,
                'MODULE',
                description=_('Implementation module'),
                hidden=True,
                default='satchmo.payment.modules.worldpay'),

    StringValue(PAYMENT_GROUP,
                'KEY',
                description=_("Module key"),
                hidden=True,
                default='WORLDPAY'),

    StringValue(PAYMENT_GROUP,
                'LABEL',
                description=_('English name for this group on the checkout screens'),
                default='Credit / Debit card (WorldPay)',
                help_text=_('This will be passed to the translation.')),

    StringValue(PAYMENT_GROUP,
                'URL_BASE',
                description=_('The url base used for constructing urlpatterns which will use this module'),
                default=r'^worldpay/'),

    MultipleStringValue(PAYMENT_GROUP,
                        'CREDITCHOICES',
                        description=_('Available credit cards'),
                        choices=(
                            (('Mastercard', 'Mastercard')),
                            (('Visa', 'Visa')),
                            (('Visa Electron', 'Visa Electron')),  # GBP - UK only
                            (('Solo', 'Solo')),  # GBP - UK only
                            (('JCB', 'JCB')),  # GBP - UK only
                            (('Maestro', 'Maestro')),  # GBP - UK only
                            (('Laser', 'Laser')),  # Euro - ROI only
                            (('American Express', 'American Express')),
                            (('Diners Club', 'Diners Club'))),
                        default=('Mastercard', 'Visa', 'Visa Electron', 'Solo', 'JCB', 'Maestro', 'Laser')
                        ),

    BooleanValue(PAYMENT_GROUP,
                 'EXTRA_LOGGING',
                 description=_("Verbose logs"),
                 help_text=_("Add extensive logs during post."),
                 default=False),
)
