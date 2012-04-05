"""
Configuration items for the shop.
Also contains shopping cart and related classes.
"""
import datetime
import logging
import operator
from decimal import Decimal

from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import force_unicode
from django.core import urlresolvers
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from satchmo import caching
from satchmo.configuration import ConfigurationSettings, config_value
from satchmo.contact.models import Contact
from satchmo.contact.signals import satchmo_contact_location_changed
from satchmo.l10n.models import Country
from satchmo.l10n.utils import money_format
from satchmo.payment.fields import PaymentChoiceCharField
from satchmo.product import signals as product_signals
from satchmo.product.models import Product, DownloadableProduct
from satchmo.shipping.fields import ShippingChoiceCharField
from satchmo.tax.utils import get_tax_processor
from satchmo.shop import signals
from satchmo.shop.notification import order_success_listener, send_order_update_notice
from satchmo.discount.utils import find_discount_for_code

log = logging.getLogger('satchmo.shop.models')


class NullConfig(object):
    """Standin for a real config when we don't have one yet."""

    def __init__(self):
        self.store_name = self.store_description = _("Test Store")
        self.store_email = self.street1 = self.street2 = self.city = self.state = self.postal_code = self.phone = ""
        self.site = self.country = None
        self.no_stock_checkout = False
        self.in_country_only = True
        self.sales_country = None

    def _options(self):
        return ConfigurationSettings()

    options = property(fget=_options)

    def __str__(self):
        return "Test Store - no configured store exists!"


class ConfigManager(models.Manager):
    def get_current(self, site=None):
        """Convenience method to get the current shop config"""
        if not site:
            site = Site.objects.get_current()

        site = site.id

        try:
            shop_config = caching.cache_get("Config", site)
        except caching.NotCachedError, nce:
            try:
                shop_config = self.get(site__id__exact=site)
                caching.cache_set(nce.key, value=shop_config)
            except Config.DoesNotExist:
                log.warning("No Shop Config found, using test shop config for site=%s.", site)
                shop_config = NullConfig()

        return shop_config


class Config(models.Model):
    """
    Used to store specific information about a store.  Also used to
    configure various store behaviors
    """
    site = models.OneToOneField(Site, verbose_name=_("Site"), primary_key=True)
    store_name = models.CharField(_("Store Name"),max_length=100, unique=True)
    store_description = models.TextField(_("Description"), blank=True, null=True)
    store_email = models.EmailField(_("Email"), blank=True, null=True)
    street1=models.CharField(_("Street"),max_length=50, blank=True, null=True)
    street2=models.CharField(_("Street"), max_length=50, blank=True, null=True)
    city=models.CharField(_("City"), max_length=50, blank=True, null=True)
    state=models.CharField(_("State"), max_length=30, blank=True, null=True)
    postal_code=models.CharField(_("Post Code"), blank=True, null=True, max_length=9)
    country=models.ForeignKey(Country, blank=True, null=False, verbose_name=_('Country'))
    phone = models.CharField(_("Phone Number"), blank=True, null=True, max_length=12)
    no_stock_checkout = models.BooleanField(_("Purchase item not in stock?"), default=True)
    in_country_only = models.BooleanField(_("Only sell to in-country customers?"), default=True)
    sales_country = models.ForeignKey(Country, blank=True, null=True,
                                     related_name='sales_country',
                                     verbose_name=_("Default country for customers"))
    shipping_countries = models.ManyToManyField(Country, blank=True, verbose_name=_("Shipping Countries"), related_name="shop_configs")

    objects = ConfigManager()

    def _options(self):
        return ConfigurationSettings()

    options = property(fget=_options)

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


    def _base_url(self, secure=False):
        prefix = "http"
        if secure:
            prefix += "s"
        return prefix + "://" + self.site.domain

    base_url = property(fget=_base_url)

    def save(self, *args, **kwargs):
        caching.cache_delete("Config", self.site.id)
        # ensure the default country is in shipping countries
        mycountry = self.country

        if mycountry:
            if not self.sales_country:
                log.debug("%s: No sales_country set, adding country of store, '%s'", self, mycountry)
                self.sales_country = mycountry

# This code doesn't work when creating a new site. At the time of creation, all of the necessary relationships
# aren't setup. I modified the load_store code so that it would create this relationship manually when running
# with sample data. This is a bit of a django limitation so I'm leaving this in here for now. - CBM
#            salescountry = self.sales_country
#            try:
#                need = self.shipping_countries.get(pk=salescountry.pk)
#            except Country.DoesNotExist:
#                log.debug("%s: Adding default country '%s' to shipping countries", self, salescountry.iso2_code)
#                self.shipping_countries.add(salescountry)
        else:
            log.warn("%s: has no country set", self)

        super(Config, self).save(*args, **kwargs)
        caching.cache_set("Config", self.site.id, value=self)

    def __unicode__(self):
        return self.store_name

    class Meta:
        verbose_name = _("Store Configuration")
        verbose_name_plural = _("Store Configurations")


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

        if 'cart' in request.session:
            cartid = request.session['cart']
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
                    log.debug('Removing invalid cart from session')
                    del request.session['cart']

        if isinstance(cart, NullCart) and not isinstance(cart, OrderCart) and contact is not None:
            carts = Cart.objects.filter(customer=contact)
            if carts.count() > 0:
                cart = carts[0]
                request.session['cart'] = cart.id

        if not cart:
            if create:
                site = Site.objects.get_current()
                if contact is None:
                    cart = Cart(site=site)
                else:
                    cart = Cart(site=site, customer=contact)
                cart.save()
                request.session['cart'] = cart.id

            elif return_nullcart:
                cart = NullCart()

            else:
                raise Cart.DoesNotExist()

        #log.debug("Cart: %s", cart)
        return cart


class Cart(models.Model):
    """
    Store items currently in a cart
    The desc isn't used but it is needed to make the admin interface work appropriately
    Could be used for debugging
    """
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    desc = models.CharField(_("Description"), blank=True, null=True, max_length=10)
    date_time_created = models.DateTimeField(_("Creation Date"))
    customer = models.ForeignKey(Contact, blank=True, null=True, verbose_name=_('Customer'))

    objects = CartManager()

    def _get_count(self):
        itemCount = 0
        for item in self.cartitem_set.all():
            itemCount += item.quantity
        return (itemCount)
    numItems = property(_get_count)

    def _get_total(self):
        total = Decimal("0")
        for item in self.cartitem_set.all():
            total += item.line_total
        return(total)
    total = property(_get_total)

    def __iter__(self):
        return iter(self.cartitem_set.all())

    def __len__(self):
        return self.cartitem_set.count()

    def __unicode__(self):
        return u"Shopping Cart (%s)" % self.date_time_created

    def add_item(self, chosen_item, number_added, details=None):
        if details is None:
            details = {}
        alreadyInCart = False
        # Custom Products will not be added, they will each get their own line item
        if 'CustomProduct' in chosen_item.get_subtypes():
            item_to_modify = CartItem(cart=self, product=chosen_item, quantity=0)
        else:
            item_to_modify = CartItem(cart=self, product=chosen_item, quantity=0)
            for similarItem in self.cartitem_set.filter(product__id=chosen_item.id):
                looksTheSame = len(details) == similarItem.details.count()
                if looksTheSame:
                    for detail in details:
                        try:
                            similarItem.details.get(
                                    name=detail['name'],
                                    value=detail['value'],
                                    price_change=detail['price_change']
                                    )
                        except CartItemDetails.DoesNotExist:
                            looksTheSame = False
                if looksTheSame:
                    item_to_modify = similarItem
                    alreadyInCart = True
                    break

        signals.satchmo_cart_add_verify.send(self, cart=self, cartitem=item_to_modify, added_quantity=number_added, details=details)
        if not alreadyInCart:
            self.cartitem_set.add(item_to_modify)

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

    def save(self, *args, **kwargs):
        """Ensure we have a date_time_created before saving the first time."""
        if not self.pk:
            self.date_time_created = datetime.datetime.now()
        try:
            self.site
        except Site.DoesNotExist:
            self.site = Site.objects.get_current()
        super(Cart, self).save(*args, **kwargs)

    def _get_shippable(self):
        """Return whether the cart contains shippable items."""
        for cartitem in self.cartitem_set.all():
            if cartitem.is_shippable:
                return True
        return False
    is_shippable = property(_get_shippable)

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
        if config.no_stock_checkout == False:
            for cart_item in self.cartitem_set.all():
                if not cart_item.has_enough_stock():
                    not_enough_stock.append(cart_item)
        return not_enough_stock

    class Meta:
        verbose_name = _("Shopping Cart")
        verbose_name_plural = _("Shopping Carts")


class NullCartItem(object):
    def __init__(self, itemid):
        self.id = itemid
        self.quantity = 0
        self.line_total = 0


class CartItem(models.Model):
    """
    An individual item in the cart
    """
    cart = models.ForeignKey(Cart, verbose_name=_('Cart'))
    product = models.ForeignKey(Product, verbose_name=_('Product'))
    quantity = models.IntegerField(_("Quantity"))

    def _get_line_unitprice(self):
        # Get the qty discount price as the unit price for the line.

        self.qty_price = self.get_qty_price(self.quantity)
        self.detail_price = self.get_detail_price()
        #send signal to possibly adjust the unitprice
        signals.satchmo_cartitem_price_query.send(self, cartitem=self)
        price = self.qty_price + self.detail_price

        #clean up temp vars
        del self.qty_price
        del self.detail_price

        return price

    unit_price = property(_get_line_unitprice)

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

    def _get_line_total(self):
        return self.unit_price * self.quantity
    line_total = property(_get_line_total)

    def _get_description(self):
        return self.product.translated_name()
    description = property(_get_description)

    def _is_shippable(self):
        return self.product.is_shippable

    is_shippable = property(fget=_is_shippable)

    def add_detail(self, data):
        detl = CartItemDetails(cartitem=self, name=data['name'], value=data['value'], sort_order=data['sort_order'], price_change=data['price_change'])
        detl.save()
        #self.details.add(detl)

    def _has_details(self):
        """
        Determine if this specific item has more detail
        """
        return (self.details.count() > 0)

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

    def __unicode__(self):
        currency = config_value('SHOP', 'CURRENCY')
        currency = currency.replace("_", " ")
        return u'%s - %s %s%s' % (self.quantity, self.product.name,
            force_unicode(currency), self.line_total)

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ('id',)


class CartItemDetails(models.Model):
    """
    An arbitrary detail about a cart item.
    """
    cartitem = models.ForeignKey(CartItem, related_name='details', )
    value = models.TextField(_('detail'))
    name = models.CharField(_('name'), max_length=100)
    price_change = models.DecimalField(_("Item Detail Price Change"), max_digits=6, decimal_places=2, blank=True, null=True)
    sort_order = models.IntegerField(_("Sort Order"),
        help_text=_("The display order for this group."))

    class Meta:
        ordering = ('sort_order',)
        verbose_name = _("Cart Item Detail")
        verbose_name_plural = _("Cart Item Details")


ORDER_CHOICES = (
    ('Online', _('Online')),
    ('In Person', _('In Person')),
    ('Show', _('Show')),
)


class Status(models.Model):
    status = models.CharField(_("Status"), max_length=255)
    description = models.TextField(_("description"), null=True, blank=True)
    notify = models.BooleanField(_("Notify"), help_text="Notify the user on status update", default=True)
    display = models.BooleanField(_("Display"), help_text="Show orders of this status in the admin area home page", default=True)

    def __unicode__(self):
        return self.status

    def orders(self):
        """ Get all orders of this status """
        return Order.objects.filter(status__status=self)

    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Statuses")


class OrderManager(models.Manager):

    def live(self):
        return self.filter(frozen=False)

    def from_request(self, request):
        """Get the order from the session

        Returns:
        - Order object or None
        """
        order = None
        if 'orderID' in request.session:
            try:
                order = Order.objects.live().get(id=request.session['orderID'])

                if request.user != order.contact.user:
                    order = None
            except Order.DoesNotExist:
                pass

            if order is None:
                del request.session['orderID']

        if order is None:
            raise Order.DoesNotExist()

        return order

    def remove_partial_order(self, request):
        """Delete cart from request if it exists and is incomplete (has no status)"""
        try:
            order = Order.objects.from_request(request)
            if not order.status:
                del request.session['orderID']
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
    site = models.ForeignKey(Site, verbose_name=_('Site'))
    contact = models.ForeignKey(Contact, verbose_name=_('Contact'))
    ship_addressee = models.CharField(_("Addressee"), max_length=61, blank=True)
    ship_street1 = models.CharField(_("Street"), max_length=80, blank=True)
    ship_street2 = models.CharField(_("Street"), max_length=80, blank=True)
    ship_city = models.CharField(_("City"), max_length=50, blank=True)
    ship_state = models.CharField(_("State"), max_length=50, blank=True)
    ship_postal_code = models.CharField(_("Post Code"), max_length=30, blank=True)
    ship_country = models.ForeignKey(Country, blank=True, related_name="ship_country")
    bill_addressee = models.CharField(_("Addressee"), max_length=61, blank=True)
    bill_street1 = models.CharField(_("Street"), max_length=80, blank=True)
    bill_street2 = models.CharField(_("Street"), max_length=80, blank=True)
    bill_city = models.CharField(_("City"), max_length=50, blank=True)
    bill_state = models.CharField(_("State"), max_length=50, blank=True)
    bill_postal_code = models.CharField(_("Post Code"), max_length=30, blank=True)
    bill_country = models.ForeignKey(Country, blank=True, related_name="bill_country")
    notes = models.TextField(_("Notes"), blank=True, null=True)
    sub_total = models.DecimalField(_("Subtotal"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    total = models.DecimalField(_("Total"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    discount_code = models.CharField(_("Discount Code"), max_length=20, blank=True, null=True,
        help_text=_("Coupon Code"))
    discount = models.DecimalField(_("Discount amount"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    method = models.CharField(_("Order method"),
        choices=ORDER_CHOICES, max_length=200, blank=True)
    shipping_description = models.CharField(_("Shipping Description"),
        max_length=200, blank=True, null=True)
    shipping_method = models.CharField(_("Shipping Method"),
        max_length=200, blank=True, null=True)
    shipping_model = ShippingChoiceCharField(_("Shipping Models"),
        max_length=30, blank=True, null=True)
    shipping_cost = models.DecimalField(_("Shipping Cost"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    shipping_discount = models.DecimalField(_("Shipping Discount"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    tax = models.DecimalField(_("Tax"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    status = models.ForeignKey("OrderStatus", blank=True, null=True, editable=False, related_name="current_status")
    frozen = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(_("Timestamp"), editable=False)

    objects = OrderManager()

    def __unicode__(self):
        return "Order #%s: %s" % (self.id, self.contact.full_name)

    def save(self, *args, **kwargs):
        """
        Copy addresses from contact. If the order has just been created, set
        the create_date.
        """
        if self.pk is None:
            self.copy_addresses()
            self.time_stamp = datetime.datetime.now()
        super(Order, self).save(*args, **kwargs)  # Call the "real" save() method.

    def freeze(self):
        self.frozen = True
        self.time_stamp = datetime.datetime.now()

    def add_status(self, status=None, notes=None):
        orderstatus = OrderStatus()
        if not status:
            if self.orderstatus_set.count() > 0:
                status_obj = self.status
            else:
                status_obj, __ = Status.objects.get_or_create(status="Pending")
        else:
            status_obj, __ = Status.objects.get_or_create(status=status)

        orderstatus.status = status_obj
        orderstatus.notes = notes
        orderstatus.time_stamp = datetime.datetime.now()
        orderstatus.order = self
        orderstatus.save()

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

    def balance_forward(self):
        return money_format(self.balance)

    balance_forward = property(fget=balance_forward)

    def _balance_paid(self):
        payments = [p.amount for p in self.payments.all()]
        if payments:
            return reduce(operator.add, payments)
        else:
            return Decimal("0.0000000000")

    balance_paid = property(_balance_paid)

    def _credit_card(self):
        """Return the credit card associated with this payment."""
        for payment in self.payments.order_by('-time_stamp'):
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

    def _get_balance_remaining_url(self):
        return ('satchmo_balance_remaining_order', None, {'order_id': self.id})
    get_balance_remaining_url = models.permalink(_get_balance_remaining_url)

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
        q = self.payments.exclude(transaction_id__isnull=False, transaction_id="PENDING")
        return q.exclude(amount=Decimal("0.00"))

    def invoice(self):
        url = urlresolvers.reverse('satchmo_print_shipping', None, None, {'doc': 'invoice', 'id': self.id})
        return mark_safe(u'<a href="%s">%s</a>' % (url, _('View')))
    invoice.allow_tags = True

    def _item_discount(self):
        """Get the discount of just the items, less the shipping discount."""
        return self.discount - self.shipping_discount
    item_discount = property(_item_discount)

    def packingslip(self):
        url = urlresolvers.reverse('satchmo_print_shipping', None, None, {'doc': 'packingslip', 'id': self.id})
        return mark_safe(u'<a href="%s">%s</a>' % (url, _('View')))
    packingslip.allow_tags = True

    def recalculate_total(self, save=True):
        """Calculates sub_total, taxes and total if the order is not already partially paid."""
        if self.is_partially_paid:
            log.debug("Order %i - skipping recalculate_total since product is partially paid.", self.id)
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

        if 'Shipping' in discount.item_discounts:
            self.shipping_discount = discount.item_discounts['Shipping']
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

        for taxdesc, taxamt in taxrates.items():
            taxdetl = OrderTaxDetail(order=self, tax=taxamt, description=taxdesc, method=taxProcessor.method)
            taxdetl.save()

        log.debug("Order #%i, recalc: sub_total=%s, shipping=%s, discount=%s, tax=%s",
            self.id,
            money_format(item_sub_total),
            money_format(self.shipping_sub_total),
            money_format(self.discount),
            money_format(self.tax))

        self.total = Decimal(item_sub_total + self.shipping_sub_total + self.tax)

        if save:
            self.save()

    def shippinglabel(self):
        url = urlresolvers.reverse('satchmo_print_shipping', None, None, {'doc': 'shippinglabel', 'id': self.id})
        return mark_safe(u'<a href="%s">%s</a>' % (url, _('View')))
    shippinglabel.allow_tags = True

    def _order_total(self):
        #Needed for the admin list display
        return money_format(self.total)
    order_total = property(_order_total)

    def order_success(self):
        """Run each item's order_success method."""
        log.info("Order success: %s", self)
        for orderitem in self.orderitem_set.all():
            subtype = orderitem.product.get_subtype_with_attr('order_success')
            if subtype:
                subtype.order_success(self, orderitem)
        if self.is_downloadable:
            self.add_status('Shipped', _("Order immediately available for download"))
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

    def _shipping_sub_total(self):
        if self.shipping_cost is None:
            self.shipping_cost = Decimal('0.00')
        if self.shipping_discount is None:
            self.shipping_discount = Decimal('0.00')
        return self.shipping_cost - self.shipping_discount
    shipping_sub_total = property(_shipping_sub_total)

    def _shipping_tax(self):
        rates = self.taxes.filter(description__iexact='shipping')
        if rates.count() > 0:
            tax = reduce(operator.add, [t.tax for t in rates])
        else:
            tax = Decimal("0.0000000000")
        return tax
    shipping_tax = property(_shipping_tax)

    def _shipping_with_tax(self):
        return self.shipping_sub_total + self.shipping_tax
    shipping_with_tax = property(_shipping_with_tax)

    def sub_total_with_tax(self):
        return reduce(operator.add, [o.total_with_tax for o in self.orderitem_set.all()])

    def validate(self, request):
        """
        Return whether the order is valid.
        Not guaranteed to be side-effect free.
        """
        valid = True
        for orderitem in self.orderitem_set.all():
            for subtype_name in orderitem.product.get_subtypes():
                subtype = getattr(orderitem.product, subtype_name.lower())
                validate_method = getattr(subtype, 'validate_order', None)
                if validate_method:
                    valid = valid and validate_method(request, self, orderitem)
        return valid

    class Meta:
        verbose_name = _("Product Order")
        verbose_name_plural = _("Product Orders")


class OrderItem(models.Model):
    """
    A line item on an order.
    """
    order = models.ForeignKey(Order, verbose_name=_("Order"))
    product = models.ForeignKey(Product, verbose_name=_("Product"))
    quantity = models.IntegerField(_("Quantity"), )
    unit_price = models.DecimalField(_("Unit price"),
        max_digits=18, decimal_places=10)
    unit_tax = models.DecimalField(_("Unit tax"),
        max_digits=18, decimal_places=10, null=True)
    line_item_price = models.DecimalField(_("Line item price"),
        max_digits=18, decimal_places=10)
    tax = models.DecimalField(_("Line item tax"),
        max_digits=18, decimal_places=10, null=True)
    expire_date = models.DateField(_("Subscription End"), help_text=_("Subscription expiration date."), blank=True, null=True)
    completed = models.BooleanField(_("Completed"), default=False)
    stock_updated = models.BooleanField(_("Stock Updated"), default=False)
    discount = models.DecimalField(_("Line item discount"),
        max_digits=18, decimal_places=10, blank=True, null=True)

    def __unicode__(self):
        return self.product.translated_name()

    def _get_category(self):
        return(self.product.get_category.translated_name())
    category = property(_get_category)

    def _is_shippable(self):
        return self.product.is_shippable

    is_shippable = property(fget=_is_shippable)

    def _sub_total(self):
        if self.discount:
            return self.line_item_price - self.discount
        else:
            return self.line_item_price
    sub_total = property(_sub_total)

    def _total_with_tax(self):
        return self.sub_total + self.tax
    total_with_tax = property(_total_with_tax)

    def _unit_price_with_tax(self):
        return self.unit_price + self.unit_tax
    unit_price_with_tax = property(_unit_price_with_tax)

    def _get_description(self):
        return self.product.translated_name()
    description = property(_get_description)

    def save(self, *args, **kwargs):
        self.update_tax()
        super(OrderItem, self).save(*args, **kwargs)

    def update_tax(self):
        taxclass = self.product.taxClass
        processor = get_tax_processor(order=self.order)
        self.unit_tax = processor.by_price(taxclass, self.unit_price)
        self.tax = processor.by_orderitem(self)

    class Meta:
        verbose_name = _("Order Line Item")
        verbose_name_plural = _("Order Line Items")
        ordering = ('id',)


class OrderItemDetail(models.Model):
    """
    Name, value pair and price delta associated with a specific item in an order
    """
    item = models.ForeignKey(OrderItem, verbose_name=_("Order Item"), )
    name = models.CharField(_('Name'), max_length=100)
    value = models.CharField(_('Value'), max_length=255)
    price_change = models.DecimalField(_("Price Change"), max_digits=18, decimal_places=10, blank=True, null=True)
    sort_order = models.IntegerField(_("Sort Order"),
        help_text=_("The display order for this group."))

    def __unicode__(self):
        return u"%s - %s,%s" % (self.item, self.name, self.value)

    class Meta:
        verbose_name = _("Order Item Detail")
        verbose_name_plural = _("Order Item Details")
        ordering = ('sort_order',)


class DownloadLink(models.Model):
    downloadable_product = models.ForeignKey(DownloadableProduct, verbose_name=_('Downloadable product'))
    order = models.ForeignKey(Order, verbose_name=_('Order'))
    key = models.CharField(_('Key'), max_length=40)
    num_attempts = models.IntegerField(_('Number of attempts'), )
    time_stamp = models.DateTimeField(_('Time stamp'), default=datetime.datetime.now(), editable=True)
    active = models.BooleanField(_('Active'), default=True)

    def _attempts_left(self):
        return self.downloadable_product.num_allowed_downloads - self.num_attempts
    attempts_left = property(_attempts_left)

    def is_valid(self):
        # Check num attempts and expire_minutes
        if not self.downloadable_product.active:
            return (False, _("This download is no longer active"))
        if self.num_attempts >= self.downloadable_product.num_allowed_downloads:
            return (False, _("You have exceeded the number of allowed downloads."))
        expire_time = datetime.timedelta(minutes=self.downloadable_product.expire_minutes) + self.time_stamp
        if datetime.datetime.now() > expire_time:
            return (False, _("This download link has expired."))
        return (True, "")

    def get_absolute_url(self):
        return('satchmo.shop.views.download.process', (), {'download_key': self.key})
    get_absolute_url = models.permalink(get_absolute_url)

    def get_full_url(self):
        url = urlresolvers.reverse('satchmo_download_process', kwargs={'download_key': self.key})
        return('http://%s%s' % (Site.objects.get_current(), url))

    def save(self, *args, **kwargs):
        """
        Set the initial time stamp
        """
        super(DownloadLink, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s - %s" % (self.downloadable_product.product.slug, self.time_stamp)

    def _product_name(self):
        return u"%s" % (self.downloadable_product.product.translated_name())
    product_name = property(_product_name)

    class Meta:
        verbose_name = _("Download Link")
        verbose_name_plural = _("Download Links")


class OrderStatus(models.Model):
    """
    An order will have multiple statuses as it moves its way through processing.
    """

    order = models.ForeignKey(Order, verbose_name=_("Order"))
    status = models.ForeignKey(Status, verbose_name=_("Status"))
    notes = models.TextField(_("Notes"), blank=True)
    time_stamp = models.DateTimeField(_("Timestamp"), editable=False)

    def __unicode__(self):
        return self.status.status

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.time_stamp = datetime.datetime.now()
        super(OrderStatus, self).save(*args, **kwargs)

        # Set the most recent status
        if self.order.status == None or self.order.status.time_stamp < self.time_stamp:
            self.order.status = self
            self.order.save()

        # Send a notification if appropriate
        if self.status.notify:
            send_order_update_notice(self)

    class Meta:
        verbose_name = _("Order Status")
        verbose_name_plural = _("Order Statuses")
        ordering = ('time_stamp',)


class OrderPayment(models.Model):
    order = models.ForeignKey(Order, related_name="payments")
    payment = PaymentChoiceCharField(_("Payment Method"),
        max_length=25, blank=True)
    amount = models.DecimalField(_("amount"),
        max_digits=18, decimal_places=10, blank=True, null=True)
    time_stamp = models.DateTimeField(_("timestamp"), default=datetime.datetime.now(), editable=True)
    transaction_id = models.CharField(_("Transaction ID"), max_length=25, blank=True, null=True)

    def _credit_card(self):
        """Return the credit card associated with this payment."""
        try:
            return self.creditcards.get()
        except self.creditcards.model.DoesNotExist:
            return None
    credit_card = property(_credit_card)

    def _amount_total(self):
        return money_format(self.amount)

    amount_total = property(fget=_amount_total)

    def __unicode__(self):
        if self.id is not None:
            return u"Order payment #%i" % self.id
        else:
            return u"Order payment (unsaved)"

    class Meta:
        verbose_name = _("Order Payment")
        verbose_name_plural = _("Order Payments")


class OrderVariable(models.Model):
    order = models.ForeignKey(Order, related_name="variables")
    key = models.SlugField(_('key'))
    value = models.CharField(_('value'), max_length=100)

    class Meta:
        ordering = ('key',)
        verbose_name = _("Order variable")
        verbose_name_plural = _("Order variables")

    def __unicode__(self):
        if len(self.value) > 10:
            v = self.value[:10] + '...'
        else:
            v = self.value
        return u"OrderVariable: %s=%s" % (self.key, v)


class OrderTaxDetail(models.Model):
    """A tax line item"""
    order = models.ForeignKey(Order, related_name="taxes")
    method = models.CharField(_("Model"), max_length=50)
    description = models.CharField(_("Description"), max_length=50, blank=True)
    tax = models.DecimalField(_("Tax"),
        max_digits=18, decimal_places=10, blank=True, null=True)

    def __unicode__(self):
        if self.description:
            return u"Tax: %s %s" % (self.description, self.tax)
        else:
            return u"Tax: %s" % self.tax

    class Meta:
        verbose_name = _('Order tax detail')
        verbose_name_plural = _('Order tax details')
        ordering = ('id',)


def _remove_order_on_cart_update(request=None, cart=None, **kwargs):
    if request:
        log.debug("caught cart changed signal - remove_order_on_cart_update")
        Order.objects.remove_partial_order(request)


def _recalc_total_on_contact_change(contact=None, **kwargs):
    log.debug("Recalculating all contact orders not in process")
    orders = Order.objects.live().filter(contact=contact, status=None)
    log.debug("Found %i orders to recalc", len(orders))
    for order in orders:
        order.copy_addresses()
        order.recalculate_total()


def _create_download_link(product=None, order=None, subtype=None, **kwargs):
    if product and order and subtype == "download":
        new_link = DownloadLink(downloadable_product=product, order=order, key=product.create_key(), num_attempts=0)
        new_link.save()
    else:
        log.debug("ignoring subtype_order_success signal, looking for download product, got %s", subtype)

signals.satchmo_cart_changed.connect(_remove_order_on_cart_update, sender=None)
satchmo_contact_location_changed.connect(_recalc_total_on_contact_change, sender=None)
signals.order_success.connect(order_success_listener, sender=None)
product_signals.subtype_order_success.connect(_create_download_link, sender=None)

import config
