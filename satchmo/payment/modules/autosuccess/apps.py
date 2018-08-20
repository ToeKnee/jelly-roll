from django.apps import AppConfig


class AutoSuccessConfig(AppConfig):
    """Autosuccess app."""
    name = "satchmo.payment.modules.autosuccess"
    verbose_name = "Autosuccess Payment"

    def ready(self):
        from . import config
