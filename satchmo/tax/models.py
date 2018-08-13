"""
Store tables used to calculate tax on a product
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchmo.l10n.models import AdminArea, Country


class TaxClass(models.Model):
    """
    Type of tax that can be applied to a product.  Tax
    might vary based on the type of product.  In the US, clothing could be
    taxed at a different rate than food items.
    """
    title = models.CharField(_("Title"), max_length=20,
                             help_text=_("Displayed title of this tax."))
    description = models.CharField(_("Description"), max_length=30,
                                   help_text=_("Description of products that would be taxed."))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Tax Class")
        verbose_name_plural = _("Tax Classes")


class TaxRate(models.Model):
    """
    Actual percentage tax based on area and product class
    """
    taxClass = models.ForeignKey(
        TaxClass,
        on_delete=models.CASCADE,
        verbose_name=_('Tax Class')
    )
    taxZone = models.ForeignKey(
        AdminArea,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('Tax Zone')
    )
    taxCountry = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('Tax Country')
    )
    percentage = models.DecimalField(_("Percentage"), max_digits=7,
                                     decimal_places=6, help_text=_("% tax for this area and type"))

    def _country(self):
        if self.taxZone:
            return self.taxZone.country.name
        else:
            return self.taxCountry.name
    country = property(_country)

    def _display_percentage(self):
        return "%#2.2f%%" % (100*self.percentage)
    _display_percentage.short_description = _('Percentage')
    display_percentage = property(_display_percentage)

    def __str__(self):
        return "%s - %s = %s" % (self.taxClass,
                                 self.taxZone and self.taxZone or self.taxCountry,
                                 self.display_percentage)

    class Meta:
        verbose_name = _("Tax Rate")
        verbose_name_plural = _("Tax Rates")
