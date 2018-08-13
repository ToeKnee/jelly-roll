from django.apps import AppConfig


class ShippingConfig(AppConfig):
    """Shipping app."""
    name = "satchmo.shipping"
    verbose_name = "Shipping"

    def ready(self):
        from . import config
