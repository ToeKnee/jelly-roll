from django.utils.translation import ugettext_lazy as _

import satchmo.shipping.config


URGENT = 0
PRIORITY = 1
STANDARD = 2
ECONOMY = 3
POSTAGE_SPEED_CHOICES = (
    (URGENT, _("Urgent")),
    (PRIORITY, _("Priority")),
    (STANDARD, _("Standard")),
    (ECONOMY, _("Economy")),
)
