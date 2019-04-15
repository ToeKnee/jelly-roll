import factory

from satchmo.product.brand.models import Brand


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    slug = factory.Faker("word")
    ordering = 0

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of products were passed in, use them
            for product in extracted:
                self.products.add(product)
