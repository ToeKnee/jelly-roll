from satchmo.utils import load_once
load_once('tieredweightzone', 'satchmo.shipping.modules.tieredweightzone')

default_app_config = 'satchmo.shipping.modules.tieredweightzone.apps.TieredWeightZoneConfig'


def get_methods():
    from .models import Carrier, Shipper
    return [Shipper(carrier) for carrier in Carrier.objects.filter(active=True).order_by('ordering')]
