from django.apps import AppConfig


class FulfilmentConfig(AppConfig):
    """Fulfilment app."""

    name = "satchmo.fulfilment"
    verbose_name = "Fulfilment"

    def ready(self):
        from . import config
