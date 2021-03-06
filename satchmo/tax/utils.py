from satchmo.configuration.functions import config_value
from satchmo.utils import load_module

import decimal

TWOPLACES = decimal.Decimal("0.01")


def get_tax_processor(order=None, user=None):
    modulename = config_value("TAX", "MODULE")
    mod = load_module(modulename + ".tax")
    return mod.Processor(order=order, user=user)


def round_cents(x):
    return x.quantize(TWOPLACES, decimal.ROUND_FLOOR)
