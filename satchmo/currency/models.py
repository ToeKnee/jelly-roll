from django.db import models
from django.utils.translation import ugettext_lazy as _

from satchmo.l10n.models import Country


class Currency(models.Model):
    iso_4217_code = models.CharField(_("ISO 4217 code"), max_length=3, unique=True)
    name = models.CharField(_("Name"), max_length=255)
    symbol = models.CharField(_("Symbol"), max_length=5)
    minor_symbol = models.CharField(_("Minor Symbol"), max_length=5, help_text=_("Pence, Cent, Sen, etc."))
    countries = models.ManyToManyField(Country, related_name="currency")

    primary = models.BooleanField(_("Primary"), help_text=_("Primary currency for the shop"), default=False)
    accepted = models.BooleanField(_("Accepted"), help_text=_("Accepted alternative currency for the shop"), default=False)

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    def __unicode__(self):
        return self.iso_4217_code

    def save(self, *args, **kwargs):
        # Ensure that there is only one primary currency
        if self.primary:
            Currency.objects.exclude(id=self.id).update(primary=False)
            if self.accepted is False:
                self.accepted = True

        return super(Currency, self).save(*args, **kwargs)
