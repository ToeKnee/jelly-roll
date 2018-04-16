from . import config
from .models import Carrier, Shipper
from satchmo.utils import load_once

load_once('tieredweightzone', 'satchmo.shipping.modules.tieredweightzone')


def get_methods():
    return [Shipper(carrier) for carrier in Carrier.objects.filter(active=True).order_by('ordering')]
