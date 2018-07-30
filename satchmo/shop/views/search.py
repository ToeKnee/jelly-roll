from django.shortcuts import render
from satchmo.product.models import Product
from satchmo.shop import signals


def search_view(request, template="search.html"):
    """Perform a search based on keywords and categories in the form submission"""
    if request.method == "GET":
        data = request.GET
    else:
        data = request.POST

    keywords = data.get('keywords', '').split(' ')
    category = data.get('category', None)

    keywords = [_f for _f in keywords if _f]

    results = {}

    # this signal will usually call listeners.default_product_search_listener
    signals.satchmo_search.send(Product, request=request,
                                category=category, keywords=keywords, results=results)

    context = {
        'results': results,
        'category': category,
        'keywords': keywords
    }
    return render(request, template, context)
