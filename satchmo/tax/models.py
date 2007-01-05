"""
Store tables used to calculate tax on a product
"""

from django.db import models
from satchmo.i18n.models import Area, Country
from satchmo.shop.utils.validators import MutuallyExclusiveWithField

class TaxClass(models.Model):
    """
    Type of tax that can be applied to a product.  Tax
    might vary based on the type of product.  In the US, clothing could be 
    taxed at a different rate than food items.
    """
    title = models.CharField("Title", maxlength=20, help_text="Displayed title of this tax")
    description = models.CharField("Description", maxlength=30,help_text='Description of products that would be taxed')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Tax Classes"
    
    class Admin:
        pass
        

taxrate_zoneandcountry_zone_validator = MutuallyExclusiveWithField('taxCountry')
taxrate_zoneandcountry_country_validator = MutuallyExclusiveWithField('taxZone')
class TaxRate(models.Model):
    """
    Actual percentage tax based on area and product class
    """
    taxClass = models.ForeignKey(TaxClass)
    taxZone = models.ForeignKey(Area, blank=True, null=True, 
                                validator_list=[taxrate_zoneandcountry_zone_validator])
    taxCountry = models.ForeignKey(Country, blank=True, null=True,
                                   validator_list=[taxrate_zoneandcountry_country_validator])
    percentage = models.FloatField(max_digits=7, decimal_places=6, help_text="% tax for this area and type")
    
    def _country(self):
        if self.taxZone:
            return self.taxZone.country.name
        else:
            return self.taxCountry.name
    country = property(_country)
    
    def __str__(self):
        return ("%s - %s" % (self.taxClass,
                             self.taxZone and self.taxZone or self.taxCountry))
    
    class Admin:
        list_display = ("taxClass", "taxZone", "taxCountry", "percentage")
