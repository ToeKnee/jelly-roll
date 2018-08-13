from django.http import Http404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from satchmo.discount.utils import find_best_auto_discount
from satchmo.product import signals
from satchmo.product.models import Category
from satchmo.product.brand.models import Brand

import logging
log = logging.getLogger(__name__)


def brand_list(request):
    brands = Brand.objects.active()
    ctx = {
        'brands': brands,
    }
    signals.index_prerender.send(Brand, request=request, context=ctx, object_list=brands)

    return render(request, 'product/brand/index.html', ctx)


def brand_page(request, brandname):
    try:
        brand = Brand.objects.by_slug(brandname)
    except Brand.DoesNotExist:
        raise Http404(_('Brand "%s" does not exist') % brandname)

    products = brand.active_products()
    sale = find_best_auto_discount(products)

    ctx = {
        'brand': brand,
        'products': products,
        'sale': sale,
    }

    return render(request, 'product/brand/view_brand.html', ctx)


def brand_category_page(request, category_slug, brand_slug):
    if category_slug != "-":
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404(_('Cagtegory "%s" does not exist') % category_slug)
        try:
            brand = category.brands.get(slug=brand_slug)
        except Brand.DoesNotExist:
            raise Http404(_('Brand "%s" does not exist in "%s"') % (brand_slug, category_slug))
    else:
        category = None
        try:
            brand = Brand.objects.get(slug=brand_slug)
        except Brand.DoesNotExist:
            raise Http404(_('Brand "%s" does not exist in "%s"') % (brand_slug, category_slug))

    if category:
        products = brand.active_products(category)
    else:
        products = brand.active_products()
    sale = find_best_auto_discount(products)

    context = {
        'products': products,
        'category': category,
        'brand': brand,
        'sale': sale,
    }

    return render(request, 'product/brand/view_brand.html', context)
