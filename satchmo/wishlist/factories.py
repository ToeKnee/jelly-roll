import factory

from satchmo.contact.factories import ContactFactory
from satchmo.product.factories import ProductFactory
from satchmo.wishlist.models import ProductWish


class ProductWishFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductWish

    contact = factory.SubFactory(ContactFactory)
    product = factory.SubFactory(ProductFactory, active=True)
