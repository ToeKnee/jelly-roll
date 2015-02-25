import factory
from decimal import Decimal

from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from satchmo.product.models import (
    ConfigurableProduct,
    Product,
    Price,
)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    site = factory.LazyAttribute(lambda a: Site.objects.get_current())
    name = factory.Sequence(lambda n: 'Product {0}'.format(n))
    slug = factory.LazyAttribute(lambda a: slugify(a.name))

    @factory.post_generation
    def create_price(obj, create, extracted, **kwargs):
        PriceFactory(product=obj)


class TaxableProductFactory(ProductFactory):
    taxable = True


class ConfigurableProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConfigurableProduct

    product = factory.SubFactory(ProductFactory)


class PriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Price

    product = factory.SubFactory(TaxableProductFactory)
    price = Decimal("5.00")
