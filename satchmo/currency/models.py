import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from satchmo.l10n.models import Country


class CurrencyManager(models.Manager):
    def get_primary(self):
        return Currency.objects.get(primary=True)

    def accepted(self):
        return Currency.objects.filter(primary=False, accepted=True)

    def all_accepted(self):
        return Currency.objects.filter(accepted=True)


class Currency(models.Model):
    iso_4217_code = models.CharField(_("ISO 4217 code"), max_length=3, unique=True)
    name = models.CharField(_("Name"), max_length=255)
    symbol = models.CharField(_("Symbol"), max_length=5)
    minor_symbol = models.CharField(_("Minor Symbol"), max_length=5, help_text=_("Pence, Cent, Sen, etc."))
    countries = models.ManyToManyField(Country, related_name="currency")

    primary = models.BooleanField(_("Primary"), help_text=_("Primary currency for the shop"), default=False)
    accepted = models.BooleanField(_("Accepted"), help_text=_("Accepted alternative currency for the shop"), default=False)

    objects = CurrencyManager()

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


class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, related_name="exchange_rates", editable=False)
    date = models.DateField(_("Date"), default=datetime.date.today, editable=False)
    rate = models.DecimalField(_("Rate"), help_text=_("Rate from primary currency"), max_digits=6, decimal_places=4, editable=False)

    class Meta:
        verbose_name = _('Exchange Rate')
        verbose_name_plural = _('Exchange Rates')
        unique_together = ('currency', 'date')
        get_latest_by = "date"
        ordering = ("-date", )
        order_with_respect_to = 'currency'

    def __unicode__(self):
        return u"{currency} {rate}".format(
            currency=self.currency,
            rate=self.rate
        )
