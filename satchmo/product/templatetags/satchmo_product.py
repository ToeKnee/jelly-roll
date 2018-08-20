from django import template
from satchmo import caching
from satchmo.product.models import Product
from satchmo.shop.templatetags import get_filter_args
from satchmo.product.queries import bestsellers
from satchmo.product.views import display_featured
from satchmo.currency.models import Currency
from satchmo.currency.utils import convert_to_currency, currency_for_request, money_format

register = template.Library()


def is_producttype(product, ptype):
    """Returns True if product is ptype"""
    if ptype in product.get_subtypes():
        return True
    else:
        return False


register.filter('is_producttype', is_producttype)


def product_count(category, args=''):
    """Get a count of products for the base object.

    If `category` is None, then count everything.
    If it is a `Category` object then count everything in the category and subcategories.
    """
    args, kwargs = get_filter_args(args, boolargs=('variations'))
    variations = kwargs.get('variations', False)
    try:
        ct = caching.cache_get('product_count', category, variations)
    except caching.NotCachedError:
        if not category:
            ct = Product.objects.active_by_site(variations=variations).count()
        else:
            ct = category.active_products(
                include_children=True,
                variations=variations
            ).count()

        caching.cache_set('product_count', category, args, value=ct)
    return ct


register.filter('product_count', product_count)


def product_images(product, args=""):
    args, kwargs = get_filter_args(
        args,
        keywords=('include_main', 'maximum'),
        boolargs=('include_main'),
        intargs=('maximum'),
        stripquotes=True)

    q = product.productimage_set
    if kwargs.get('include_main', True):
        q = q.all()
    else:
        main = product.main_image
        q = q.exclude(id=main.id)

    maximum = kwargs.get('maximum', -1)
    if maximum > -1:
        q = list(q)[:maximum]

    return q


register.filter('product_images', product_images)


def smart_attr(product, key):
    """
    Run the smart_attr function on the spec'd product
    """
    return product.smart_attr(key)


register.filter('smart_attr', smart_attr)


def product_sort_by_price(products):
    """
    Sort a product list by unit price

    Example::

        {% for product in products|product_sort_by_price %}
    """

    if products:
        fast = sorted([(product.unit_price, product) for product in products])
        return list(zip(*fast))[1]


register.filter('product_sort_by_price', product_sort_by_price)


@register.inclusion_tag('bestsellers.html')
def show_bestsellers(limit=5):
    ''' Renders best sellers list '''
    products = bestsellers(limit)
    return {"bestsellers": products}


@register.inclusion_tag('featured.html', takes_context=True)
def show_featured(context, limit=1, random=True):
    ''' Renders best sellers list '''
    products = display_featured(limit, random)
    context["featured"] = products
    return context


@register.inclusion_tag('product/quick_product.html', takes_context=True)
def quick_product(context, product, show_wishlist=True):
    ''' Renders a product in a way that is usefull for a list '''
    if show_wishlist == "False":
        show_wishlist = False

    context.update({
        "product": product,
        "show_wishlist": show_wishlist
    })
    return context


@register.inclusion_tag('product/full_product.html', takes_context=True)
def full_product(context, product):
    ''' Renders a product in a way that is useful for the product detail page '''
    context["product"] = product
    current_currency = currency_for_request(context.get('request'))
    context['other_prices'] = [
        money_format(
            convert_to_currency(
                product.unit_price, currency.iso_4217_code
            ),
            currency.iso_4217_code
        )
        for currency
        in Currency.objects.filter(
            accepted=True
        ).exclude(
            iso_4217_code=current_currency
        ).order_by(
            'iso_4217_code'
        )
    ]
    return context
