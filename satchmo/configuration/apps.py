from django.apps import AppConfig


class ConfigurationConfig(AppConfig):
    """Configuration app."""

    name = "satchmo.configuration"
    verbose_name = "Configuration"

    def ready(self):
        pass
