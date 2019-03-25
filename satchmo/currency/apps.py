from django.apps import AppConfig


class CurrencyConfig(AppConfig):
    """Currency app."""

    name = "satchmo.currency"
    verbose_name = "Currency"

    def ready(self):
        from . import config
