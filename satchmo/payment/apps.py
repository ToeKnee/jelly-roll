from django.apps import AppConfig


class PaymentConfig(AppConfig):
    """Payment app."""
    name = "satchmo.payment"
    verbose_name = "Payment"

    def ready(self):
        from . import config
