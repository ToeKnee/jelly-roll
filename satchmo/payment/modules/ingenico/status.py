""" Ingenico Transaction Status

https://payment-services.ingenico.com/int/en/ogone/support/guides/user%20guides/statuses-and-errors
"""

from django.utils.translation import ugettext as _

TRANSACTION_STATUS = {
    0: {
        "NAME": _("Invalid or incomplete"),
        "DESCRIPTION": _(
            "At least one of the payment data fields is invalid or missing. The NCERROR and NCERRORPLUS fields give an explanation of the error."
        ),
        "NCERROR": 500,
        "NCSTATUS": 5,
    },
    1: {
        "NAME": _("Cancelled by customer"),
        "DESCRIPTION": _("The customer has cancelled the transaction."),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    2: {
        "NAME": _("Authorisation refused"),
        "DESCRIPTION": _(
            "The authorisation has been refused by the financial institution. The customer can retry the authorisation process after selecting another card or another payment method."
        ),
        "NCERROR": 300,
        "NCSTATUS": 3,
    },
    4: {
        "NAME": _("Order stored"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    40: {
        "NAME": _("Stored waiting external result"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    41: {
        "NAME": _("Waiting for client payment"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    46: {
        "NAME": _("Waiting authentication"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    5: {
        "NAME": _("Authorised"),
        "DESCRIPTION": _(
            """The authorisation has been accepted.

An authorisation code is available in the "ACCEPTANCE" field.
The status will be 5 if you have defined "Authorisation" as the default operation code in the "Global transaction parameters" tab, in the "Default operation code" section of the Technical information page in your account."""
        ),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    50: {
        "NAME": _("Authorised waiting external result"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    51: {
        "NAME": _("Authorisation waiting"),
        "DESCRIPTION": _(
            """The authorisation will be processed offline.

This is the standard response if you have selected offline processing in your account configuration.

The status will be 51 in two events:

    You have defined "Always offline (Scheduled)" as payment processing in the "Global transaction parameters" tab, "Processing for individual transactions" section of the Technical Information page in your account.
    When the online acquiring system is unavailable and you have defined "Online but switch to offline in intervals when the online acquiring system is unavailable" as payment processing in the "Global transaction parameters" tab, "Processing for individual transactions" section of the Technical Information page in your account.

You don't have to take any action when status 51 applies."""
        ),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    52: {
        "NAME": _("Authorisation not known"),
        "DESCRIPTION": _(
            """A technical problem arose during the authorisation/payment process, giving an unpredictable result.

The merchant can contact the acquirer helpdesk to know the exact status of the payment or can wait until we have updated the status in our system.
The customer should not retry the authorisation process since the authorisation/payment might already have been accepted."""
        ),
        "NCERROR": 200,
        "NCSTATUS": 2,
    },
    55: {"NAME": _("Standby"), "DESCRIPTION": _(""), "NCERROR": None, "NCSTATUS": None},
    56: {
        "NAME": _("Ok with scheduled payments"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    57: {
        "NAME": _("Not OK with scheduled payments"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    59: {
        "NAME": _("Authorisation to be requested manually"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    6: {
        "NAME": _("Authorised and cancelled"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    61: {
        "NAME": _("Author. deletion waiting"),
        "DESCRIPTION": _("The authorisation deletion will be processed offline."),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    62: {
        "NAME": _("Author. deletion uncertain"),
        "DESCRIPTION": _(
            """A technical problem arose during the authorisation deletion process, giving an unpredictable result.

The merchant can contact the acquirer helpdesk to establish the precise status of the payment or wait until we have updated the status in our system."""
        ),
        "NCERROR": 200,
        "NCSTATUS": 2,
    },
    63: {
        "NAME": _("Author. deletion refused"),
        "DESCRIPTION": _("A technical problem arose."),
        "NCERROR": 300,
        "NCSTATUS": 3,
    },
    64: {
        "NAME": _("Authorised and cancelled"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    7: {
        "NAME": _("Payment deleted"),
        "DESCRIPTION": _("The payment has been cancelled/deleted"),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    71: {
        "NAME": _("Payment deletion pending"),
        "DESCRIPTION": _("Waiting for payment cancellation/deletion"),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    72: {
        "NAME": _("Payment deletion uncertain"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    73: {
        "NAME": _("Payment deletion refused"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    74: {
        "NAME": _("Payment deleted"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    8: {
        "NAME": _("Refund"),
        "DESCRIPTION": _("The payment has been refunded"),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    81: {
        "NAME": _("Refund pending"),
        "DESCRIPTION": _("Waiting for refund of the payment"),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    82: {
        "NAME": _("Refund uncertain"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    83: {
        "NAME": _("Refund refused"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    84: {"NAME": _("Refund"), "DESCRIPTION": _(""), "NCERROR": None, "NCSTATUS": None},
    85: {
        "NAME": _("Refund handled by merchant"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    9: {
        "NAME": _("Payment requested"),
        "DESCRIPTION": _(
            """The payment has been accepted.

An authorisation code is available in the field "ACCEPTANCE".

The initial status of a transaction will be 9 if you have defined "Sale" as the default operation code in the "Global transaction parameters" tab, "Default operation code" section of the Technical information page in your account."""
        ),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    91: {
        "NAME": _("Payment processing"),
        "DESCRIPTION": _("The data capture will be processed offline."),
        "NCERROR": 0,
        "NCSTATUS": 0,
    },
    92: {
        "NAME": _("Payment uncertain"),
        "DESCRIPTION": _(
            """A technical problem arose during the authorisation/payment process, giving an unpredictable result.

The merchant can contact the acquirer helpdesk to know the exact status of the payment or can wait until we have updated the status in our system.
The customer should not retry the authorisation process since the authorisation/payment might already have been accepted."""
        ),
        "NCERROR": 200,
        "NCSTATUS": 2,
    },
    93: {
        "NAME": _("Payment refused"),
        "DESCRIPTION": _("A technical problem arose"),
        "NCERROR": 300,
        "NCSTATUS": 3,
    },
    94: {
        "NAME": _("Refund declined by the acquirer"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    95: {
        "NAME": _("Payment handled by merchant"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    96: {
        "NAME": _("Refund reversed"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
    99: {
        "NAME": _("Being processed"),
        "DESCRIPTION": _(""),
        "NCERROR": None,
        "NCSTATUS": None,
    },
}
