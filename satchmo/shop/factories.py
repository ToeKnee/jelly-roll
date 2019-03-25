import factory
import uuid
from decimal import Decimal

from django.contrib.sites.models import Site

from factory import lazy_attribute

from satchmo.contact.factories import ContactFactory
from satchmo.currency.factories import CurrencyFactory
from satchmo.l10n.factories import CountryFactory
from satchmo.shop.models import (
    Cart,
    CartItem,
    Config,
    Order,
    OrderItem,
    OrderPayment,
    OrderRefund,
    OrderStatus,
    Status,
)
from satchmo.product.factories import ProductFactory, TaxableProductFactory


class ShopConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Config

    site_id = 1
    store_name = "Test Shop"

    country = factory.LazyAttribute(lambda a: CountryFactory())


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    site = factory.LazyAttribute(lambda a: Site.objects.get_current())
    customer = factory.SubFactory(ContactFactory)

    @factory.post_generation
    def add_cart_item(obj, create, extracted, **kwargs):
        CartItemFactory(cart=obj)


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 5


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    contact = factory.SubFactory(ContactFactory)
    site = factory.LazyAttribute(lambda a: Site.objects.get_current())
    currency = factory.SubFactory(CurrencyFactory)


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 5

    @factory.post_generation
    def update_quantity(obj, create, extracted, **kwargs):
        obj.product.items_in_stock += obj.quantity
        obj.product.save()

    @lazy_attribute
    def unit_price(oi):
        return oi.product.unit_price

    @lazy_attribute
    def line_item_price(oi):
        return oi.unit_price * oi.quantity


class TaxableOrderItemFactory(OrderItemFactory):
    product = factory.SubFactory(TaxableProductFactory)


class TestOrderFactory(OrderFactory):
    shipping_cost = Decimal("10.00")
    discount = Decimal("0.00")
    shipping_discount = Decimal("0.00")
    sub_total = Decimal("25.00")
    tax = Decimal("0.00")
    total = Decimal("35.00")

    @factory.post_generation
    def add_order_item(obj, create, extracted, **kwargs):
        TaxableOrderItemFactory(order=obj)


class PaidOrderFactory(TestOrderFactory):
    frozen = True

    @factory.post_generation
    def add_payment(obj, create, extracted, **kwargs):
        OrderPaymentFactory(order=obj)


class OrderPaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderPayment

    order = factory.SubFactory(PaidOrderFactory)
    payment = "PAYMENT_AUTOSUCCESS"
    amount = factory.LazyAttribute(lambda obj: obj.order.total)
    transaction_id = factory.LazyAttribute(lambda obj: uuid.uuid4())


class OrderRefundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderRefund

    order = factory.SubFactory(PaidOrderFactory)
    amount = factory.LazyAttribute(lambda obj: obj.order.total / 2)


class ShippedOrderFactory(PaidOrderFactory):
    """Doesn't really represent a shipped order, but at least it has a
    Shipped status
    """

    @factory.post_generation
    def add_shipped_status(obj, create, extracted, **kwargs):
        if create:
            obj.add_status("Shipped", "Test Order Shipped")


class StatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Status

    status = "Test"


class OrderStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderStatus

    order = factory.SubFactory(OrderFactory)
    status = factory.SubFactory(StatusFactory)
    notes = "Test Order Status"
