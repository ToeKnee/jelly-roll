from django.apps import AppConfig


class SixConfig(AppConfig):
    """Six app."""

    name = "satchmo.fulfilment.modules.six"
    verbose_name = "Six Fulfilment"

    def ready(self):
        from . import config
