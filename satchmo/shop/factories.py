import factory
from decimal import Decimal

from django.contrib.sites.models import Site

from factory import lazy_attribute

from satchmo.contact.factories import ContactFactory
from satchmo.l10n.factories import CountryFactory
from satchmo.shop.models import Config, Order, OrderItem
from satchmo.product.factories import ProductFactory, TaxableProductFactory


class ShopConfigFactory(factory.Factory):
    FACTORY_FOR = Config

    site_id = 1
    store_name = "Test Shop"

    country = factory.LazyAttribute(lambda a: CountryFactory())


class OrderItemFactory(factory.Factory):
    FACTORY_FOR = OrderItem

    #order = factory.CircularSubFactory('satchmo.shop.factories', 'OrderFactory')
    product = factory.SubFactory(ProductFactory)
    quantity = 5

    @lazy_attribute
    def unit_price(oi):
        return oi.product.unit_price

    @lazy_attribute
    def line_item_price(oi):
        return oi.unit_price * oi.quantity


class TaxableOrderItemFactory(OrderItemFactory):
    product = factory.SubFactory(TaxableProductFactory)


class OrderFactory(factory.Factory):
    FACTORY_FOR = Order

    contact = factory.RelatedFactory(ContactFactory)
    site = factory.LazyAttribute(lambda a: Site.objects.get_current())


class TestOrderFactory(OrderFactory):
    shipping_cost = Decimal('10.00')
    order_item = factory.RelatedFactory(TaxableOrderItemFactory)


class TestOrderNonTaxedFactory(TestOrderFactory):
    order_item = factory.RelatedFactory(OrderItemFactory)
