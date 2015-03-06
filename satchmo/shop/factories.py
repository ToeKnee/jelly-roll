import factory
from decimal import Decimal

from django.contrib.sites.models import Site

from factory import lazy_attribute

from satchmo.contact.factories import ContactFactory
from satchmo.l10n.factories import CountryFactory
from satchmo.shop.models import Config, Order, OrderItem, OrderPayment
from satchmo.product.factories import ProductFactory, TaxableProductFactory


class ShopConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Config

    site_id = 1
    store_name = "Test Shop"

    country = factory.LazyAttribute(lambda a: CountryFactory())


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    contact = factory.SubFactory(ContactFactory)
    site = factory.LazyAttribute(lambda a: Site.objects.get_current())


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
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


class TestOrderFactory(OrderFactory):
    shipping_cost = Decimal('10.00')
    discount = Decimal('0.00')
    shipping_discount = Decimal('0.00')
    sub_total = Decimal('25.00')
    tax = Decimal('0.00')
    total = Decimal('35.00')

    @factory.post_generation
    def add_order_item(obj, create, extracted, **kwargs):
        TaxableOrderItemFactory(order=obj)


class PaidOrderFactory(TestOrderFactory):
    @factory.post_generation
    def add_payment(obj, create, extracted, **kwargs):
        OrderPaymentFactory(order=obj)


class OrderPaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderPayment

    order = factory.SubFactory(PaidOrderFactory)
    payment = "PAYMENT_AUTOSUCCESS"
    amount = factory.LazyAttribute(lambda obj: obj.order.total)
