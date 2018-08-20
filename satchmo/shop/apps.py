from django.apps import AppConfig


class ShopConfig(AppConfig):
    """Shop app."""
    name = "satchmo.shop"
    verbose_name = "Shop"

    def ready(self):
        from . import config
