import factory
from decimal import Decimal

from django.utils.text import slugify

from satchmo.product.models import ConfigurableProduct, Product, Price


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: "Product {0}".format(n))
    slug = factory.LazyAttribute(lambda a: slugify(a.name))
    unit_price = Decimal("5.00")

    @factory.post_generation
    def brands(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of products were passed in, use them
            for brand in extracted:
                self.brands.add(brand)


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
