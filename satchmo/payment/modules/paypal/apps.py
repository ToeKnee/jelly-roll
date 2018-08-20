from django.apps import AppConfig


class PayPalConfig(AppConfig):
    """Paypal app."""
    name = "satchmo.payment.modules.paypal"
    verbose_name = "PayPal Payment"

    def ready(self):
        from . import config
