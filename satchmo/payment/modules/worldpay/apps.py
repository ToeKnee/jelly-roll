from django.apps import AppConfig


class WorldPayConfig(AppConfig):
    """WorldPay app."""

    name = "satchmo.payment.modules.worldpay"
    verbose_name = "WorldPay Payment"

    def ready(self):
        from . import config
