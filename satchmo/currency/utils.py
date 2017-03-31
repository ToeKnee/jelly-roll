import math

from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

from satchmo.configuration import config_value
from .models import Currency, ExchangeRate


def money_format(value, currency_code):
    """Convert Decimal to a money formatted unicode string.
    """

    try:
        currency = Currency.objects.all().get(iso_4217_code=currency_code)
    except Currency.DoesNotExist:
        return _("{currency} is not accepted".format(currency=currency_code))

    return u"{currency_symbol}{value:.2f} ({code})".format(
        currency_symbol=currency.symbol,
        value=value,
        code=currency.iso_4217_code,
    )


def convert_to_currency(value, currency_code):
    """Convert a Decimal value using the current exchange rate for the supplied currency_code"""
    if value is None:
        return Decimal("0.00")

    currency = Currency.objects.get_primary()
    if currency_code is not None and currency_code != currency.iso_4217_code:
        try:
            currency = Currency.objects.accepted().get(iso_4217_code=currency_code)
        except Currency.DoesNotExist:
            pass

        try:
            exchange_rate = currency.exchange_rates.latest().rate
        except ExchangeRate.DoesNotExist:
            exchange_rate = Decimal("1.00")

        # Add a small buffer
        buffer = config_value('CURRENCY', 'BUFFER')
        value = value + buffer

        # Multiply by the exchange rate
        value = value * exchange_rate

        # Round up to the nearest whole unit of currency
        if config_value('CURRENCY', 'ROUND_UP'):
            if value % 1 > Decimal("0.5"):
                value = Decimal(math.ceil(value))
            else:
                value = Decimal(math.floor(value)) + Decimal("0.5")

    # Take away 1 minor unit of currency
    if config_value('CURRENCY', 'PSYCHOLOGICAL_PRICING') and value == math.ceil(value):
        value = value - Decimal("0.01")

    return value


def currency_for_request(request):
    """ Find the currency_code for the request """
    currency_code = None

    if request is not None:
        # Try to look up the currency code from the session
        currency_code = request.session.get("currency_code")

        # If not, try the profile
        if currency_code is None:
            try:
                currency_code = request.user.profile.currency_code
            except AttributeError:
                pass

    # If not, fall back to primary currency
    if currency_code is None:
        currency = Currency.objects.get_primary()
        currency_code = currency.iso_4217_code

    return currency_code
