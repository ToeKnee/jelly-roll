"""
Configuration items for the shop.
Also contains shopping cart and related classes.
"""
import datetime
import hmac
import logging
import operator
import random
import time
from decimal import Decimal, ROUND_HALF_EVEN
from workdays import workday

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import OuterRef, Subquery
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from satchmo import caching
from satchmo.configuration.functions import ConfigurationSettings
from satchmo.contact.models import Contact
from satchmo.contact.signals import satchmo_contact_location_changed
from satchmo.currency.models import Currency, ExchangeRate
from satchmo.currency.utils import (
    convert_to_currency,
    currency_for_request,
    money_format,
)
from satchmo.discount.utils import find_discount_for_code
from satchmo.l10n.models import Country
from satchmo.payment.fields import PaymentChoiceCharField
from satchmo.product import signals as product_signals
from satchmo.product.models import Product, DownloadableProduct
from satchmo.shipping.fields import ShippingChoiceCharField
from satchmo.shipping.models import POSTAGE_SPEED_CHOICES, STANDARD
from satchmo.shop import signals
from satchmo.shop.notification import send_order_update, send_owner_order_notice
from satchmo.tax.utils import get_tax_processor
from functools import reduce

log = logging.getLogger(__name__)


class ConfigManager(models.Manager):
    def get_current(self):
        """Convenience method to get the current shop config"""
        try:
            shop_config = caching.cache_get("Config")
        except caching.NotCachedError as nce:
            shop_config = Config.objects.get(site=Site.objects.get_current())
            caching.cache_set(nce.key, value=shop_config)

        return shop_config


class Config(models.Model):
    """
    Used to store specific information about a store.  Also used to
    configure various store behaviors
    """

    site = models.OneToOneField(
        Site, on_delete=models.CASCADE, verbose_name=_("Site"), primary_key=True
    )
    store_name = models.CharField(_("Store Name"), max_length=100, unique=True)
    store_description = models.TextField(_("Description"), blank=True, null=True)
    store_email = models.EmailField(_("Email"), blank=True, null=True)
    street1 = models.CharField(_("Street"), max_length=50, blank=True, null=True)
    street2 = models.CharField(_("Street"), max_length=50, blank=True, null=True)
    city = models.CharField(_("City"), max_length=50, blank=True, null=True)
    state = models.CharField(_("State"), max_length=30, blank=True, null=True)
    postal_code = models.CharField(_("Post Code"), blank=True, null=True, max_length=9)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        null=False,
        verbose_name=_("Country"),
    )
    phone = models.CharField(_("Phone Number"), blank=True, null=True, max_length=12)
    no_stock_checkout = models.BooleanField(
        _("Purchase item not in stock?"), default=False
    )
    in_country_only = models.BooleanField(
        _("Only sell to in-country customers?"), default=True
    )
    sales_country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="sales_country",
        verbose_name=("Default country for customers"),
    )
    shipping_countries = models.ManyToManyField(
        Country,
        blank=True,
        verbose_name=_("Shipping Countries"),
        related_name="shop_configs",
    )

    objects = ConfigManager()

    class Meta:
        verbose_name = _("Store Configuration")
        verbose_name_plural = _("Store Configurations")

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        caching.cache_delete("config")
        # ensure the default country is in shipping countries
        mycountry = self.country

        if mycountry:
            if not self.sales_country:
                log.debug(
                    "%s: No sales_country set, adding country of store, '%s'",
                    self,
                    mycountry,
                )
                self.sales_country = mycountry
        else:
            log.warning("%s: has no country set", self)

        super(Config, self).save(*args, **kwargs)
        caching.cache_set("Config", value=self)

    @property
    def base_url(self):
        site = Site.objects.get_current()
        return "https://" + site.domain

    @property
    def options(self):
        return ConfigurationSettings()

    def areas(self):
        """Get country areas (states/counties).  Used in forms."""
        if self.in_country_only:
            return self.sales_country.adminarea_set.filter(active=True)
        else:
            return None

    def countries(self):
        """Get country selections.  Used in forms."""
        if self.in_country_only:
            return Country.objects.filter(pk=self.sales_country.pk)
        else:
            return self.shipping_countries.filter(active=True)


class NullCart(object):
    """Standin for a real cart when we don't have one yet.  More convenient than testing for null all the time."""

    desc = None
    date_time_created = None
    customer = None
    total = Decimal("0")
    numItems = 0

    def add_item(self, *args, **kwargs):
        pass

    def remove_item(self, *args, **kwargs):
        pass

    def empty(self):
        pass

    def not_enough_stock(self):
        pass

    def __str__(self):
        return "NullCart (empty)"

    def __iter__(self):
        return iter([])

    def __len__(self):
        return 0

    @property
    def currency(self):
        return Currency.objects.get_primary()


class OrderCart(NullCart):
    """Allows us to fake a cart if we are reloading an order."""

    def __init__(self, order):
        super(OrderCart, self).__init__(order)
        self._order = order

    def _numItems(self):
        return self._order.orderitem_set.count()

    numItems = property(_numItems)

    def _cartitem_set(self):
        return self._order.orderitem_set

    cartitem_set = property(_cartitem_set)

    def _total(self):
        return self._order.balance

    total = property(_total)

    def _not_enough_stock(self):
        pass

    not_enough_stock = property(_total)

    is_shippable = False

    def __str__(self):
        return "OrderCart (%i) = %i" % (self._order.id, len(self))

    def __len__(self):
        return self.numItems


class CartManager(models.Manager):
    def from_request(self, request, create=False, return_nullcart=True):
        """Get the current cart from the request"""
        cart = None
        try:
            contact = Contact.objects.from_request(request, create=False)
        except Contact.DoesNotExist:
            contact = None

        if "cart" in request.session:
            cartid = request.session["cart"]
            if cartid == "order":
                log.debug("Getting Order Cart from request")
                try:
                    order = Order.objects.from_request(request)
                    cart = OrderCart(order)
                except Order.DoesNotExist:
                    pass

            else:
                try:
                    cart = Cart.objects.get(id=cartid)
                except Cart.DoesNotExist:
                    log.debug("Removing invalid cart from session")
                    del request.session["cart"]

        if (
            isinstance(cart, NullCart)
            and not isinstance(cart, OrderCart)
            and contact is not None
        ):
            carts = Cart.objects.filter(customer=contact)
            if carts.count() > 0:
                cart = carts[0]
                request.session["cart"] = cart.id

        if not cart:
            if create:
                if contact is None:
                    cart = Cart()
                else:
                    cart = Cart(customer=contact)
                cart.save()
                request.session["cart"] = cart.id

            elif return_nullcart:
                cart = NullCart()

            else:
                raise Cart.DoesNotExist()

        # Set the currency in the cart
        if isinstance(cart, Cart):
            currency_code = currency_for_request(request)
            currency = Currency.objects.all_accepted().get(iso_4217_code=currency_code)
            if cart.currency != currency:
                cart.currency = currency
                cart.save()

        log.debug("Cart: %s", cart)
        return cart


class Cart(models.Model):
    """
    Store items currently in a cart
    The desc isn't used but it is needed to make the admin interface work appropriately
    Could be used for debugging
    """

    desc = models.CharField(_("Description"), blank=True, null=True, max_length=10)
    date_time_created = models.DateTimeField(_("Creation Date"))
    customer = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_("Customer"),
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        verbose_name=_("Currency"),
        related_name="carts",
        editable=False,
        null=True,
        blank=True,
    )

    objects = CartManager()

    class Meta:
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")

    def __str__(self):
        return "Shopping Cart (%s)" % self.date_time_created

    def __iter__(self):
        return iter(self.cartitem_set.all())

    def __len__(self):
        return self.cartitem_set.count()

    def save(self, *args, **kwargs):
        """Ensure we have a date_time_created before saving the first time."""
        if not self.pk:
            self.date_time_created = timezone.now()

        if self.currency is None:
            self.currency = Currency.objects.get_primary()

        super(Cart, self).save(*args, **kwargs)

    def add_item(self, chosen_item, number_added, details=None):
        if details is None:
            details = {}
        alreadyInCart = False
        # Custom Products will not be added, they will each get their own line item
        if "CustomProduct" in chosen_item.get_subtypes():
            item_to_modify = CartItem(cart=self, product=chosen_item, quantity=0)
        else:
            item_to_modify = CartItem(cart=self, product=chosen_item, quantity=0)
            for similarItem in self.cartitem_set.filter(product__id=chosen_item.id):
                looksTheSame = len(details) == similarItem.details.count()
                if looksTheSame:
                    for detail in details:
                        try:
                            similarItem.details.get(
                                name=detail["name"],
                                value=detail["value"],
                                price_change=detail["price_change"],
                            )
                        except CartItemDetails.DoesNotExist:
                            looksTheSame = False
                if looksTheSame:
                    item_to_modify = similarItem
                    alreadyInCart = True
                    break

        signals.satchmo_cart_add_verify.send(
            self,
            cart=self,
            cartitem=item_to_modify,
            added_quantity=number_added,
            details=details,
        )

        if not alreadyInCart:
            self.cartitem_set.add(item_to_modify, bulk=False)

        item_to_modify.quantity += number_added
        item_to_modify.save()
        if not alreadyInCart:
            for data in details:
                item_to_modify.add_detail(data)

        return item_to_modify

    def remove_item(self, chosen_item_id, number_removed):
        item_to_modify = self.cartitem_set.get(id=chosen_item_id)
        item_to_modify.quantity -= number_removed
        if item_to_modify.quantity <= 0:
            item_to_modify.delete()
        self.save()

    def empty(self):
        for item in self.cartitem_set.all():
            item.delete()
        self.save()

    def get_shipment_list(self):
        """Return a list of shippable products, where each item is split into
        multiple elements, one for each quantity."""
        items = []
        for cartitem in self.cartitem_set.all():
            if cartitem.is_shippable:
                p = cartitem.product
                for __ in range(0, cartitem.quantity):
                    items.append(p)
        return items

    def not_enough_stock(self):
        """ Check that items are in stock
            Return a list of out of stock items, or an empty list
        """
        not_enough_stock = []
        config = Config.objects.get_current()
        print(config.no_stock_checkout)
        if config.no_stock_checkout is False:
            for cart_item in self.cartitem_set.all():
                if not cart_item.has_enough_stock():
                    not_enough_stock.append(cart_item)
        return not_enough_stock

    @property
    def is_shippable(self):
        """Return whether the cart contains shippable items."""
        for cartitem in self.cartitem_set.all():
            if cartitem.is_shippable:
                return True
        return False

    @property
    def numItems(self):
        itemCount = 0
        for item in self.cartitem_set.all():
            itemCount += item.quantity
        return itemCount

    @property
    def total(self):
        total = Decimal("0")
        for item in self.cartitem_set.all():
            total += item.line_total
        return total

    @property
    def display_total(self):
        return money_format(self.total, self.currency.iso_4217_code)


class NullCartItem(object):
    def __init__(self, itemid):
        self.id = itemid
        self.quantity = 0
        self.line_total = 0


class CartItem(models.Model):
    """
    An individual item in the cart
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name=_("Cart"))
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    quantity = models.IntegerField(_("Quantity"))

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ("id",)

    def __str__(self):
        return "%s X %s @ %s" % (self.quantity, self.product.name, self.unit_price)

    @property
    def unit_price(self):
        # Get the qty discount price as the unit price for the line.
        self.qty_price = self.get_qty_price(self.quantity)
        self.detail_price = self.get_detail_price()

        # send signal to possibly adjust the unit price
        signals.satchmo_cartitem_price_query.send(self, cartitem=self)

        price = self.qty_price + self.detail_price
        if self.cart.currency:
            price = convert_to_currency(price, self.cart.currency.iso_4217_code)

        # Clean up temp vars
        del self.qty_price
        del self.detail_price

        return price

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def display_line_total(self):
        return money_format(self.line_total, self.cart.currency.iso_4217_code)

    def get_detail_price(self):
        """Get the delta price based on detail modifications"""
        delta = Decimal("0")
        if self.has_details:
            for detail in self.details.all():
                if detail.price_change and detail.value:
                    delta += detail.price_change
        return delta

    def get_qty_price(self, qty):
        """Get the price for for each unit before any detail modifications"""
        return self.product.get_qty_price(qty)

    def _get_description(self):
        return self.product.name

    description = property(_get_description)

    def _is_shippable(self):
        return self.product.is_shippable

    is_shippable = property(fget=_is_shippable)

    def add_detail(self, data):
        detl = CartItemDetails(
            cartitem=self,
            name=data["name"],
            value=data["value"],
            sort_order=data["sort_order"],
            price_change=data["price_change"],
        )
        detl.save()
        # self.details.add(detl)

    def _has_details(self):
        """
        Determine if this specific item has more detail
        """
        return self.details.count() > 0

    has_details = property(_has_details)

    def has_enough_stock(self):
        """
        Check to see that there is enough stock to fulfill the order
        """
        config = Config.objects.get_current()
        if config.no_stock_checkout or self.quantity <= self.product.items_in_stock:
            return True
        else:
            return False


class CartItemDetails(models.Model):
    """
    An arbitrary detail about a cart item.
    """

    cartitem = models.ForeignKey(
        CartItem, on_delete=models.CASCADE, related_name="details"
    )
    value = models.TextField(_("detail"))
    name = models.CharField(_("name"), max_length=100)
    price_change = models.DecimalField(
        _("Item Detail Price Change"),
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
    )
    sort_order = models.IntegerField(
        _("Sort Order"), help_text=_("The display order for this group.")
    )

    class Meta:
        ordering = ("sort_order",)
        verbose_name = _("Cart Item Detail")
        verbose_name_plural = _("Cart Item Details")


ORDER_CHOICES = (
    ("Online", _("Online")),
    ("In Person", _("In Person")),
    ("Show", _("Show")),
)


class Status(models.Model):
    status = models.CharField(_("Status"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    notify = models.BooleanField(
        _("Notify"), help_text="Notify the user on status update", default=True
    )
    display = models.BooleanField(
        _("Display"),
        help_text="Show orders of this status in the admin area home page",
        default=True,
    )
    time_stamp = models.DateTimeField(_("Time stamp"), default=timezone.now)

    def __str__(self):
        return self.status

    def orders(self):
        """ Get all orders of this status """
        return Order.objects.by_latest_status(self)

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Statuses")


class OrderQuerySet(models.QuerySet):
    def live(self):
        return self.filter(frozen=False)

    def unfulfilled(self):
        return self.by_latest_status(
            "Processing", exclude_status="Payment Created"
        ).filter(frozen=True, fulfilled=False)

    def by_latest_status(self, status, exclude_status=None):
        """Return orders with their latest status matching `status`.

        It is possible to exclude a payment status for the latest
        search. This is useful for "Payment Created" or similar that
        can be created asynchronoulsy and appear after the
        "Processing" status.

        """
        if isinstance(status, str):
            status = Status.objects.get(status=status)
        newest_status = OrderStatus.objects.filter(order=OuterRef("pk")).order_by(
            "-time_stamp"
        )

        if exclude_status:
            if isinstance(exclude_status, str):
                newest_status = newest_status.exclude(status__status=exclude_status)
            elif isinstance(exclude_status, list):
                newest_status = newest_status.exclude(status__status__in=exclude_status)

        return self.annotate(
            status=Subquery(newest_status.values("status")[:1])
        ).filter(status=status.id)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def live(self):
        return self.get_queryset().live()

    def unfulfilled(self):
        return self.get_queryset().unfulfilled()

    def by_latest_status(self, status):
        return self.get_queryset().by_latest_status(status)

    def from_request(self, request):
        """Get the order from the session

        Returns:
        - Order object or None
        """

        order = None
        if "orderID" in request.session:
            try:
                order = Order.objects.live().get(id=request.session["orderID"])
            except Order.DoesNotExist:
                pass

            if order is None:
                del request.session["orderID"]

        if order is not None and request.user != order.contact.user:
            order = None

        if order is None:
            raise Order.DoesNotExist()

        return order

    def remove_partial_order(self, request):
        """Delete cart from request if it exists and is incomplete (has no status)"""
        try:
            order = Order.objects.from_request(request)
            if not order.status:
                del request.session["orderID"]
                log.info("Deleting incomplete order #%i from database", order.id)
                order.delete()
                return True
        except Order.DoesNotExist:
            pass
        return False


class Order(models.Model):
    """
    Orders contain a copy of all the information at the time the order was
    placed.
    """

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, verbose_name=_("Contact"), editable=False
    )
    frozen = models.BooleanField(default=False)
    fulfilled = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(_("Timestamp"), editable=False)
    notes = models.TextField(_("Notes"), blank=True, null=True, default="")
    method = models.CharField(
        _("Order method"), choices=ORDER_CHOICES, max_length=200, blank=True
    )
    discount_code = models.CharField(
        _("Discount Code"),
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Coupon Code"),
    )

    ship_addressee = models.CharField(_("Addressee"), max_length=61, blank=True)
    ship_street1 = models.CharField(_("Street"), max_length=80, blank=True)
    ship_street2 = models.CharField(_("Street"), max_length=80, blank=True)
    ship_city = models.CharField(_("City"), max_length=50, blank=True)
    ship_state = models.CharField(_("State"), max_length=50, blank=True)
    ship_postal_code = models.CharField(_("Post Code"), max_length=30, blank=True)
    ship_country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, related_name="ship_country"
    )
    bill_addressee = models.CharField(_("Addressee"), max_length=61, blank=True)
    bill_street1 = models.CharField(_("Street"), max_length=80, blank=True)
    bill_street2 = models.CharField(_("Street"), max_length=80, blank=True)
    bill_city = models.CharField(_("City"), max_length=50, blank=True)
    bill_state = models.CharField(_("State"), max_length=50, blank=True)
    bill_postal_code = models.CharField(_("Post Code"), max_length=30, blank=True)
    bill_country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, related_name="bill_country"
    )

    shipping_description = models.CharField(
        _("Shipping Description"), max_length=200, blank=True, null=True
    )
    shipping_method = models.CharField(
        _("Shipping Method"), max_length=200, blank=True, null=True
    )
    shipping_model = ShippingChoiceCharField(
        _("Shipping Models"), max_length=30, blank=True, null=True
    )
    estimated_delivery_min_days = models.PositiveIntegerField(
        _("Minimum number of days after shipping until delivery"), default=1
    )
    estimated_delivery_expected_days = models.PositiveIntegerField(
        _("Usual number of days after shipping until delivery"), default=7
    )
    estimated_delivery_max_days = models.PositiveIntegerField(
        _("Maximum number of days after shipping until delivery"), default=25
    )
    shipping_signed_for = models.BooleanField(_("Signed For"), default=False)
    shipping_tracked = models.BooleanField(_("Tracked"), default=False)
    tracking_number = models.CharField(
        _("Tracking Number"), max_length=64, blank=True, null=True
    )
    tracking_url = models.URLField(_("Tracking URL"), blank=True, null=True)
    shipping_postage_speed = models.PositiveIntegerField(
        _("Postage Speed"), choices=POSTAGE_SPEED_CHOICES, default=STANDARD
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        verbose_name=_("Currency"),
        related_name="orders",
        editable=False,
    )
    exchange_rate = models.DecimalField(
        _("Exchange Rate"),
        help_text=_("Rate from primary currency"),
        max_digits=6,
        decimal_places=4,
        editable=False,
        default=Decimal("1.00"),
    )
    sub_total = models.DecimalField(
        _("Subtotal"), max_digits=18, decimal_places=2, blank=True, null=True
    )
    shipping_cost = models.DecimalField(
        _("Shipping Cost"), max_digits=18, decimal_places=2, blank=True, null=True
    )
    shipping_discount = models.DecimalField(
        _("Shipping Discount"), max_digits=18, decimal_places=2, blank=True, null=True
    )
    tax = models.DecimalField(
        _("Tax"), max_digits=18, decimal_places=2, blank=True, null=True
    )
    discount = models.DecimalField(
        _("Discount amount"), max_digits=18, decimal_places=2, blank=True, null=True
    )
    total = models.DecimalField(
        _("Total"), max_digits=18, decimal_places=2, blank=True, null=True
    )
    refund = models.DecimalField(
        _("Refund"),
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("The amount refunded in the currency of the order"),
    )

    objects = OrderManager()

    class Meta:
        verbose_name = _("Product Order")
        verbose_name_plural = _("Product Orders")

    def __str__(self):
        return "Order #%s: %s" % (self.id, self.contact.full_name)

    def save(self, *args, **kwargs):
        """
        Copy addresses from contact. If the order has just been created, set
        the create_date.
        """
        if self.pk is None:
            self.copy_addresses()
            self.time_stamp = timezone.now()
        # Call the "real" save() method.
        super(Order, self).save(*args, **kwargs)

    def freeze(self):
        self.frozen = True
        self.time_stamp = timezone.now()

    def add_status(self, status=None, notes="", status_notify_by_default=False):
        order_status = OrderStatus()
        if not status:
            if self.order_states.count() > 0:
                status_obj = self.status
            else:
                status_obj, __ = Status.objects.get_or_create(status="Pending")
        else:
            status_obj, created = Status.objects.get_or_create(status=status)
            if created:
                status_obj.notify = status_notify_by_default
                status_obj.save()

        order_status.status = status_obj
        order_status.notes = notes
        order_status.time_stamp = timezone.now()
        order_status.order = self
        order_status.save()
        return order_status

    @cached_property
    def status(self):
        return self.order_states.last()

    def add_variable(self, key, value):
        """Add an OrderVariable, used for misc stuff that is just too small to get its own field"""
        try:
            v = self.variables.get(key__exact=key)
            v.value = value
        except OrderVariable.DoesNotExist:
            v = OrderVariable(order=self, key=key, value=value)
        v.save()

    def get_variable(self, key, default=None):
        qry = self.variables.filter(key__exact=key)
        ct = qry.count()
        if ct == 0:
            return default
        else:
            return qry[0]

    def copy_addresses(self):
        """
        Copy the addresses so we know what the information was at time of order.
        """
        shipaddress = self.contact.shipping_address
        billaddress = self.contact.billing_address
        self.ship_addressee = shipaddress.addressee
        self.ship_street1 = shipaddress.street1
        self.ship_street2 = shipaddress.street2
        self.ship_city = shipaddress.city
        self.ship_state = shipaddress.state
        self.ship_postal_code = shipaddress.postal_code
        self.ship_country = shipaddress.country
        self.bill_addressee = billaddress.addressee
        self.bill_street1 = billaddress.street1
        self.bill_street2 = billaddress.street2
        self.bill_city = billaddress.city
        self.bill_state = billaddress.state
        self.bill_postal_code = billaddress.postal_code
        self.bill_country = billaddress.country

    def remove_all_items(self):
        """Delete all items belonging to this order."""
        for item in self.orderitem_set.all():
            item.delete()
        self.save()

    def _balance(self):
        self.force_recalculate_total(save=True)
        return self.total - self.balance_paid

    balance = property(fget=_balance)

    @property
    def balance_forward(self):
        return money_format(self.balance, self.currency.iso_4217_code)

    def _balance_paid(self):
        payments = [p.amount for p in self.payments.all()]
        if payments:
            return reduce(operator.add, payments)
        else:
            return Decimal("0.0000000000")

    balance_paid = property(_balance_paid)

    def _credit_card(self):
        """Return the credit card associated with this payment."""
        for payment in self.payments.order_by("-time_stamp"):
            try:
                if payment.creditcards.count() > 0:
                    return payment.creditcards.get()
            except payment.creditcards.model.DoesNotExist:
                pass
        return None

    credit_card = property(_credit_card)

    def _full_bill_street(self, delim="\n"):
        """
        Return both billing street entries separated by delim.
        Note - Use linebreaksbr filter to convert to html in templates.
        """
        if self.bill_street2:
            address = self.bill_street1 + delim + self.bill_street2
        else:
            address = self.bill_street1
        return mark_safe(address)

    full_bill_street = property(_full_bill_street)

    def _full_ship_street(self, delim="\n"):
        """
        Return both shipping street entries separated by delim.
        Note - Use linebreaksbr filterto convert to html in templates.
        """
        if self.ship_street2:
            address = self.ship_street1 + delim + self.ship_street2
        else:
            address = self.ship_street1
        return mark_safe(address)

    full_ship_street = property(_full_ship_street)

    def _ship_country_name(self):
        return Country.objects.get(iso2_code=self.ship_country).name

    ship_country_name = property(_ship_country_name)

    def _bill_country_name(self):
        return Country.objects.get(iso2_code=self.bill_country).name

    bill_country_name = property(_bill_country_name)

    def get_balance_remaining_url(self):
        return reverse("satchmo_balance_remaining_order", None, {"order_id": self.id})

    def _partially_paid(self):
        return self.balance_paid > Decimal("0.0000000000")

    partially_paid = property(_partially_paid)

    def _is_partially_paid(self):
        if self.total:
            balance = self.balance
            return float(balance) > 0.0 and self.balance != self.balance_paid
        else:
            return False

    is_partially_paid = property(fget=_is_partially_paid)

    def payments_completed(self):
        q = self.payments.exclude(
            transaction_id__isnull=False, transaction_id="PENDING"
        )
        return q.exclude(amount=Decimal("0.00"))

    def invoice(self):
        url = reverse(
            "satchmo_print_shipping", None, None, {"doc": "invoice", "id": self.id}
        )
        return mark_safe('<a href="%s">%s</a>' % (url, _("View")))

    invoice.allow_tags = True

    def _item_discount(self):
        """Get the discount of just the items, less the shipping discount."""
        return self.discount - self.shipping_discount

    item_discount = property(_item_discount)

    def packingslip(self):
        url = reverse(
            "satchmo_print_shipping", None, None, {"doc": "packingslip", "id": self.id}
        )
        return mark_safe('<a href="%s">%s</a>' % (url, _("View")))

    packingslip.allow_tags = True

    def recalculate_total(self, save=True):
        """Calculates sub_total, taxes and total if the order is not already partially paid."""
        if self.is_partially_paid:
            log.debug(
                "Order %i - skipping recalculate_total since product is partially paid.",
                self.id,
            )
        else:
            self.force_recalculate_total(save=save)

    def force_recalculate_total(self, save=True):
        """Calculates sub_total, taxes and total."""

        zero = Decimal("0.0000000000")

        # Find the discount code and calculate it
        discount = find_discount_for_code(self.discount_code)
        discount.calc(self)

        # Save the total discount in this Order's discount attribute
        self.discount = discount.total

        itemprices = []
        fullprices = []

        # Apply discounts to line item
        for lineitem in self.orderitem_set.all():
            lid = lineitem.id
            if lid in discount.item_discounts:
                lineitem.discount = discount.item_discounts[lid]
            else:
                lineitem.discount = zero
            if save:
                lineitem.save()

            itemprices.append(lineitem.sub_total)
            fullprices.append(lineitem.line_item_price)

        if "Shipping" in discount.item_discounts:
            self.shipping_discount = discount.item_discounts["Shipping"]
        else:
            self.shipping_discount = zero

        if itemprices:
            item_sub_total = reduce(operator.add, itemprices)
        else:
            item_sub_total = zero

        if fullprices:
            full_sub_total = reduce(operator.add, fullprices)
        else:
            full_sub_total = zero

        self.sub_total = full_sub_total

        taxProcessor = get_tax_processor(self)
        totaltax, taxrates = taxProcessor.process()
        self.tax = totaltax

        # clear old taxes
        for taxdetl in self.taxes.all():
            taxdetl.delete()

        for taxdesc, taxamt in list(taxrates.items()):
            taxdetl = OrderTaxDetail(
                order=self, tax=taxamt, description=taxdesc, method=taxProcessor.method
            )
            taxdetl.save()

        log.debug(
            "Order #%i, recalc: sub_total=%s, shipping=%s, discount=%s, tax=%s",
            self.id,
            money_format(item_sub_total, self.currency.iso_4217_code),
            money_format(self.shipping_sub_total, self.currency.iso_4217_code),
            money_format(self.discount, self.currency.iso_4217_code),
            money_format(self.tax, self.currency.iso_4217_code),
        )

        self.total = Decimal(item_sub_total + self.shipping_sub_total + self.tax)

        if save:
            self.save()

    def shippinglabel(self):
        url = reverse(
            "satchmo_print_shipping",
            None,
            None,
            {"doc": "shippinglabel", "id": self.id},
        )
        return mark_safe('<a href="%s">%s</a>' % (url, _("View")))

    shippinglabel.allow_tags = True

    def _convert_to_primary(self, value):
        if value is None:
            value = Decimal("0.00")

        if self.currency.primary is False:
            reverse_exchange_rate = Decimal("1.00") / self.exchange_rate
            value = value * reverse_exchange_rate
        return value

    def sub_total_in_primary_currency(self):
        """Returns the sub total value of the order in the primary
        currency at the exchange rate of the order

        """
        return self._convert_to_primary(self.sub_total)

    def shipping_cost_in_primary_currency(self):
        """Returns the shipping cost of the order in the primary
        currency at the exchange rate of the order

        """
        return self._convert_to_primary(self.shipping_cost)

    def refund_in_primary_currency(self):
        """Returns the refund value of the order in the primary
        currency at the exchange rate of the order

        """
        refund_total = Decimal("0.00")
        for refund in self.refunds.all():
            refund_total += refund.amount_in_primary_currency()

        return refund_total

    def total_in_primary_currency(self):
        """Returns the total value of the order in the primary
        currency at the exchange rate of the order

        """
        return self._convert_to_primary(self.total)

    @property
    def display_total(self):
        """ Display the order total in the correct currency """
        return money_format(self.total, self.currency.iso_4217_code)

    @property
    def display_tax(self):
        return money_format(self.tax, self.currency.iso_4217_code)

    @property
    def display_refund(self):
        return money_format(self.refund, self.currency.iso_4217_code)

    @property
    def display_sub_total(self):
        return money_format(self.sub_total, self.currency.iso_4217_code)

    @property
    def display_sub_total_with_tax(self):
        return money_format(self.sub_total_with_tax(), self.currency.iso_4217_code)

    @property
    def display_balance(self):
        return money_format(self.balance, self.currency.iso_4217_code)

    @property
    def display_balance_paid(self):
        return money_format(self.balance_paid, self.currency.iso_4217_code)

    @property
    def display_shipping_sub_total(self):
        return money_format(self.shipping_sub_total, self.currency.iso_4217_code)

    @property
    def display_shipping_with_tax(self):
        return money_format(self.shipping_with_tax, self.currency.iso_4217_code)

    @property
    def display_shipping_cost(self):
        return money_format(self.shipping_cost, self.currency.iso_4217_code)

    @property
    def display_discount(self):
        return money_format(self.discount, self.currency.iso_4217_code)

    @property
    def display_shipping_discount(self):
        return money_format(self.shipping_discount, self.currency.iso_4217_code)

    @property
    def display_item_discount(self):
        return money_format(self.item_discount, self.currency.iso_4217_code)

    def order_success(self):
        """Run each item's order_success method."""
        log.info("Order success: %s", self)
        for orderitem in self.orderitem_set.all():
            subtype = orderitem.product.get_subtype_with_attr("order_success")
            if subtype:
                subtype.order_success(self, orderitem)
        if self.is_downloadable:
            self.add_status("Shipped", _("Order immediately available for download"))

        send_owner_order_notice(self)

        signals.order_success.send(self, order=self)

    def _paid_in_full(self):
        """True if total has been paid"""
        return self.balance <= 0

    paid_in_full = property(fget=_paid_in_full)

    def _has_downloads(self):
        """Determine if there are any downloadable products on this order"""
        if self.downloadlink_set.count() > 0:
            return True
        return False

    has_downloads = property(_has_downloads)

    def _is_downloadable(self):
        """Determine if all products on this order are downloadable"""
        for orderitem in self.orderitem_set.all():
            if not orderitem.product.is_downloadable:
                return False
        return True

    is_downloadable = property(_is_downloadable)

    def _is_shippable(self):
        """Determine if we will be shipping any items on this order """
        for orderitem in self.orderitem_set.all():
            if orderitem.is_shippable:
                return True
        return False

    is_shippable = property(_is_shippable)

    @property
    def shipping_sub_total(self):
        if self.shipping_cost is None:
            self.shipping_cost = Decimal("0.00")
        if self.shipping_discount is None:
            self.shipping_discount = Decimal("0.00")
        return self.shipping_cost - self.shipping_discount

    def _shipping_tax(self):
        rates = self.taxes.filter(description__iexact="shipping")
        if rates.count() > 0:
            tax = reduce(operator.add, [t.tax for t in rates])
        else:
            tax = Decimal("0.0000000000")
        return tax

    shipping_tax = property(_shipping_tax)

    def _shipping_with_tax(self):
        return self.shipping_sub_total + self.shipping_tax

    shipping_with_tax = property(_shipping_with_tax)

    @property
    def shipped(self):
        """ Returns True if the order has a Shipped status """
        return self.order_states.filter(status__status="Shipped").exists()

    def shipping_date(self):
        """Returns the shipping date.

        If the order has not shipped yet, it will do it's best to
        estimate the shipping date base off of business days and
        before/after midday (assumes orders placed before midday
        working days are shipped the same day).

        """
        if self.shipped:
            # Most recent shipped status
            shipped = self.order_states.filter(status__status="Shipped").order_by(
                "-time_stamp"
            )[0]
            ship_date = shipped.time_stamp.date()
        elif (
            self.time_stamp.isoweekday() >= 6  # Weekend 6th and 7th day of week
            or self.time_stamp.hour >= 12
        ):  # Midday
            # Ships next business day
            ship_date = workday(self.time_stamp, 1).date()
        else:
            # Ships same day
            ship_date = self.time_stamp.date()
        return ship_date

    def estimated_delivery_min_date(self):
        return workday(self.shipping_date(), self.estimated_delivery_min_days)

    def estimated_delivery_expected_date(self):
        return workday(self.shipping_date(), self.estimated_delivery_expected_days + 1)

    def estimated_delivery_max_date(self):
        return workday(self.shipping_date(), self.estimated_delivery_max_days + 1)

    def sub_total_with_tax(self):
        return reduce(
            operator.add, [o.total_with_tax for o in self.orderitem_set.all()]
        )

    def validate(self, request):
        """
        Return whether the order is valid.
        Not guaranteed to be side-effect free.
        """
        valid = True
        for orderitem in self.orderitem_set.all():
            for subtype_name in orderitem.product.get_subtypes():
                subtype = getattr(orderitem.product, subtype_name.lower())
                validate_method = getattr(subtype, "validate_order", None)
                if validate_method:
                    valid = valid and validate_method(request, self, orderitem)
        return valid

    @property
    def weight(self):
        total_weight = Decimal("0.00")
        for item in self.orderitem_set.all():
            total_weight += item.weight
        return total_weight

    @property
    def verification_hash(self):
        value = "{id} {user_id}".format(id=self.id, user_id=self.contact_id)
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"), value.encode("utf-8"), "md5"
        ).hexdigest()

    def verify_hash(self, verification_hash):
        if hasattr(hmac, "compare_digest"):
            return hmac.compare_digest(
                str(self.verification_hash), str(verification_hash)
            )
        else:
            # Avoid timing attacks
            sleep_for = random.random() / 100
            time.sleep(sleep_for)
            return self.verification_hash == verification_hash


class OrderItem(models.Model):
    """
    A line item on an order.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_("Order"))
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    quantity = models.IntegerField(_("Quantity"))
    unit_price = models.DecimalField(_("Unit price"), max_digits=18, decimal_places=2)
    unit_tax = models.DecimalField(
        _("Unit tax"), max_digits=18, decimal_places=2, null=True
    )
    line_item_price = models.DecimalField(
        _("Line item price"), max_digits=18, decimal_places=2
    )
    tax = models.DecimalField(
        _("Line item tax"), max_digits=18, decimal_places=2, null=True
    )
    expire_date = models.DateField(
        _("Subscription End"),
        help_text=_("Subscription expiration date."),
        blank=True,
        null=True,
    )
    completed = models.BooleanField(_("Completed"), default=False)
    stock_updated = models.BooleanField(_("Stock Updated"), default=False)
    discount = models.DecimalField(
        _("Line item discount"), max_digits=18, decimal_places=2, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Order Line Item")
        verbose_name_plural = _("Order Line Items")
        ordering = ("id",)

    def __str__(self):
        return self.product.name

    def _get_category(self):
        return self.product.get_category.name

    category = property(_get_category)

    def _is_shippable(self):
        return self.product.is_shippable

    is_shippable = property(fget=_is_shippable)

    @cached_property
    def currency_code(self):
        return self.order.currency.iso_4217_code

    @property
    def display_unit_price(self):
        return money_format(self.unit_price, self.currency_code)

    @property
    def display_unit_price_with_tax(self):
        return money_format(self.unit_price_with_tax, self.currency_code)

    @property
    def display_discount(self):
        return money_format(self.discount, self.currency_code)

    @property
    def display_sub_total(self):
        return money_format(self.sub_total, self.currency_code)

    @property
    def display_total_with_tax(self):
        return money_format(self.total_with_tax, self.currency_code)

    @property
    def sub_total(self):
        if self.discount:
            price = self.line_item_price - self.discount
        else:
            price = self.line_item_price

        return price

    @property
    def total_with_tax(self):
        return self.sub_total + self.tax

    @property
    def unit_price_with_tax(self):
        return self.unit_price + self.unit_tax

    def _get_description(self):
        return self.product.name

    description = property(_get_description)

    def save(self, *args, **kwargs):
        self.update_tax()
        super(OrderItem, self).save(*args, **kwargs)

    def update_tax(self):
        taxclass = self.product.taxClass
        processor = get_tax_processor(order=self.order)
        self.unit_tax = processor.by_price(taxclass, self.unit_price)
        self.tax = processor.by_orderitem(self)

    @property
    def weight(self):
        return self.product.weight * self.quantity


class OrderItemDetail(models.Model):
    """
    Name, value pair and price delta associated with a specific item in an order
    """

    item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, verbose_name=_("Order Item")
    )
    name = models.CharField(_("Name"), max_length=100)
    value = models.CharField(_("Value"), max_length=255)
    price_change = models.DecimalField(
        _("Price Change"), max_digits=18, decimal_places=2, blank=True, null=True
    )
    sort_order = models.IntegerField(
        _("Sort Order"), help_text=_("The display order for this group.")
    )

    def __str__(self):
        return "%s - %s,%s" % (self.item, self.name, self.value)

    class Meta:
        verbose_name = _("Order Item Detail")
        verbose_name_plural = _("Order Item Details")
        ordering = ("sort_order",)


class DownloadLink(models.Model):
    downloadable_product = models.ForeignKey(
        DownloadableProduct,
        on_delete=models.CASCADE,
        verbose_name=_("Downloadable product"),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name=_("Order"))
    key = models.CharField(_("Key"), max_length=40)
    num_attempts = models.IntegerField(_("Number of attempts"))
    time_stamp = models.DateTimeField(
        _("Time stamp"), default=timezone.now, editable=True
    )
    active = models.BooleanField(_("Active"), default=True)

    def _attempts_left(self):
        return self.downloadable_product.num_allowed_downloads - self.num_attempts

    attempts_left = property(_attempts_left)

    def is_valid(self):
        # Check num attempts and expire_minutes
        if not self.downloadable_product.active:
            return (False, _("This download is no longer active"))
        if self.num_attempts >= self.downloadable_product.num_allowed_downloads:
            return (False, _("You have exceeded the number of allowed downloads."))
        expire_time = (
            datetime.timedelta(minutes=self.downloadable_product.expire_minutes)
            + self.time_stamp
        )
        if timezone.now() > expire_time:
            return (False, _("This download link has expired."))
        return (True, "")

    def get_absolute_url(self):
        return reverse(
            "satchmo.shop.views.download.process", (), {"download_key": self.key}
        )

    def get_full_url(self):
        url = reverse("satchmo_download_process", kwargs={"download_key": self.key})
        return "https://%s%s" % (Site.objects.get_current(), url)

    def save(self, *args, **kwargs):
        """
        Set the initial time stamp
        """
        super(DownloadLink, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s" % (self.downloadable_product.product.slug, self.time_stamp)

    def _product_name(self):
        return "%s" % (self.downloadable_product.product.name)

    product_name = property(_product_name)

    class Meta:
        verbose_name = _("Download Link")
        verbose_name_plural = _("Download Links")


class OrderStatus(models.Model):
    """
    An order will have multiple statuses as it moves its way through processing.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("Order"),
        related_name="order_states",
    )
    status = models.ForeignKey(
        Status, on_delete=models.CASCADE, verbose_name=_("Status")
    )
    notes = models.TextField(_("Notes"), blank=True)
    time_stamp = models.DateTimeField(
        _("Timestamp"), auto_now_add=True, editable=False, db_index=True
    )

    class Meta:
        verbose_name = _("Order Status")
        verbose_name_plural = _("Order Statuses")
        ordering = ("time_stamp",)

    def __str__(self):
        return self.status.status

    def save(self, *args, **kwargs):
        # Should we send a notification. Just record True or False,
        # actually handle the notification at the end of this function
        send_order_notification = False
        if self.id is None:
            send_order_notification = True

        super(OrderStatus, self).save(*args, **kwargs)

        # Actually send the notification
        if send_order_notification:
            send_order_update(self)


class OrderPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment = PaymentChoiceCharField(_("Payment Method"), max_length=25, blank=True)
    amount = models.DecimalField(
        _("amount"), max_digits=18, decimal_places=2, blank=True, null=True
    )

    exchange_rate = models.DecimalField(
        _("Exchange Rate"),
        help_text=_("Rate from primary currency at time of payment"),
        max_digits=6,
        decimal_places=4,
        editable=False,
        default=Decimal("1.00"),
    )

    time_stamp = models.DateTimeField(
        _("timestamp"), default=timezone.now, editable=True
    )
    transaction_id = models.CharField(
        _("Transaction ID"), max_length=64, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Order Payment")
        verbose_name_plural = _("Order Payments")

    def __str__(self):
        if self.id is not None:
            return "Order payment #%i" % self.id
        else:
            return "Order payment (unsaved)"

    @property
    def credit_card(self):
        """Return the credit card associated with this payment."""
        try:
            return self.creditcards.get()
        except self.creditcards.model.DoesNotExist:
            return None

    @property
    def amount_total(self):
        return self.display_total

    @property
    def currency(self):
        return self.order.currency

    @property
    def display_total(self):
        return money_format(self.amount, self.currency.iso_4217_code)


class OrderRefund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    payment = PaymentChoiceCharField(_("Payment Method"), max_length=25, blank=True)
    amount = models.DecimalField(_("Amount"), max_digits=18, decimal_places=2)
    exchange_rate = models.DecimalField(
        _("Exchange Rate"),
        help_text=_("Rate from primary currency  at time of refund"),
        max_digits=6,
        decimal_places=4,
        editable=False,
        default=Decimal("1.00"),
    )

    timestamp = models.DateTimeField(
        _("Timestamp"), default=timezone.now, editable=True
    )
    transaction_id = models.CharField(
        _("Transaction ID"), max_length=64, blank=True, null=True
    )

    class Meta:
        verbose_name = _("Order Refund")
        verbose_name_plural = _("Order Refunds")

    def __str__(self):
        if self.id is not None:
            return "Order refund #{id} - {amount}".format(
                id=self.id, amount=self.display_amount
            )
        else:
            return "Order refund (unsaved)"

    def save(self, *args, **kwargs):
        if self.id is None:
            # If this is the first time saving this payment, check if
            # the exchange rate is default (1.00), if it is, try to
            # get the latest exchange rate
            if self.exchange_rate == Decimal("1.00"):
                try:
                    self.exchange_rate = self.currency.exchange_rates.latest().rate
                except ExchangeRate.DoesNotExist:
                    self.exchange_rate = Decimal("1.00")

            # If this is the first time saving this payment, add it to
            # the orders refund attribute
            if self.order.refund:
                self.order.refund += self.amount
            else:
                self.order.refund = self.amount
            self.order.save()
        return super(OrderRefund, self).save(*args, **kwargs)

    @property
    def currency(self):
        return self.order.currency

    @property
    def display_amount(self):
        return money_format(self.amount, self.currency.iso_4217_code)

    def amount_in_primary_currency(self):
        if self.amount is None:
            amount = Decimal("0.00")
        else:
            amount = self.amount

        if self.currency.primary is False:
            reverse_exchange_rate = Decimal("1.00") / self.exchange_rate
            amount = (amount * reverse_exchange_rate).quantize(
                Decimal(".01"), ROUND_HALF_EVEN
            )

        return amount


class OrderVariable(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="variables")
    key = models.SlugField(_("key"))
    value = models.CharField(_("value"), max_length=100)

    class Meta:
        ordering = ("key",)
        verbose_name = _("Order variable")
        verbose_name_plural = _("Order variables")

    def __str__(self):
        if len(self.value) > 10:
            v = self.value[:10] + "..."
        else:
            v = self.value
        return "OrderVariable: %s=%s" % (self.key, v)


class OrderTaxDetail(models.Model):
    """A tax line item"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="taxes")
    method = models.CharField(_("Model"), max_length=50)
    description = models.CharField(_("Description"), max_length=50, blank=True)
    tax = models.DecimalField(
        _("Tax"), max_digits=18, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        if self.description:
            return "Tax: %s %s" % (self.description, self.tax)
        else:
            return "Tax: %s" % self.tax

    class Meta:
        verbose_name = _("Order tax detail")
        verbose_name_plural = _("Order tax details")
        ordering = ("id",)


def _remove_order_on_cart_update(request=None, cart=None, **kwargs):
    if request:
        log.debug("caught cart changed signal - remove_order_on_cart_update")
        Order.objects.remove_partial_order(request)


def _recalc_total_on_contact_change(contact=None, **kwargs):
    log.debug("Recalculating all contact orders not in process")
    orders = Order.objects.live().filter(contact=contact)
    log.debug("Found %i orders to recalc", len(orders))
    for order in orders:
        order.copy_addresses()
        order.recalculate_total()


def _create_download_link(product=None, order=None, subtype=None, **kwargs):
    if product and order and subtype == "download":
        new_link = DownloadLink(
            downloadable_product=product,
            order=order,
            key=product.create_key(),
            num_attempts=0,
        )
        new_link.save()
    else:
        log.debug(
            "ignoring subtype_order_success signal, looking for download product, got %s",
            subtype,
        )


signals.satchmo_cart_changed.connect(_remove_order_on_cart_update, sender=None)
satchmo_contact_location_changed.connect(_recalc_total_on_contact_change, sender=None)
product_signals.subtype_order_success.connect(_create_download_link, sender=None)
