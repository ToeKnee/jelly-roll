from django.apps import AppConfig


class TieredWeightZoneConfig(AppConfig):
    """TieredWeightZone app."""
    name = "satchmo.shipping.modules.tieredweightzone"
    verbose_name = "Tiered Weight Zone Shipping"

    def ready(self):
        from . import config
