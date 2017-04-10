from django import http
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import select_template
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.generic.list import ListView

from satchmo.configuration import config_value
from satchmo.currency.utils import (
    currency_for_request,
    money_format,
)
from satchmo.discount.utils import find_best_auto_discount
from satchmo.product.brand.models import Brand
from satchmo.product.models import (
    Category,
    ConfigurableProduct,
    IngredientsList,
    Product,
    sorted_tuple,
)
from satchmo.product.signals import index_prerender
from satchmo.product.utils import get_tax
from satchmo.shop.views.utils import bad_or_missing
from satchmo.utils.json import json_encode

import logging
log = logging.getLogger(__name__)

NOTSET = object()


# ---- Helpers ----
def find_product_template(product, producttypes=None):
    """Searches for the correct override template given a product."""
    if producttypes is None:
        producttypes = product.get_subtypes()

    templates = ["product/detail_%s.html" % x.lower() for x in producttypes]
    templates.append('base_product.html')
    return select_template(templates)


def optionids_from_post(configurableproduct, POST):
    """Reads through the POST dictionary and tries to match keys to possible `OptionGroup` ids
    from the passed `ConfigurableProduct`"""
    chosen_options = []
    for opt_grp in configurableproduct.option_group.all():
        if str(opt_grp.id) in POST:
            chosen_options.append('%s-%s' % (opt_grp.id, POST[str(opt_grp.id)]))
    return sorted_tuple(chosen_options)


# ---- Views ----
def category_index(request, template="product/category_index.html", root_only=True):
    """Display all categories.

    Parameters:
    - root_only: If true, then only show root categories.
    """
    cats = Category.objects.root_categories()
    ctx = {
        'categorylist': cats
    }
    return render_to_response(template, RequestContext(request, ctx))


def category_view(request, slug, parent_slugs='', template='base_category.html'):
    """Display the category, its child categories, and its products.

    Parameters:
     - slug: slug of category
     - parent_slugs: ignored
    """
    try:
        category = Category.objects.get(slug=slug)
        products = category.active_products()
        sale = find_best_auto_discount(products)

    except Category.DoesNotExist:
        return bad_or_missing(request, _('The category you have requested does not exist.'))

    child_categories = category.get_all_children()

    ctx = {
        'category': category,
        'child_categories': child_categories,
        'sale': sale,
        'products': products,
    }
    index_prerender.send(Product, request=request, context=ctx, category=category, object_list=products)
    return render_to_response(template, RequestContext(request, ctx))


def display_featured(limit=None, random=None):
    """
    Used by the index generic view to choose how the featured products are displayed.
    Items can be displayed randomly or all in order
    """
    if random:
        random_display = random
    else:
        random_display = config_value('SHOP', 'RANDOM_FEATURED')
    if limit:
        num_to_display = limit
    else:
        num_to_display = config_value('SHOP', 'NUM_DISPLAY')
    q = Product.objects.featured_by_site().filter(items_in_stock__gt=0)
    if not random_display:
        return q[:num_to_display]
    else:
        return q.order_by('?')[:num_to_display]


def get_configurable_product_options(request, id):
    """Used by admin views"""
    cp = get_object_or_404(ConfigurableProduct, product__id=id)
    options = ''
    for og in cp.option_group.all():
        for opt in og.option_set.all():
            options += '<option value="%s">%s</option>' % (opt.id, str(opt))
    if not options:
        return '<option>No valid options found in "%s"</option>' % cp.product.slug
    return http.HttpResponse(options, mimetype="text/html")


@never_cache
def get_product(request, category_slug, brand_slug, product_slug, selected_options=(),
                include_tax=NOTSET, default_view_tax=NOTSET):
    """Basic product view"""
    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    try:
        category = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        category = None
    brand = Brand.objects.get(slug=brand_slug)

    if default_view_tax == NOTSET:
        default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if default_view_tax:
        include_tax = True

    elif include_tax == NOTSET:
        include_tax = default_view_tax

    if default_view_tax:
        include_tax = True

    subtype_names = product.get_subtypes()

    if 'ProductVariation' in subtype_names:
        selected_options = product.productvariation.unique_option_ids
        # Display the ConfigurableProduct that this ProductVariation belongs to.
        product = product.productvariation.parent.product
        subtype_names = product.get_subtypes()

    best_discount = find_best_auto_discount(product)

    extra_context = {
        'product': product,
        'category': category,
        'brand': brand,
        'default_view_tax': default_view_tax,
        'sale': best_discount,
    }

    # Get the template context from the Product.
    extra_context = product.add_template_context(
        context=extra_context,
        request=request, selected_options=selected_options,
        include_tax=include_tax, default_view_tax=default_view_tax
    )

    if include_tax:
        tax_amt = get_tax(request.user, product, 1)
        extra_context['product_tax'] = tax_amt
        extra_context['price_with_tax'] = product.unit_price + tax_amt

    template = find_product_template(product, producttypes=subtype_names)
    context = RequestContext(request, extra_context)
    return http.HttpResponse(template.render(context))


def get_price(request, product_slug):
    """Get base price for a product, returning the answer encoded as JSON."""
    quantity = 1

    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
    except Product.DoesNotExist:
        return http.HttpResponseNotFound(json_encode(('', _("not available"))), mimetype="text/javascript")

    prod_slug = product.slug

    if request.method == "POST" and 'quantity' in request.POST:
        quantity = int(request.POST['quantity'])

    currency_code = currency_for_request(request)
    if 'ConfigurableProduct' in product.get_subtypes():
        cp = product.configurableproduct
        chosen_options = optionids_from_post(cp, request.POST)
        pvp = cp.get_product_from_options(chosen_options)

        if not pvp:
            return http.HttpResponse(json_encode(('', _("not available"))), mimetype="text/javascript")
        prod_slug = pvp.slug

        price = money_format(pvp.get_qty_price(quantity), currency_code)
    else:
        price = money_format(product.get_qty_price(quantity), currency_code)

    if not price:
        return http.HttpResponse(json_encode(('', _("not available"))), mimetype="text/javascript")

    return http.HttpResponse(json_encode((prod_slug, price)), mimetype="text/javascript")


def get_price_detail(request, product_slug):
    """Get all price details for a product, returning the response encoded as JSON."""
    results = {
        "success": False,
        "message": _("not available")
    }
    price = None

    if request.method == "POST":
        reqdata = request.POST
    else:
        reqdata = request.GET

    try:
        product = Product.objects.get_by_site(active=True, slug=product_slug)
        found = True

        if 'quantity' in reqdata:
            quantity = int(reqdata['quantity'])
        else:
            quantity = 1

        if 'ConfigurableProduct' in product.get_subtypes():
            cp = product.configurableproduct
            chosen_options = optionids_from_post(cp, reqdata)
            product = cp.get_product_from_options(chosen_options)

        if product:
            price = product.get_qty_price(quantity)
            base_tax = get_tax(request.user, product, quantity)
            price_with_tax = price + base_tax

            currency_code = currency_for_request(request)
            results['slug'] = product.slug
            results['currency_price'] = money_format(price, currency_code)
            results['price'] = float(price)
            results['tax'] = float(base_tax)
            results['currency_tax'] = money_format(base_tax, currency_code)
            results['currency_price_with_tax'] = money_format(price_with_tax, currency_code)
            results['price_with_tax'] = float(price_with_tax)
            results['success'] = True
            results['message'] = ""

    except Product.DoesNotExist:
        found = False

    data = json_encode(results)
    if found:
        return http.HttpResponse(data, mimetype="text/javascript")
    else:
        return http.HttpResponseNotFound(data, mimetype="text/javascript")


class IngredientsListView(ListView):
    template_name = "product/ingredients_list.html"

    def get_queryset(self):
        return IngredientsList.objects.all().order_by("description")
