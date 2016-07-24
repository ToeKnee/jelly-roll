from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from satchmo.l10n.mixins import TranslatedObjectMixin
from satchmo.product.models import (
    Category,
    Product
)

import logging
log = logging.getLogger(__name__)


class BrandManager(models.Manager):

    def active(self, site=None):
        if not site:
            site = Site.objects.get_current()
        return self.filter(site=site, active=True)

    def by_slug(self, slug):
        site = Site.objects.get_current()
        return self.get(slug=slug, site=site)


class Brand(models.Model, TranslatedObjectMixin):
    """A product brand"""
    site = models.ForeignKey(Site)
    slug = models.SlugField(_("Slug"), unique=True,
                            help_text=_("Used for URLs"))
    products = models.ManyToManyField(Product, blank=True,
                                      related_name="brands",
                                      verbose_name=_("Products"))
    categories = models.ManyToManyField(Category, blank=True,
                                        related_name="brands",
                                        verbose_name=_("Category"))
    ordering = models.IntegerField(_("Ordering"))
    active = models.BooleanField(default=True)
    restock_interval = models.IntegerField(_("Restock Interval"), null=True,
        blank=False, help_text=_("Typical value in days between restocks"))
    last_restocked = models.DateField(_("Last Restocked"), null=True, blank=True,
                           help_text=_("Date of last restock"))
    stock_due_on = models.DateField(_("Stock Due On"), null=True, blank=True,
                           help_text=_("Date of next restock if known"))

    objects = BrandManager()

    class Meta:
        ordering = ('ordering', 'slug')
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')

    def __unicode__(self):
        return u"%s" % self.slug

    def get_absolute_url(self):
        url = reverse('satchmo_brand_view',
                      kwargs={
                          'brandname': self.slug
                      })
        return url

    def get_category_url(self):
        try:
            category = self.active_categories[0]
        except IndexError:
            category = None

        if category:
            url = reverse('satchmo_brand_category_view',
                          kwargs={
                              'category_slug': category.slug,
                              'brand_slug': self.slug
                          })
        else:
            url = reverse('satchmo_brand_view',
                          kwargs={
                              'brandname': self.slug
                          })
        return url

    @property
    def active_categories(self):
        return self.categories.filter(active=True)

    @property
    def translation(self):
        return self._find_translation()

    def active_products(self, category=None):
        products = self.products.filter(site=self.site, active=True)
        if category:
            products = products.filter(category=category)
        return products

    def has_categories(self):
        return self.active_categories().count() > 0

    def has_content(self):
        return self.has_products() or self.has_categories()

    def has_products(self):
        return self.active_products().count > 0


class BrandTranslation(models.Model):
    brand = models.ForeignKey(Brand, related_name="translations")
    languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(_('title'), max_length=100, blank=False)
    short_description = models.CharField(_('Short Description'), blank=True, max_length=200)  # TODO: This should be changed to meta_keywords
    meta_description = models.TextField(_('Meta Description'), blank=True)
    description = models.TextField(_('Full description, visible to customers'), blank=True)  # TODO: Rename this to "full description"
    picture = models.ImageField(
        verbose_name=_('Picture'),
        upload_to="brand/",
        null=True, blank=True,
        max_length=200
    )

    class Meta:
        ordering = ('languagecode', )
        verbose_name = _('Brand Translation')
        verbose_name_plural = _('Brand Translations')

    @property
    def filename(self):
        if self.brand:
            return '%s-%s' % (self.brand.slug, self.id)
        else:
            return 'default'
