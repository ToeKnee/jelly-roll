from django.apps import AppConfig


class TaxConfig(AppConfig):
    """Tax app."""

    name = "satchmo.tax"
    verbose_name = "Tax"

    def ready(self):
        from . import config
