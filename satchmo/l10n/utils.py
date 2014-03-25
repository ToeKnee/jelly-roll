import locale
import logging
from decimal import Decimal

log = logging.getLogger(__name__)


def money_format(value, grouping=True):
    """
    Convert Decimal to a money formatted unicode string.
    """
    if value is None:
        value = Decimal("0.00")
    return locale.currency(value, grouping=grouping).decode("utf-8")
