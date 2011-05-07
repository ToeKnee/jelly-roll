import locale
import logging

locale.setlocale(locale.LC_ALL, '')

log = logging.getLogger('l10n.utils')

def money_format(value, grouping=True):
    """
    Convert Decimal to a money formatted string.
    """
    return locale.currency(value, grouping=grouping)
