"""
Base model used for products.  Stores hierarchical categories
as well as individual product level information which includes
options.
"""

import datetime
import hashlib
import logging
import os.path
import random
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.db.models.fields.files import FileField
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import get_language, ugettext_lazy as _

from satchmo.configuration.functions import (
    SettingNotSet,
    config_value,
    config_value_safe,
)
from satchmo.currency.models import Currency
from satchmo.currency.utils import convert_to_currency
from satchmo.shipping.config import shipping_methods
from satchmo.shop.signals import satchmo_search
from satchmo.tax.models import TaxClass
from satchmo.utils import add_month, cross_list, get_flat_list, normalize_dir
from . import signals

log = logging.getLogger(__name__)

dimension_units = (("cm", "cm"), ("in", "in"))
weight_units = (("kg", "kg"), ("lb", "lb"))

SHIP_CLASS_CHOICES = (
    ("DEFAULT", _("Default")),
    ("YES", _("Shippable")),
    ("NO", _("Not Shippable")),
)


def default_dimension_unit():
    val = config_value_safe("SHOP", "MEASUREMENT_SYSTEM", (None, None))[0]
    if val == "metric":
        return "cm"
    else:
        return "in"


def default_weight_unit():
    val = config_value_safe("SHOP", "MEASUREMENT_SYSTEM", (None, None))[0]
    if val == "metric":
        return "kg"
    else:
        return "lb"


class CategoryManager(models.Manager):
    def root_categories(self, **kwargs):
        """Get all root categories."""
        return self.filter(parent__isnull=True, **kwargs)

    def search(self, keyword, include_children=False):
        """Search for categories by keyword.
        Note, this does not return a queryset."""

        cats = self.filter(
            Q(name__icontains=keyword)
            | Q(meta__icontains=keyword)
            | Q(description__icontains=keyword)
        )

        if include_children:
            # get all the children of the categories found
            cats = [cat.get_active_children(include_self=True) for cat in cats]

        # sort properly
        if cats:
            fastsort = sorted([(c.ordering, c.name, c) for c in get_flat_list(cats)])
            # extract the cat list
            cats = list(zip(*fastsort))[2]
        return cats


class Category(models.Model):
    """
    Basic hierarchical category model for storing products
    """

    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description of category"), default="", blank=True)
    slug = models.SlugField(
        _("Slug"),
        help_text=_("Used for URLs, auto-generated from name if blank"),
        blank=True,
    )
    active = models.BooleanField(_("Active"), default=False)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="child"
    )
    meta = models.TextField(
        _("Meta Description"),
        blank=True,
        null=True,
        help_text=_("Meta description for this category"),
    )
    description = models.TextField(_("Description"), blank=True, help_text="Optional")
    ordering = models.IntegerField(
        _("Ordering"),
        default=0,
        help_text=_("Override alphabetical order in category display"),
    )
    related_categories = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name=_("Related Categories"),
        related_name="related_categories",
    )
    objects = CategoryManager()

    class Meta:
        ordering = ["parent__id", "ordering", "name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        name_list = [cat.name for cat in self._recurse_for_parents(self)]
        name_list.append(self.name)
        return self.get_separator().join(name_list)

    def get_absolute_url(self):
        return reverse("satchmo_category", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self.id:
            if self.parent and self.parent_id == self.id:
                raise ValidationError(_("You must not save a category in itself!"))

            for p in self._recurse_for_parents(self):
                if self.id == p.id:
                    raise ValidationError(_("You must not save a category in itself!"))

        if not self.slug:
            self.slug = slugify(self.name)

        super(Category, self).save(*args, **kwargs)
        img_key = "Category_get_mainImage %s" % (self.id)
        img_key = img_key.replace(" ", "-")
        ap_key = "Category_active_products %s" % (self.id)
        ap_key = ap_key.replace(" ", "-")
        cache.delete_many([img_key, ap_key])

    @property
    def main_image(self):
        key = "Category_get_mainImage %s" % (self.id)
        key = key.replace(" ", "-")
        img = cache.get(key)
        if img is None:
            img = False
            if self.images.count() > 0:
                img = self.images.order_by("sort")[0]
            else:
                if self.parent_id and self.parent != self:
                    img = self.parent.main_image

            if not img:
                # This should be a "Image Not Found" placeholder image
                try:
                    img = CategoryImage.objects.filter(category__isnull=True).order_by(
                        "sort"
                    )[0]
                except IndexError:
                    log.warning("Default category image not found")
            cache.set(key, img)
        return img

    def active_products(self, variations=True, include_children=False, **kwargs):
        key = "Category_active_products %s" % (self.id)
        key = key.replace(" ", "-")
        products = cache.get(key)
        if products is None:
            if variations and include_children:
                cats = self.get_all_children(include_self=True)
                products = Product.objects.select_related().filter(
                    category__in=cats, active=True, **kwargs
                )
            elif variations and not include_children:
                products = self.product_set.select_related().filter(
                    active=True, **kwargs
                )
            elif not variations and include_children:
                cats = self.get_all_children(include_self=True)
                products = Product.objects.select_related().filter(
                    category__in=cats,
                    active=True,
                    productvariation__parent__isnull=True,
                    **kwargs
                )
            elif not variations and not include_children:
                products = self.product_set.select_related().filter(
                    active=True, productvariation__parent__isnull=True, **kwargs
                )
            cache.set(key, products)
        return products

    def active_products_include_children(self, variations=True, **kwargs):
        return self.active_products(variations, True, **kwargs)

    def _recurse_for_parents(self, cat_obj):
        p_list = []
        if cat_obj.parent_id:
            p = cat_obj.parent
            p_list.append(p)
            if p != self:
                more = self._recurse_for_parents(p)
                p_list.extend(more)
        if cat_obj == self and p_list:
            p_list.reverse()
        return p_list

    def parents(self):
        return self._recurse_for_parents(self)

    def get_separator(self):
        return " - "

    def _parents_repr(self):
        name_list = [cat.name for cat in self._recurse_for_parents(self)]
        return self.get_separator().join(name_list)

    _parents_repr.short_description = "Category parents"

    def get_url_name(self):
        # Get all the absolute URLs and names for use in the site navigation.
        name_list = []
        url_list = []
        for cat in self._recurse_for_parents(self):
            name_list.append(cat.name)
            url_list.append(cat.get_absolute_url())
        name_list.append(self.name)
        url_list.append(self.get_absolute_url())
        return list(zip(name_list, url_list))

    def _flatten(self, L):
        """
        Taken from a python newsgroup post
        """
        if not isinstance(L, list):
            return [L]
        if L == []:
            return L
        return self._flatten(L[0]) + self._flatten(L[1:])

    def _recurse_for_children(self, node, only_active=False):
        children = []
        children.append(node)
        for child in node.child.all():
            if child != self:
                # TODO: I think there is a problem here if the category has child categories, but they have no active children
                if (
                    (not only_active)
                    or child.active_products().count() > 0
                    or len(child.get_active_children()) > 0
                ):
                    children_list = self._recurse_for_children(
                        child, only_active=only_active
                    )
                    children.append(children_list)
        return children

    def get_active_children(self, include_self=False):
        """
        Gets a list of all of the children categories which have active products.
        """
        return self.get_all_children(only_active=True, include_self=include_self)

    def get_all_children(self, only_active=False, include_self=False):
        """
        Gets a list of all of the children categories.
        """
        key = "Category_get_all_children_%s_%s_%s" % (
            self.id,
            only_active,
            include_self,
        )
        key = key.replace("_", "-")
        flat_list = cache.get(key)
        if flat_list is None:
            children_list = self._recurse_for_children(self, only_active=only_active)
            if include_self:
                ix = 0
            else:
                ix = 1
            flat_list = self._flatten(children_list[ix:])
            cache.set(key, flat_list)
        return flat_list


class CategoryImage(models.Model):
    """
    A picture of an item.  Can have many pictures associated with an item.
    """

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True, related_name="images"
    )
    picture = models.ImageField(
        verbose_name=_("Picture"), upload_to="product-category/", max_length=200
    )
    caption = models.CharField(
        _("Optional caption"), max_length=255, null=True, blank=True
    )
    sort = models.IntegerField(_("Sort Order"))

    def _get_filename(self):
        if self.category:
            return "%s-%s" % (self.category.slug, self.id)
        else:
            return "default"

    _filename = property(_get_filename)

    def __str__(self):
        if self.category:
            return "Image of Category %s" % self.category.slug
        elif self.caption:
            return 'Image with caption "%s"' % self.caption
        else:
            return "%s" % self.picture

    class Meta:
        ordering = ["sort"]
        unique_together = (("category", "sort"),)
        verbose_name = _("Category Image")
        verbose_name_plural = _("Category Images")


class OptionGroupManager(models.Manager):
    def get_sortmap(self):
        """Returns a dictionary mapping ids to sort order"""

        work = {}
        for uid, order in self.values_list("id", "sort_order"):
            work[uid] = order

        return work


class OptionGroup(models.Model):
    """
    A set of options that can be applied to an item.
    Examples - Size, Color, Shape, etc
    """

    name = models.CharField(
        _("Name of Option Group"),
        max_length=255,
        help_text=_("This will be the text displayed on the product page."),
    )
    description = models.TextField(
        _("Detailed Description"),
        blank=True,
        help_text=_(
            "Further description of this group (i.e. shirt size vs shoe size)."
        ),
    )
    sort_order = models.IntegerField(
        _("Sort Order"), help_text=_("The display order for this group.")
    )

    objects = OptionGroupManager()

    def __str__(self):
        if self.description:
            return "%s - %s" % (self.name, self.description)
        else:
            return self.name

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("Option Group")
        verbose_name_plural = _("Option Groups")


class OptionManager(models.Manager):
    def from_unique_id(self, unique_id):
        group_id, option_value = split_option_unique_id(unique_id)
        return Option.objects.get(option_group=group_id, value=option_value)


class Option(models.Model):
    """
    These are the actual items in an OptionGroup.  If the OptionGroup is Size, then an Option
    would be Small.
    """

    objects = OptionManager()
    option_group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE)
    name = models.CharField(_("Display value"), max_length=255)
    value = models.CharField(_("Stored value"), max_length=255)
    price_change = models.DecimalField(
        _("Price Change"),
        null=True,
        blank=True,
        max_digits=14,
        decimal_places=6,
        help_text=_("This is the price differential for this option."),
    )
    sort_order = models.IntegerField(_("Sort Order"))

    class Meta:
        ordering = ("option_group", "sort_order", "name")
        unique_together = (("option_group", "value"),)
        verbose_name = _("Option Item")
        verbose_name_plural = _("Option Items")

    def _get_unique_id(self):
        return make_option_unique_id(self.option_group_id, self.value)

    unique_id = property(_get_unique_id)

    def __repr__(self):
        return "<Option: %s>" % self.name

    def __str__(self):
        return "%s: %s" % (self.option_group.name, self.name)


class ProductManager(models.Manager):
    def active(self, variations=True, **kwargs):
        if not variations:
            kwargs["productvariation__parent__isnull"] = True
        return self.filter(active=True, **kwargs)

    def in_stock(self, **kwargs):
        return self.filter(active=True, items_in_stock__gt=0, **kwargs)

    def featured(self, **kwargs):
        return self.active(featured=True, **kwargs)

    def recent(self, **kwargs):
        query = self.active(**kwargs)
        if query.count() == 0:
            query = self.active()

        query = query.order_by("-date_added")
        return query


class Product(models.Model):
    """
    Root class for all Products
    """

    name = models.CharField(
        _("Full Name"),
        max_length=255,
        blank=False,
        help_text=_("The products full name"),
    )
    slug = models.SlugField(
        _("Slug Name"),
        blank=True,
        help_text=_("Used for URLs, auto-generated from name if blank"),
        max_length=255,
        unique=True,
    )
    sku = models.CharField(
        _("SKU"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Defaults to slug if left blank"),
        unique=True,
    )
    short_description = models.TextField(
        _("Short description of product"),
        help_text=_(
            "This should be a 1 or 2 line description for use in product listing screens"
        ),
        max_length=200,
        default="",
        blank=True,
    )
    description = models.TextField(
        _("Description of product"),
        help_text=_(
            "This field can contain HTML and should be a few paragraphs explaining the background of the product, and anything that would help the potential customer make their purchase."
        ),
        default="",
        blank=True,
    )
    enhanced_description = models.TextField(
        _("Enhanced description of product"),
        help_text=_(
            "Additional information about the product to appear below the fold."
        ),
        default="",
        blank=True,
    )
    category = models.ManyToManyField(Category, blank=True, verbose_name=_("Category"))
    unit_price = models.DecimalField(
        _("Unit Price"),
        help_text=_("Base price for quantity of 1"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    items_in_stock = models.IntegerField(_("Number in stock"), default=0)
    meta = models.TextField(
        _("Meta Description"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_("Meta description for this product"),
    )
    date_added = models.DateField(_("Date added"))
    date_updated = models.DateField(_("Date updated"))
    active = models.BooleanField(
        _("Is product active?"),
        default=True,
        help_text=_(
            "This will determine whether or not this product will appear on the site"
        ),
    )
    featured = models.BooleanField(
        _("Featured Item"),
        default=False,
        help_text=_("Featured items will show on the front page"),
    )
    ordering = models.IntegerField(
        _("Ordering"),
        default=0,
        help_text=_("Override alphabetical order in category display"),
    )
    weight = models.DecimalField(
        _("Weight"), max_digits=8, decimal_places=2, null=True, blank=True
    )
    weight_units = models.CharField(
        _("Weight units"), max_length=3, null=True, blank=True
    )
    length = models.DecimalField(
        _("Length"), max_digits=6, decimal_places=2, null=True, blank=True
    )
    length_units = models.CharField(
        _("Length units"), max_length=3, null=True, blank=True
    )
    width = models.DecimalField(
        _("Width"), max_digits=6, decimal_places=2, null=True, blank=True
    )
    width_units = models.CharField(
        _("Width units"), max_length=3, null=True, blank=True
    )
    height = models.DecimalField(
        _("Height"), max_digits=6, decimal_places=2, null=True, blank=True
    )
    height_units = models.CharField(
        _("Height units"), max_length=3, null=True, blank=True
    )
    related_items = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name=_("Related Items"),
        related_name="related_products",
    )
    also_purchased = models.ManyToManyField(
        "self",
        blank=True,
        verbose_name=_("Previously Purchased"),
        related_name="also_products",
    )
    total_sold = models.IntegerField(_("Total sold"), default=0)
    taxable = models.BooleanField(_("Taxable"), default=False)
    taxClass = models.ForeignKey(
        TaxClass,
        on_delete=models.CASCADE,
        verbose_name=_("Tax Class"),
        blank=True,
        null=True,
        help_text=_("If it is taxable, what kind of tax?"),
    )
    shipclass = models.CharField(
        _("Shipping"),
        choices=SHIP_CLASS_CHOICES,
        default="YES",
        max_length=10,
        help_text=_(
            "If this is 'Default', then we'll use the product type to determine if it is shippable."
        ),
    )
    instructions = models.ForeignKey(
        "Instruction", on_delete=models.CASCADE, null=True, blank=True
    )
    precautions = models.ForeignKey(
        "Precaution", on_delete=models.CASCADE, null=True, blank=True
    )
    objects = ProductManager()

    class Meta:
        ordering = ("ordering", "name")
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        main_category = self.main_category
        if main_category:
            category_slug = main_category.slug
        else:
            category_slug = _("-")

        main_brand = self.main_brand
        if main_brand:
            brand_slug = main_brand.slug
        else:
            brand_slug = _("-")

        return reverse(
            "satchmo_product",
            kwargs={
                "category_slug": category_slug,
                "brand_slug": brand_slug,
                "product_slug": self.slug,
            },
        )

    def save(self, *args, **kwargs):
        self.date_updated = datetime.datetime.now()

        if not self.date_added:
            self.date_added = self.date_updated

        if self.name and not self.slug:
            self.slug = slugify(self.name)

        if not self.sku:
            self.sku = self.slug
        super(Product, self).save(*args, **kwargs)
        ProductPriceLookup.objects.smart_create_for_product(self)

        key = "Product_get_mainImage %s" % (self.id)
        key = key.replace(" ", "-")
        cache.delete(key)

    @property
    def main_category(self):
        """Return the first category for the product"""

        try:
            category = self.category.all()[0]
        except IndexError:
            category = None
        return category

    @property
    def main_brand(self):
        """Return the first brand for the product"""

        try:
            brand = self.brands.all()[0]
        except IndexError:
            brand = None
        return brand

    @property
    def mpn(self):
        return self.productattribute_set.filter(name="mpn").first().value

    @property
    def main_image(self):
        key = "Product_get_mainImage %s" % (self.id)
        key = key.replace(" ", "-")
        img = cache.get(key)
        if img is None:
            img = False
            if self.productimage_set.count() > 0:
                img = self.productimage_set.order_by("sort")[0]
            else:
                # try to get a main image by looking at the parent if this has one
                p = self.get_subtype_with_attr("parent", "product")
                if p:
                    img = p.parent.product.main_image

            if not img:
                # This should be a "Image Not Found" placeholder image
                try:
                    img = ProductImage.objects.filter(product__isnull=True).order_by(
                        "sort"
                    )[0]
                except IndexError:
                    log.warning(
                        "Default product image not found - try `manage.py migrate`"
                    )
            cache.set(key, img)
        return img

    @property
    def is_discountable(self):
        p = self.get_subtype_with_attr("discountable")
        if p:
            return p.discountable
        else:
            return True

    def all_prices(self):
        prices = [
            {
                "price": convert_to_currency(self.unit_price, currency.iso_4217_code),
                "iso_4217_code": currency.iso_4217_code,
                "symbol": currency.symbol,
            }
            for currency in Currency.objects.filter(accepted=True).order_by(
                "iso_4217_code"
            )
        ]
        return prices

    def get_qty_price(self, qty):
        """
        If QTY_DISCOUNT prices are specified, then return the appropriate discount price for
        the specified qty.  Otherwise, return the unit_price
        returns price as a Decimal
        """
        if qty == 1:
            return self.unit_price

        subtype = self.get_subtype_with_attr("get_qty_price")
        if subtype:
            price = subtype.get_qty_price(qty)

        else:
            price = get_product_quantity_price(self, qty)
            if not price:
                price = self.unit_price

        return price

    def get_qty_price_list(self):
        """Return a list of tuples (qty, price)"""
        price_objects = (
            Price.objects.filter(product__id=self.id)
            .exclude(expires__isnull=False, expires__lt=datetime.date.today())
            .select_related()
        )
        prices = [(1, self.unit_price)] + [
            (price.quantity, price.dynamic_price) for price in price_objects
        ]
        return prices

    def in_stock(self):
        subtype = self.get_subtype_with_attr("in_stock")
        if subtype:
            return subtype.in_stock

        return self.items_in_stock > 0

    @property
    def has_full_dimensions(self):
        """Return true if the dimensions all have units and values. Used in shipping calcs. """
        for att in (
            "length",
            "length_units",
            "width",
            "width_units",
            "height",
            "height_units",
        ):
            if self.smart_attr(att) is None:
                return False
        return True

    @property
    def has_full_weight(self):
        """Return True if we have weight and weight units"""
        for att in ("weight", "weight_units"):
            if self.smart_attr(att) is None:
                return False
        return True

    def get_subtypes(self):
        types = []
        try:
            for key in config_value("PRODUCT", "PRODUCT_TYPES"):
                app, subtype = key.split("::")
                try:
                    subclass = getattr(self, subtype.lower())
                    gettype = getattr(subclass, "_get_subtype")
                    subtype = gettype()
                    if subtype not in types:
                        types.append(subtype)
                except models.ObjectDoesNotExist:
                    pass
        except SettingNotSet:
            log.warning("Error getting subtypes, OK if in SyncDB")

        return tuple(types)

    get_subtypes.short_description = _("Product Subtypes")

    def get_subtype_with_attr(self, *args):
        """Get a subtype with the specified attributes.  Note that this can be chained
        so that you can ensure that the attribute then must have the specified attributes itself.

        example:  get_subtype_with_attr('parent') = any parent
        example:  get_subtype_with_attr('parent', 'product') = any parent which has a product attribute
        """
        for subtype_name in self.get_subtypes():
            subtype = getattr(self, subtype_name.lower())
            if hasattr(subtype, args[0]):
                if len(args) == 1:
                    return subtype
                else:
                    found = True
                    for attr in args[1:-1]:
                        if hasattr(subtype, attr):
                            subtype = getattr(self, attr)
                        else:
                            found = False
                            break
                    if found and hasattr(subtype, args[-1]):
                        return subtype

        return None

    def smart_attr(self, attr):
        """Retrieve an attribute, or its parent's attribute if it is null.
        Ex: to get a weight.  obj.smart_attr('weight')"""

        val = getattr(self, attr)
        if val is None:
            for subtype_name in self.get_subtypes():
                subtype = getattr(self, subtype_name.lower())

                if hasattr(subtype, "parent"):
                    subtype = subtype.parent.product

                if hasattr(subtype, attr):
                    val = getattr(subtype, attr)
                    if val is not None:
                        break

        return val

    @property
    def has_variants(self):
        subtype = self.get_subtype_with_attr("has_variants")
        return subtype and subtype.has_variants

    @property
    def get_category(self):
        """
        Return the primary category associated with this product
        """
        subtype = self.get_subtype_with_attr("get_category")
        if subtype:
            return subtype.get_category

        try:
            return self.category.all()[0]
        except IndexError:
            return None

    @property
    def is_downloadable(self):
        """
        If this Product has any subtypes associated with it that are downloadable, then
        consider it downloadable
        """
        return self.get_subtype_with_attr("is_downloadable") is not None

    @property
    def is_subscription(self):
        """
        If this Product has any subtypes associated with it that are subscriptions, then
        consider it subscription based.
        """
        for prod_type in self.get_subtypes():
            subtype = getattr(self, prod_type.lower())
            if hasattr(subtype, "is_subscription"):
                return True
        return False

    @property
    def is_shippable(self):
        """
        If this Product has any subtypes associated with it that are not
        shippable, then consider the product not shippable.
        If it is downloadable, then we don't ship it either.
        """
        if self.shipclass == "DEFAULT":
            subtype = self.get_subtype_with_attr("is_shippable")
            if subtype and not subtype.is_shippable:
                return False
            return True
        elif self.shipclass == "YES":
            return True
        else:
            return False

    def add_template_context(self, context, *args, **kwargs):
        """
        Add context for the product template.
        Call the add_template_context method of each subtype and return the
        combined context.
        """
        subtypes = self.get_subtypes()
        logging.debug("subtypes = %s", subtypes)
        for subtype_name in subtypes:
            subtype = getattr(self, subtype_name.lower())
            if hasattr(subtype, "add_template_context"):
                context = subtype.add_template_context(context, *args, **kwargs)
        return context

    def cheapest_shipping(self):
        from satchmo.shop.models import Config

        shop_details = Config.objects.get_current()
        country = shop_details.country_id

        min_price = None
        min_carrier = None
        if self.is_shippable:
            for method in shipping_methods():
                try:
                    price = method.carrier.price(self.weight, country)
                except:
                    price = None
                if price:
                    if min_price is None or price < min_price:
                        min_price = price
                        min_carrier = method.carrier
        return {"carrier": min_carrier, "price": min_price}

    def days_since_last_stocked(self):
        try:
            brand = self.brands.all()[0]
        except IndexError:
            return None
        days_since_last_stocked = datetime.date.today() - brand.last_restocked
        return days_since_last_stocked

    def stock_due_date(self):
        "Returns the date stock is due"

        if self.items_in_stock < 1:
            try:
                brand = self.brands.all()[0]
            except IndexError:
                return None

            if (
                brand.stock_due_on is not None
                and brand.stock_due_on > datetime.date.today()
            ):
                # If we know when it's coming
                return brand.stock_due_on
            elif (
                brand.last_restocked is not None
                and self.days_since_last_stocked().days < brand.restock_interval
            ):
                # It's within a normal range
                return brand.last_restocked + datetime.timedelta(
                    days=brand.restock_interval
                )
            elif brand.restock_interval is not None:
                # No idea when stock due, give estimate
                return datetime.date.today() + datetime.timedelta(
                    days=brand.restock_interval
                )
            else:
                return None
        return None


def get_all_options(obj, ids_only=False):
    """
    Returns all possible combinations of options for this products OptionGroups as a List of Lists.
    Ex:
    For OptionGroups Color and Size with Options (Blue, Green) and (Large, Small) you'll get
    [['Blue', 'Small'], ['Blue', 'Large'], ['Green', 'Small'], ['Green', 'Large']]
    Note: the actual values will be instances of Option instead of strings
    """
    sublist = []
    masterlist = []
    # Create a list of all the options & create all combos of the options
    for opt in obj.option_group.select_related().all():
        for value in opt.option_set.all():
            if ids_only:
                sublist.append(value.unique_id)
            else:
                sublist.append(value)
        masterlist.append(sublist)
        sublist = []
    results = cross_list(masterlist)
    return results


class CustomProduct(models.Model):
    """
    Product which must be custom-made or ordered.
    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product"), primary_key=True
    )
    downpayment = models.IntegerField(_("Percent Downpayment"), default=20)
    deferred_shipping = models.BooleanField(
        _("Deferred Shipping"),
        help_text=_("Do not charge shipping at checkout for this item."),
        default=False,
    )
    option_group = models.ManyToManyField(
        OptionGroup, verbose_name=_("Option Group"), blank=True
    )

    @property
    def is_shippable(self):
        return not self.deferred_shipping

    @property
    def unit_price(self):
        """
        returns price as a Decimal
        """
        return self.product.unit_price

    def add_template_context(self, context, selected_options, **kwargs):
        """
        Add context for the product template.
        Return the updated context.
        """
        from satchmo.product.utils import serialize_options

        context["options"] = serialize_options(self, selected_options)

        return context

    def get_qty_price(self, qty):
        """
        If QTY_DISCOUNT prices are specified, then return the appropriate discount price for
        the specified qty.  Otherwise, return the unit_price
        returns price as a Decimal
        """
        if qty == 1:
            return self.unit_price

        price = get_product_quantity_price(self.product, qty)
        if not price and qty == 1:  # Prevent a recursive loop.
            price = Decimal("0.00")
        elif not price:
            price = self.product.unit_price

        return price * self.downpayment / 100

    @property
    def full_price(self, qty=1):
        """
        Return the full price, ignoring the deposit.
        """

        price = get_product_quantity_price(self.product, qty)
        if not price:
            price = self.product.unit_price
        return price

    def _get_subtype(self):
        return "CustomProduct"

    def __str__(self):
        return "CustomProduct: %s" % self.product.name

    def get_valid_options(self):
        """
        Returns all of the valid options
        """
        return get_all_options(self, ids_only=True)

    class Meta:
        verbose_name = _("Custom Product")
        verbose_name_plural = _("Custom Products")


class CustomTextField(models.Model):
    """
    A text field to be filled in by a customer.
    """

    name = models.CharField(_("Custom field name"), max_length=255)
    slug = models.SlugField(
        _("Slug"), help_text=_("Auto-generated from name if blank"), blank=True
    )
    products = models.ForeignKey(
        CustomProduct,
        on_delete=models.CASCADE,
        verbose_name=_("Custom Fields"),
        related_name="custom_text_fields",
    )
    sort_order = models.IntegerField(
        _("Sort Order"), help_text=_("The display order for this group.")
    )
    price_change = models.DecimalField(
        _("Price Change"), max_digits=14, decimal_places=6, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, instance=self)
        super(CustomTextField, self).save(*args, **kwargs)

    class Meta:
        ordering = ("sort_order",)


class ConfigurableProduct(models.Model):
    """
    Product with selectable options.
    This is a sort of virtual product that is visible to the customer, but isn't actually stocked on a shelf,
    the specific "shelf" product is determined by the selected options.
    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product"), primary_key=True
    )
    option_group = models.ManyToManyField(
        OptionGroup, blank=True, verbose_name=_("Option Group")
    )
    create_subs = models.BooleanField(
        _("Create Variations"),
        default=False,
        help_text=_(
            "Create ProductVariations for all this product's options.  To use this, you must first add an option, save, then return to this page and select this option."
        ),
    )

    def _get_subtype(self):
        return "ConfigurableProduct"

    def get_all_options(self):
        """
        Returns all possible combinations of options for this products OptionGroups as a List of Lists.
        Ex:
        For OptionGroups Color and Size with Options (Blue, Green) and (Large, Small) you'll get
        [['Blue', 'Small'], ['Blue', 'Large'], ['Green', 'Small'], ['Green', 'Large']]
        Note: the actual values will be instances of Option instead of strings
        """
        sublist = []
        masterlist = []
        # Create a list of all the options & create all combos of the options
        for opt in self.option_group.all():
            for value in opt.option_set.all():
                sublist.append(value)
            masterlist.append(sublist)
            sublist = []
        return cross_list(masterlist)

    def get_valid_options(self):
        """
        Returns unique_ids from get_all_options(), but filters out Options that this
        ConfigurableProduct doesn't have a ProductVariation for.
        """
        variations = self.productvariation_set.filter(product__active="1")
        active_options = [v.unique_option_ids for v in variations]
        all_options = get_all_options(self, ids_only=True)
        return [
            opt
            for opt in all_options
            if self._unique_ids_from_options(opt) in active_options
        ]

    def create_all_variations(self):
        """
        Get a list of all the optiongroups applied to this object
        Create all combinations of the options and create variations
        """
        # Create a new ProductVariation for each combination.
        for options in self.get_all_options():
            self.create_variation(options)

    def create_variation(self, options, name="", sku="", slug=""):
        """Create a productvariation with the specified options.
        Will not create a duplicate."""
        log.debug("Create variation: %s", options)
        variations = self.get_variations_for_options(options)

        # There isn't an existing ProductVariation.
        if not variations:
            variant = Product(items_in_stock=0, name=name)
            optnames = [opt.value for opt in options]
            if not slug:
                slug = slugify("%s-%s" % (self.product.slug, "-".join(optnames)))

            while Product.objects.filter(slug=slug).count():
                slug = "-".join((slug, str(self.product.id)))

            variant.slug = slug

            log.info("Creating variation for [%s] %s", self.product.slug, variant.slug)
            variant.save()

            pv = ProductVariation(product=variant, parent=self)
            pv.save()

            for option in options:
                pv.options.add(option)

            pv.name = name
            pv.sku = sku
            pv.save()

        else:
            variant = variations[0].product
            log.debug("Existing variant: %s", variant)
            dirty = False
            if name and name != variant.name:
                log.debug("Updating name: %s --> %s", self, name)
                variant.name = name
                dirty = True
            if sku and sku != variant.sku:
                variant.sku = sku
                log.debug("Updating sku: %s --> %s", self, sku)
                dirty = True
            if slug:
                # just in case
                slug = slugify(slug)
            if slug and slug != variant.slug:
                variant.slug = slug
                log.debug("Updating slug: %s --> %s", self, slug)
                dirty = True
            if dirty:
                log.debug("Changed existing variant, saving: %s", variant)
                variant.save()
            else:
                log.debug("No change to variant, skipping save: %s", variant)

        return variant

    def _unique_ids_from_options(self, options):
        """
        Takes an iterable of Options (or str(Option)) and outputs a sorted tuple of
        option unique ids suitable for comparing to a productvariation.option_values
        """
        optionlist = []
        for opt in options:
            if isinstance(options[0], Option):
                opt = opt.unique_id
            optionlist.append(opt)

        return sorted_tuple(optionlist)

    def get_product_from_options(self, options):
        """
        Accepts an iterable of either Option object or a sorted tuple of
        options ids.
        Returns the product that matches or None
        """
        options = self._unique_ids_from_options(options)
        pv = None
        if hasattr(self, "_variation_cache"):
            pv = self._variation_cache.get(options, None)
        else:
            for member in self.productvariation_set.all():
                if member.unique_option_ids == options:
                    pv = member
                    break
        if pv:
            return pv.product
        return None

    def get_variations_for_options(self, options):
        """
        Returns a list of existing ProductVariations with the specified options.
        """
        variations = ProductVariation.objects.filter(parent=self)
        for option in options:
            variations = variations.filter(options=option)
        return variations

    def add_template_context(
        self, context, request, selected_options, include_tax, **kwargs
    ):
        """
        Add context for the product template.
        Return the updated context.
        """
        from satchmo.product.utils import productvariation_details, serialize_options

        selected_options = self._unique_ids_from_options(selected_options)
        context["options"] = serialize_options(self, selected_options)
        context["details"] = productvariation_details(
            self.product, include_tax, request.user, request
        )

        return context

    def save(self, *args, **kwargs):
        """
        Right now this only works if you save the suboptions, then go back and choose to create the variations.
        """
        super(ConfigurableProduct, self).save()

        # Doesn't work with admin - the manipulator doesn't add the option_group
        # until after save() is called.
        if self.create_subs and self.option_group.count():
            self.create_all_variations()
            self.create_subs = False
            super(ConfigurableProduct, self).save(*args, **kwargs)

        ProductPriceLookup.objects.smart_create_for_product(self.product)

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def setup_variation_cache(self):
        self._variation_cache = {}
        for member in self.productvariation_set.all():
            key = member.unique_option_ids
            self._variation_cache[key] = member

    class Meta:
        verbose_name = _("Configurable Product")
        verbose_name_plural = _("Configurable Products")

    def __str__(self):
        return self.product.slug


def _protected_dir(instance, filename):
    raw = config_value_safe("PRODUCT", "PROTECTED_DIR", "images/")
    updir = normalize_dir(raw)
    return os.path.join(updir, os.path.basename(filename))


class DownloadableProduct(models.Model):
    """
    This type of Product is a file to be downloaded
    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product"), primary_key=True
    )
    file = FileField(_("File"), upload_to=_protected_dir)
    num_allowed_downloads = models.IntegerField(
        _("Num allowed downloads"), help_text=_("Number of times link can be accessed.")
    )
    expire_minutes = models.IntegerField(
        _("Expire minutes"),
        help_text=_("Number of minutes the link should remain active."),
    )
    active = models.BooleanField(
        _("Active"), help_text=_("Is this download currently active?"), default=True
    )
    is_shippable = False
    is_downloadable = True

    def __str__(self):
        return self.product.slug

    def _get_subtype(self):
        return "DownloadableProduct"

    def create_key(self):
        salt = bin(random.random())
        download_key = hashlib.pbkdf2_hmac(
            "sha256", self.product.name, salt, 100000
        ).hexlify()
        return download_key

    def order_success(self, order, order_item):
        signals.subtype_order_success.send(
            self, product=self, order=order, subtype="download"
        )

    class Meta:
        verbose_name = _("Downloadable Product")
        verbose_name_plural = _("Downloadable Products")


class SubscriptionProduct(models.Model):
    """
    This type of Product is for recurring billing (memberships, subscriptions, payment terms)
    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product"), primary_key=True
    )
    recurring = models.BooleanField(
        _("Recurring Billing"),
        help_text=_(
            "Customer will be charged the regular product price on a periodic basis."
        ),
        default=False,
    )
    recurring_times = models.IntegerField(
        _("Recurring Times"),
        help_text=_(
            "Number of payments which will occur at the regular rate.  (optional)"
        ),
        null=True,
        blank=True,
    )
    expire_length = models.IntegerField(
        _("Duration"),
        help_text=_("Length of each billing cycle"),
        null=True,
        blank=True,
    )
    SUBSCRIPTION_UNITS = (("DAY", _("Days")), ("MONTH", _("Months")))
    expire_unit = models.CharField(
        _("Expire Unit"),
        max_length=5,
        choices=SUBSCRIPTION_UNITS,
        default="DAY",
        null=False,
    )
    SHIPPING_CHOICES = (
        ("0", _("No Shipping Charges")),
        ("1", _("Pay Shipping Once")),
        ("2", _("Pay Shipping Each Billing Cycle")),
    )
    is_shippable = models.IntegerField(
        _("Shippable?"),
        help_text=_("Is this product shippable?"),
        choices=SHIPPING_CHOICES,
    )

    is_subscription = True

    def _get_subtype(self):
        return "SubscriptionProduct"

    def __str__(self):
        return self.product.slug

    @property
    def unit_price(self):
        """
        returns price as a Decimal
        """
        return self.product.unit_price

    def get_qty_price(self, qty, show_trial=True):
        """
        If QTY_DISCOUNT prices are specified, then return the appropriate discount price for
        the specified qty.  Otherwise, return the unit_price
        returns price as a Decimal

        Note: If a subscription has a trial, then we'll return the first trial price, otherwise the checkout won't
        balance and it will look like there are items to be paid on the order.
        """
        if show_trial:
            trial = self.get_trial_terms(0)
        else:
            trial = None

        if trial:
            price = trial.price * qty
        else:
            price = get_product_quantity_price(self.product, qty)
            if not price and qty == 1:  # Prevent a recursive loop.
                price = Decimal("0.00")
            elif not price:
                price = self.product.unit_price
        return price

    def recurring_price(self):
        """
        Get the non-trial price.
        """
        return self.get_qty_price(1, show_trial=False)

    # use order_success() and DownloadableProduct.create_key() to add user to group and perform other tasks
    def get_trial_terms(self, trial=None):
        """Get the trial terms for this subscription"""
        if trial is None:
            return self.trial_set.all().order_by("id")
        else:
            try:
                return self.trial_set.all().order_by("id")[trial]
            except IndexError:
                return None

    def calc_expire_date(self, date=None):
        if date is None:
            date = datetime.datetime.now()
        if self.expire_unit == "DAY":
            expiredate = date + datetime.timedelta(days=self.expire_length)
        else:
            expiredate = add_month(date, n=self.expire_length)

        return expiredate

    class Meta:
        verbose_name = _("Subscription Product")
        verbose_name_plural = _("Subscription Products")


class Trial(models.Model):
    """
    Trial billing terms for subscription products.
    Separating it out lets us have as many trial periods as we want.
    Note that some third party payment processors support only a limited number of trial
    billing periods.  For example, PayPal limits us to 2 trial periods, so if you are using
    PayPal for a billing option, you need to create no more than 2 trial periods for your
    product.  However, gateway based processors like Authorize.net can support as many
    billing periods as you wish.
    """

    subscription = models.ForeignKey(SubscriptionProduct, on_delete=models.CASCADE)
    price = models.DecimalField(
        _("Price"),
        help_text=_(
            "Set to 0 for a free trial.  Leave empty if product does not have a trial."
        ),
        max_digits=10,
        decimal_places=2,
        null=True,
    )
    expire_length = models.IntegerField(
        _("Trial Duration"),
        help_text=_(
            "Length of trial billing cycle.  Leave empty if product does not have a trial."
        ),
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.price)

    def _occurrences(self):
        if self.expire_length:
            return int(self.expire_length / self.subscription.expire_length)
        else:
            return 0

    occurrences = property(fget=_occurrences)

    def calc_expire_date(self, date=None):
        if date is None:
            date = datetime.datetime.now()
        if self.subscription.expire_unit == "DAY":
            expiredate = date + datetime.timedelta(days=self.expire_length)
        else:
            expiredate = add_month(date, n=self.expire_length)

        return expiredate

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Trial Terms")
        verbose_name_plural = _("Trial Terms")


class ProductVariationManager(models.Manager):
    def by_parent(self, parent):
        """Get the list of productvariations which have the `product` as the parent"""
        return ProductVariation.objects.filter(parent=parent)


class ProductVariation(models.Model):
    """
    This is the real Product that is ordered when a customer orders a
    ConfigurableProduct with the matching Options selected

    """

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, verbose_name=_("Product"), primary_key=True
    )
    options = models.ManyToManyField(Option, verbose_name=_("Options"))
    parent = models.ForeignKey(
        ConfigurableProduct, on_delete=models.CASCADE, verbose_name=_("Parent")
    )

    objects = ProductVariationManager()

    class Meta:
        verbose_name = _("Product variation")
        verbose_name_plural = _("Product variations")

    def __str__(self):
        return self.product.slug

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    @property
    def unit_price(self):
        """ Get price based on parent ConfigurableProduct """
        # allow explicit setting of prices.
        try:
            qty_discounts = Price.objects.filter(product__id=self.product.id).exclude(
                expires__isnull=False, expires__lt=datetime.date.today()
            )
            if qty_discounts.count() > 0:
                # Get the price with the quantity closest to the one specified without going over
                return qty_discounts.order_by("-quantity")[0].dynamic_price

            if self.parent.product.unit_price is None:
                log.warn("%s: Unexpectedly no parent.product.unit_price", self)
                return None

        except AttributeError:
            pass

        # calculate from options
        return self.parent.product.unit_price + self.price_delta()

    def _get_optionName(self):
        "Returns the options in a human readable form"
        if self.options.count() == 0:
            return self.parent.verbose_name
        output = self.parent.verbose_name + " ( "
        numProcessed = 0
        # We want the options to be sorted in a consistent manner
        optionDict = dict(
            [(sub.option_group.sort_order, sub) for sub in self.options.all()]
        )
        for optionNum in list(optionDict.keys()).sort():
            numProcessed += 1
            if numProcessed == self.options.count():
                output += optionDict[optionNum].name
            else:
                output += optionDict[optionNum].name + "/"
        output += " )"
        return output

    full_name = property(_get_optionName)

    def _optionkey(self):
        # todo: verify ordering
        optkeys = [
            str(x)
            for x in self.options.values_list("value", flat=True).order_by(
                "option_group__id"
            )
        ]
        return "::".join(optkeys)

    optionkey = property(fget=_optionkey)

    def _get_option_ids(self):
        """
        Return a sorted tuple of all the valid options for this variant.
        """
        qry = self.options.values_list("option_group__id", "value").order_by(
            "option_group"
        )
        ret = [make_option_unique_id(*v) for v in qry]
        return sorted_tuple(ret)

    unique_option_ids = property(_get_option_ids)

    def _get_subtype(self):
        return "ProductVariation"

    def _has_variants(self):
        return True

    has_variants = property(_has_variants)

    def _get_category(self):
        """
        Return the primary category associated with this product
        """
        return self.parent.product.category.all()[0]

    get_category = property(_get_category)

    def _check_optionParents(self):
        groupList = []
        for option in self.options.all():
            if option.option_group.id in groupList:
                return True
            else:
                groupList.append(option.option_group.id)
        return False

    def get_qty_price(self, qty):
        return get_product_quantity_price(
            self.product, qty, delta=self.price_delta(), parent=self.parent.product
        )

    def get_qty_price_list(self):
        """Return a list of tuples (qty, price)"""
        prices = Price.objects.filter(product__id=self.product.id).exclude(
            expires__isnull=False, expires__lt=datetime.date.today()
        )
        if prices.count() > 0:
            # prices directly set, return them
            pricelist = [(price.quantity, price.dynamic_price) for price in prices]
        else:
            prices = self.parent.product.get_qty_price_list()
            price_delta = self.price_delta()

            pricelist = [(qty, price + price_delta) for qty, price in prices]

        return pricelist

    def _is_shippable(self):
        product = self.product
        parent = self.parent.product
        return (
            product.shipclass == "DEFAULT" and parent.shipclass == "DEFAULT"
        ) or product.shipclass == "YES"

    is_shippable = property(fget=_is_shippable)

    def isValidOption(self, field_data, all_data):
        raise ValidationError(
            _("Two options from the same option group cannot be applied to an item.")
        )

    def price_delta(self):
        price_delta = Decimal("0.00")
        for option in self.options.all():
            if option.price_change:
                price_delta += Decimal(option.price_change)
        return price_delta

    def save(self, *args, **kwargs):
        # don't save if the product is a configurableproduct
        if "ConfigurableProduct" in self.product.get_subtypes():
            log.warn(
                "cannot add a productvariation subtype to a product which already is a configurableproduct. Aborting"
            )
            return

        pvs = ProductVariation.objects.filter(parent=self.parent)
        pvs = pvs.exclude(product=self.product)
        for pv in pvs:
            if pv.unique_option_ids == self.unique_option_ids:
                return None  # Don't allow duplicates

        if not self.product.name:
            # will force calculation of default name
            self.name = ""

        super(ProductVariation, self).save(*args, **kwargs)
        ProductPriceLookup.objects.smart_create_for_product(self.product)

    def _set_name(self, name):
        if not name:
            name = self.parent.product.name
            options = [option.name for option in self.options.order_by("option_group")]
            if options:
                name = "%s (%s)" % (name, "/".join(options))
            log.debug("Setting default name for ProductVariant: %s", name)

        self.product.name = name
        self.product.save()

    def _get_name(self):
        return self.product.name

    name = property(fset=_set_name, fget=_get_name)

    def _set_sku(self, sku):
        if not sku:
            sku = self.product.slug
        self.product.sku = sku
        self.product.save()

    def _get_sku(self):
        return self.product.sku

    sku = property(fset=_set_sku, fget=_get_sku)


class ProductPriceLookupManager(models.Manager):
    def by_product(self, product):
        return self.get(productslug=product.slug)

    def delete_expired(self):
        for p in self.filter(expires__lt=datetime.date.today()):
            p.delete()

    def create_for_product(self, product):
        """Create a set of lookup objects for all priced quantities of the Product"""

        self.delete_for_product(product)
        pricelist = product.get_qty_price_list()

        objs = []
        for qty, price in pricelist:
            obj = ProductPriceLookup(
                productslug=product.slug,
                active=product.active,
                price=price,
                quantity=qty,
                discountable=product.is_discountable,
                items_in_stock=product.items_in_stock,
            )
            obj.save()
            objs.append(obj)
        return objs

    def create_for_configurableproduct(self, configproduct):
        """Create a set of lookup objects for all variations of this product"""

        objs = self.create_for_product(configproduct)
        for pv in configproduct.configurableproduct.productvariation_set.filter(
            product__active="1"
        ):
            objs.extend(self.create_for_variation(pv, configproduct))

        return objs

    def create_for_variation(self, variation, parent):
        product = variation.product

        self.delete_for_product(product)
        pricelist = variation.get_qty_price_list()

        objs = []
        for qty, price in pricelist:
            obj = ProductPriceLookup(
                productslug=product.slug,
                parentid=parent.id,
                active=product.active,
                price=price,
                quantity=qty,
                key=variation.optionkey,
                discountable=product.is_discountable,
                items_in_stock=product.items_in_stock,
            )
            obj.save()
            objs.append(obj)
        return objs

    def delete_for_product(self, product):
        for obj in self.filter(productslug=product.slug):
            obj.delete()

    def rebuild_all(self):
        for lookup in self.all():
            lookup.delete()

        ct = 0
        log.debug("ProductPriceLookup rebuilding all pricing")
        for p in Product.objects.active(variations=False):
            prices = self.smart_create_for_product(p)
            ct += len(prices)
        log.info("ProductPriceLookup built %i prices", ct)

    def smart_create_for_product(self, product):
        subtypes = product.get_subtypes()
        if "ConfigurableProduct" in subtypes:
            return self.create_for_configurableproduct(product)
        elif "ProductVariation" in subtypes:
            return self.create_for_variation(
                product.productvariation, product.productvariation.product
            )
        else:
            return self.create_for_product(product)


class ProductPriceLookup(models.Model):
    """
    A denormalized object, used to quickly provide
    details needed for productvariation display, without way too many database hits.
    """

    key = models.CharField(max_length=60, null=True)
    parentid = models.IntegerField(null=True)
    productslug = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=14, decimal_places=6)
    quantity = models.IntegerField()
    active = models.BooleanField(default=False)
    discountable = models.BooleanField(default=False)
    items_in_stock = models.IntegerField()

    objects = ProductPriceLookupManager()

    def _product(self):
        return Product.objects.get(slug=self.productslug)

    product = property(fget=_product)

    def _dynamic_price(self):
        """Get the current price as modified by all listeners."""
        signals.satchmo_price_query.send(
            self, price=self, slug=self.productslug, discountable=self.discountable
        )
        return self.price

    dynamic_price = property(fget=_dynamic_price)


class ProductAttribute(models.Model):
    """
    Allows arbitrary name/value pairs (as strings) to be attached to a product.
    This is a very quick and dirty way to add extra info to a product.
    If you want more structure than this, create your own subtype to add
    whatever you want to your Products.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.SlugField(_("Attribute Name"), max_length=100)
    value = models.CharField(_("Value"), max_length=255)

    class Meta:
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")


class Price(models.Model):
    """A Price for a product.

    Separating it out lets us have different prices for the same
    product for different purposes.  For example for quantity
    discounts.  The current price should be the one with the earliest
    expires date, and the highest quantity that's still below the user
    specified (IE: ordered) quantity, that matches a given product.

    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(_("Price"), max_digits=14, decimal_places=6)
    quantity = models.IntegerField(
        _("Discount Quantity"),
        default=2,
        help_text=_("Use this price only for this quantity or higher"),
    )
    expires = models.DateField(_("Expires"), null=True, blank=True)

    def __str__(self):
        return str(self.price)

    @property
    def dynamic_price(self):
        """Get the current price as modified by all listeners."""
        signals.satchmo_price_query.send(self, price=self)
        return self.price

    def save(self, *args, **kwargs):
        prices = Price.objects.filter(product=self.product, quantity=self.quantity)
        # Jump through some extra hoops to check expires - if there's
        # a better way to handle this field I can't think of
        # it. Expires needs to be able to be set to None in cases
        # where there is no expiration date.
        if self.expires:
            prices = prices.filter(expires=self.expires)
        else:
            prices = prices.filter(expires__isnull=True)
        if self.id:
            prices = prices.exclude(id=self.id)
        if prices.count():
            return None  # Duplicate Price

        super(Price, self).save(*args, **kwargs)
        ProductPriceLookup.objects.smart_create_for_product(self.product)

    class Meta:
        ordering = ["expires", "-quantity"]
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        unique_together = (("product", "quantity", "expires"),)


class ProductImage(models.Model):
    """
    A picture of an item.  Can have many pictures associated with an item.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    picture = models.ImageField(
        verbose_name=_("Picture"), upload_to="products/", max_length=200
    )
    caption = models.CharField(
        _("Optional caption"), max_length=255, null=True, blank=True
    )
    sort = models.IntegerField(_("Sort Order"))
    # If it's a swatch we can style differently
    is_swatch = models.BooleanField(_("Is Swatch"), default=True)

    class Meta:
        ordering = ["sort"]
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        if self.product:
            return "Image of Product %s" % self.product.slug
        elif self.caption:
            return 'Image with caption "%s"' % self.caption
        else:
            return "%s" % self.picture

    def _get_filename(self):
        if self.product:
            return "%s-%s" % (self.product.slug, self.id)
        else:
            return "default"

    _filename = property(_get_filename)


class IngredientsList(models.Model):
    description = models.CharField(max_length=255)
    ingredients = models.TextField(_("Ingredients listing"))

    def __str__(self):
        return "%s" % (self.description)


class Instruction(models.Model):
    description = models.CharField(max_length=255)
    instructions = models.TextField(_("Usage Instructions"))

    def __str__(self):
        return "%s" % (self.description)


class Precaution(models.Model):
    description = models.CharField(max_length=255)
    precautions = models.TextField(_("Precautions"))

    def __str__(self):
        return "%s" % (self.description)


def get_product_quantity_price(product, quantity=1, delta=Decimal("0.00"), parent=None):
    """
    Returns price as a Decimal else None.
    First checks the product, if none, then checks the parent.
    """

    if quantity == 1:
        return self.unit_price

    quantity_discounts = product.price_set.exclude(
        expires__isnull=False, expires__lt=datetime.date.today()
    ).filter(quantity__lte=quantity)

    if quantity_discounts.count() > 0:
        # Get the price with the quantity closest to the one specified without going over
        val = quantity_discounts.order_by("-quantity")[0].dynamic_price
        try:
            if not isinstance(val, Decimal):
                val = Decimal(val)
            return val + delta
        except TypeError:
            return val + delta
    else:
        if parent:
            return get_product_quantity_price(parent, quantity, delta=delta)
        return None


def make_option_unique_id(groupid, value):
    return "%s-%s" % (str(groupid), str(value))


def sorted_tuple(lst):
    ret = []
    for x in lst:
        if x not in ret:
            ret.append(x)
    ret.sort()
    return tuple(ret)


def split_option_unique_id(uid):
    "reverse of make_option_unique_id"

    parts = uid.split("-")
    return (parts[0], "-".join(parts[1:]))


from . import listeners

satchmo_search.connect(listeners.default_product_search_listener, Product)
log.debug("registered base search listener")
