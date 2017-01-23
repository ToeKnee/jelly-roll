from decimal import Decimal
from satchmo.configuration import config_value


def money_format(value, grouping=True):
    """Convert Decimal to a money formatted unicode string."""
    if value is None:
        value = Decimal("0.00")
    currency_symbol = config_value("SHOP", "CURRENCY")
    return u"{currency_symbol}{value:.2f}".format(
        currency_symbol=currency_symbol,
        value=value,
    )
