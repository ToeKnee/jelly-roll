from django.apps import AppConfig


class ProductConfig(AppConfig):
    """Product app."""
    name = "satchmo.product"
    verbose_name = "Product"

    def ready(self):
        from . import config
