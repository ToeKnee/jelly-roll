from django.apps import AppConfig


class ContactConfig(AppConfig):
    """Contact app."""
    name = "satchmo.contact"
    verbose_name = "Contact"

    def ready(self):
        from . import config
        from . import listeners
