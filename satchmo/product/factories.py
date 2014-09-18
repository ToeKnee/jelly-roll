import factory

from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from satchmo.product.models import (
    ConfigurableProduct,
    Product
)


class ProductFactory(factory.Factory):
    FACTORY_FOR = Product

    site = factory.LazyAttribute(lambda a: Site.objects.get_current())
    name = factory.Sequence(lambda n: 'Product {0}'.format(n))
    slug = factory.LazyAttribute(lambda a: slugify(a.name))


class TaxableProductFactory(ProductFactory):
    taxable = True


class ConfigurableProductFactory(factory.Factory):
    FACTORY_FOR = ConfigurableProduct

    product = factory.SubFactory(ProductFactory)
