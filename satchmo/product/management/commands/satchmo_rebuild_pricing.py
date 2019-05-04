from django.core.management.base import BaseCommand
from optparse import make_option
from satchmo.product.models import Product, ProductPriceLookup


class Command(BaseCommand):
    help = "Builds Satcho Product pricing lookup tables."

    requires_model_validation = True

    def handle(self, **options):
        from django.conf import settings

        verbosity = int(options.get("verbosity", 1))

        total = 0
        if verbosity > 0:
            print("Starting product pricing")

        if verbosity > 1:
            print("Deleting old pricing")

        for lookup in ProductPriceLookup.objects.all():
            lookup.delete()

        products = Product.objects.active(variations=False)
        if verbosity > 0:
            print(("Adding %i products" % products.count()))

        for product in products:
            if verbosity > 1:
                print(("Processing product: %s" % product.slug))

            prices = ProductPriceLookup.objects.smart_create_for_product(product)
            if verbosity > 1:
                print(("Created %i prices" % len(prices)))

            total += len(prices)

        if verbosity > 0:
            print(("Added %i total prices" % total))
