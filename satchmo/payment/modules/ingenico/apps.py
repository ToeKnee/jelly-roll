from django.apps import AppConfig


class IngenicoConfig(AppConfig):
    """Ingenico app."""

    name = "satchmo.payment.modules.ingenico"
    verbose_name = "Ingenico Payment"

    def ready(self):
        from . import config
