from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from satchmo.discount.utils import find_best_auto_discount
from satchmo.product import signals
from satchmo.product.brand.models import Brand, BrandCategory

import logging
log = logging.getLogger(__name__)


def brand_list(request):
    brands = Brand.objects.active()
    ctx = {
        'brands': brands,
    }
    signals.index_prerender.send(Brand, request=request, context=ctx, object_list=brands)
    requestctx = RequestContext(request, ctx)
    return render_to_response('product/brand/index.html', requestctx)


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

    ctx = RequestContext(request, ctx)
    return render_to_response('product/brand/view_brand.html', ctx)


def brand_category_page(request, brandname, catname):
    try:
        cat = BrandCategory.objects.by_slug(brandname, catname)

    except Brand.DoesNotExist:
        raise Http404(_('Brand "%s" does not exist') % brandname)

    except BrandCategory.DoesNotExist:
        raise Http404(_('No category "%s" in brand "%s"') % (catname, brandname))

    products = cat.active_products()
    sale = find_best_auto_discount(products)

    ctx = RequestContext(request, {
        'products': products,
        'brand': cat,
        'sale': sale,
    })
    return render_to_response('product/brand/view_brand.html', ctx)
