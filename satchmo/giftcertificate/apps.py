from django.apps import AppConfig


class GiftCertificateConfig(AppConfig):
    """Gift Certificate app."""
    name = "satchmo.giftcertificate"
    verbose_name = "Gift Certificate"

    def ready(self):
        from . import config
