"""
Tiered Weight Zoned shipping models
"""
import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import get_language, ugettext_lazy as _

from satchmo.shipping.models import POSTAGE_SPEED_CHOICES, STANDARD
from satchmo.shipping.modules.base import BaseShipper
from satchmo.l10n.models import Continent, Country

import logging
log = logging.getLogger(__name__)


class TieredPriceException(Exception):
    def __init__(self, reason):
        self.reason = reason
        super(TieredPriceException, self).__init__(reason)


class Shipper(BaseShipper):
    def __init__(self, carrier):
        self.id = carrier.key
        self.carrier = carrier
        super(Shipper, self).__init__()

    def __str__(self):
        """
        This is mainly helpful for debugging purposes
        """
        return "TieredWeight_Shipper: %s" % self.id

    def description(self):
        """
        A basic description that will be displayed to the user when selecting their shipping options
        """
        return self.carrier.description

    def cost(self):
        # calculate the weight of the entire order
        assert(self._calculated)
        weight = Decimal('0.0')

        for item in self.cart.cartitem_set.all():
            if item.is_shippable and item.product.weight:
                weight += item.product.weight * item.quantity

        country = self.contact.shipping_address.country_id
        discount_multiplier = 1 - (self.shipping_discount() / Decimal('100.0'))

        return self.carrier.price(weight, country) * discount_multiplier

    def shipping_discount(self):
        discounts = ShippingDiscount.objects.filter(
            carrier=self.carrier,
            zone__in=self.contact.shipping_address.country.zone.all(),
            minimum_order_value__lte=self.cart.total
        ).filter(
            Q(start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today()) |
            Q(end_date__isnull=True)
        ).order_by(
            '-percentage'
        )

        try:
            percentage = discounts[0].percentage
        except IndexError:
            percentage = 0

        return percentage

    def method(self):
        """
        Describes the actual delivery service (Mail, FedEx, DHL, UPS, etc)
        """
        return self.carrier.method

    def expectedDelivery(self):
        """
        Can be a plain string or complex calculation returning an actual date
        """
        return self.carrier.delivery

    def valid(self, order=None):
        """
        Can do complex validation about whether or not this option is valid.
        For example, may check to see if the recipient is in an allowed country
        or location.
        """
        try:
            self.cost()
        except TieredPriceException:
            return False
        return True


class Carrier(models.Model):
    key = models.SlugField(_('Key'))
    ordering = models.IntegerField(_('Ordering'), default=0)
    active = models.BooleanField(_('Active'), default=False)
    signed_for = models.BooleanField(_('Signed For'), default=False)
    tracked = models.BooleanField(_('Tracked'), default=False)
    postage_speed = models.PositiveIntegerField(
        _('Postage Speed'), choices=POSTAGE_SPEED_CHOICES, default=STANDARD)
    estimated_delivery_min_days = models.PositiveIntegerField(
        _('Minimum number of days after shipping until delivery'), default=1)
    estimated_delivery_expected_days = models.PositiveIntegerField(
        _('Usual number of days after shipping until delivery'), default=7)
    estimated_delivery_max_days = models.PositiveIntegerField(
        _('Maximum number of days after shipping until delivery'), default=25)

    class Meta:
        db_table = "tieredweightzone_carrier"

    def __str__(self):
        return "%s (%s)" % (self.name, self.description)

    def _find_translation(self, language_code=None):
        if not language_code:
            language_code = get_language()

        c = self.translations.filter(languagecode__exact=language_code)
        ct = c.count()

        if not c or ct == 0:
            pos = language_code.find('-')
            if pos > -1:
                short_code = language_code[:pos]
                log.debug(
                    "%s: Trying to find root language content for: [%s]", self.id, short_code)
                c = self.translations.filter(languagecode__exact=short_code)
                ct = c.count()
                if ct > 0:
                    log.debug(
                        "%s: Found root language content for: [%s]", self.id, short_code)

        if not c or ct == 0:
            log.debug("Trying to find default language content for: %s", self)
            c = self.translations.filter(
                languagecode__istartswith=settings.LANGUAGE_CODE)
            ct = c.count()

        if not c or ct == 0:
            log.debug("Trying to find *any* language content for: %s", self)
            c = self.translations.all()
            ct = c.count()

        if ct > 0:
            trans = c[0]
        else:
            trans = None

        return trans

    def delivery(self):
        """Get the delivery, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.delivery
        else:
            return ""

    delivery = property(delivery)

    def description(self):
        """Get the description, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()
        if trans:
            return trans.description
        else:
            return ""
    description = property(description)

    def method(self):
        """Get the description, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.method
        else:
            return ""

    method = property(method)

    def name(self):
        """Get the name, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.name
        else:
            return ""

    name = property(name)

    def price(self, wgt, country):
        """Get a price for this weight and country."""
        # Check delivery address' continent
        destination_country = Country.objects.get(id=country)
        continent = destination_country.continent

        try:
            zone = Zone.objects.get(country=destination_country)
        except Zone.DoesNotExist:
            zone = Zone.objects.get(continent__id=continent.id, country=None)

        tiers = WeightTier.objects.filter(carrier=self, zone=zone)

        if not tiers:
            raise TieredPriceException(
                'No price available. For this zone/country/weight')

        # check for special discounts
        prices = tiers.filter(expires__isnull=False, min_weight__lte=wgt).exclude(
            expires__lt=datetime.date.today())
        if not prices.count() > 0:
            prices = tiers.filter(expires__isnull=True, min_weight__lte=wgt)

        if prices.count() > 0:
            # Get the price with the quantity closest to the one specified without going over
            return Decimal(prices.order_by('-min_weight')[0].price)
        else:
            log.debug("No tiered price found for %s: weight=%s", self.id, wgt)
            raise TieredPriceException(
                'No price available. Please contact us for a price.'
            )


class CarrierTranslation(models.Model):
    carrier = models.ForeignKey(
        'Carrier',
        on_delete=models.CASCADE,
        related_name='translations'
    )
    languagecode = models.CharField(
        _('language'), max_length=10, choices=settings.LANGUAGES,)
    name = models.CharField(_('Carrier'), max_length=50, )
    description = models.CharField(_('Description'), max_length=200)
    method = models.CharField(
        _('Method'), help_text=_("i.e. US Mail"), max_length=200)
    delivery = models.CharField(_('Delivery Days'), max_length=200)

    class Meta:
        db_table = "tieredweightzone_carriertranslation"
        ordering = ('languagecode', 'name')


class Zone(models.Model):
    key = models.SlugField(_('Key'))
    continent = models.ManyToManyField(
        Continent, related_name='continent', db_table="tieredweightzone_zone_continent"
    )
    country = models.ManyToManyField(
        Country, related_name='zone', db_table="tieredweightzone_zone_country", blank=True
    )

    class Meta:
        db_table = "tieredweightzone_zone"

    def __str__(self):
        return "%s (%s)" % (self.name, self.description)

    def _find_translation(self, language_code=None):
        if not language_code:
            language_code = get_language()

        c = self.translations.filter(languagecode__exact=language_code)
        ct = c.count()

        if not c or ct == 0:
            pos = language_code.find('-')
            if pos > -1:
                short_code = language_code[:pos]
                log.debug(
                    "%s: Trying to find root language content for: [%s]", self.id, short_code)
                c = self.translations.filter(languagecode__exact=short_code)
                ct = c.count()
                if ct > 0:
                    log.debug(
                        "%s: Found root language content for: [%s]", self.id, short_code)

        if not c or ct == 0:
            log.debug("Trying to find default language content for: %s", self)
            c = self.translations.filter(
                languagecode__istartswith=settings.LANGUAGE_CODE)
            ct = c.count()

        if not c or ct == 0:
            log.debug("Trying to find *any* language content for: %s", self)
            c = self.translations.all()
            ct = c.count()

        if ct > 0:
            trans = c[0]
        else:
            trans = None

        return trans

    @property
    def description(self):
        """Get the description, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()
        if trans:
            return trans.description
        else:
            return ""

    @property
    def name(self):
        """Get the name, looking up by language code, falling back intelligently.
        """
        trans = self._find_translation()

        if trans:
            return trans.name
        else:
            return ""


class ZoneTranslation(models.Model):
    zone = models.ForeignKey(
        'Zone',
        on_delete=models.CASCADE,
        related_name='translations'
    )
    languagecode = models.CharField(
        _('language'), max_length=10, choices=settings.LANGUAGES, )
    name = models.CharField(_('Zone'), max_length=50, )
    description = models.CharField(_('Description'), max_length=200)

    class Meta:
        db_table = "tieredweightzone_zonetranslation"
        ordering = ('languagecode', 'name')


class WeightTier(models.Model):
    carrier = models.ForeignKey(
        'Carrier',
        on_delete=models.CASCADE,
        related_name='tiers'
    )
    zone = models.ForeignKey(
        'Zone',
        on_delete=models.CASCADE,
        related_name='tiers'
    )
    min_weight = models.DecimalField(
        _("Min Weight"),
        help_text=_('The minumum weight for this tier to apply'),
        max_digits=10, decimal_places=2, )
    price = models.DecimalField(
        _("Shipping Price"), max_digits=10, decimal_places=2, )
    expires = models.DateField(_("Expires"), null=True, blank=True)

    class Meta:
        db_table = "tieredweightzone_weighttier"
        ordering = ('zone', 'carrier', 'price')

    def __str__(self):
        return "%s @ %s" % (self.price, self.min_weight)


class ShippingDiscount(models.Model):
    carrier = models.ForeignKey(
        'Carrier',
        on_delete=models.CASCADE,
        related_name='shipping_discount'
    )
    zone = models.ForeignKey(
        'Zone',
        on_delete=models.CASCADE,
        related_name='shipping_discount'
    )
    percentage = models.IntegerField(_("Percentage Discount"))
    minimum_order_value = models.DecimalField(
        _("Minimum Order Value"), max_digits=10, decimal_places=2)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"), null=True, blank=True)

    class Meta:
        db_table = "tieredweightzone_shippingdiscount"

    def save(self, *args, **kwargs):
        if self.start_date is None:
            self.start_date = datetime.date.today()
        super(ShippingDiscount, self).save(*args, **kwargs)
