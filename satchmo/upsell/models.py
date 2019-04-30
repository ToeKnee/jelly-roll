"""
Associates products to each other for upselling purposes.
"""
import datetime
import logging

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchmo import caching
from satchmo.caching.models import CachedObjectMixin
from satchmo.product.models import Product


log = logging.getLogger(__name__)

UPSELL_CHOICES = (
    ("CHECKBOX_1_FALSE", _("Checkbox to add 1")),
    ("CHECKBOX_1_TRUE", _("Checkbox to add 1, checked by default")),
    ("CHECKBOX_MATCH_FALSE", _("Checkbox to match quantity")),
    ("CHECKBOX_MATCH_TRUE", _("Checkbox to match quantity, checked by default")),
    ("FORM", _("Form with 0 quantity")),
)


class Upsell(models.Model, CachedObjectMixin):

    target = models.ManyToManyField(
        Product,
        verbose_name=_("Target Product"),
        related_name="upselltargets",
        help_text=_(
            "The products for which you want to show this goal product as an Upsell."
        ),
    )

    goal = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Goal Product"),
        related_name="upsellgoals",
    )

    create_date = models.DateField(_("Creation Date"))

    style = models.CharField(
        _("Upsell Style"),
        choices=UPSELL_CHOICES,
        default="CHECKBOX_1_FALSE",
        max_length=20,
    )

    description = models.TextField(_("Description"), blank=True)
    notes = models.TextField(
        _("Notes"), blank=True, null=True, help_text=_("Internal notes")
    )

    def is_form(self):
        """Returns true if the style is a FORM"""
        return self.style.startswith("FORM")

    def is_qty_one(self):
        """Returns true if this style has a '1' in the center field"""
        parts = self.style.split("_")
        return parts[1] == "1"

    def is_checked(self):
        """Returns true if this style ends with TRUE"""
        return self.style.endswith("TRUE")

    def __str__(self):
        return "Upsell for %s" % self.goal

    def save(self, *args, **kwargs):
        self.create_date = datetime.date.today()
        self.cache_delete()
        super(Upsell, self).save(*args, **kwargs)
        self.cache_set()
        return self

    class Meta:
        ordering = ("goal",)
