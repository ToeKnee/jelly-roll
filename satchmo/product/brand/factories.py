import factory
from decimal import Decimal

from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from satchmo.product.brand.models import Brand


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    site_id = 1
    ordering = 0
