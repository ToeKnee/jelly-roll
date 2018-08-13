from django.apps import AppConfig


class DummyConfig(AppConfig):
    """Dummy app."""
    name = "satchmo.payment.modules.dummy"
    verbose_name = "Dummy Payment"

    def ready(self):
        from . import config
