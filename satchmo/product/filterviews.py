from django.shortcuts import render
from satchmo.configuration.functions import config_value
from satchmo.product.queries import bestsellers


def display_bestsellers(request, count=0, template="product/best_sellers.html"):
    """Display a list of the products which have sold the most"""
    if count == 0:
        count = config_value("SHOP", "NUM_PAGINATED")

    ctx = {"products": bestsellers(count)}
    return render(request, template, ctx)
