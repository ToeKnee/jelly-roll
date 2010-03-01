from satchmo.product.models import Product

from django.shortcuts import render_to_response
from django.template import RequestContext
from satchmo.configuration.functions import config_choice_values
from satchmo.configuration.functions import config_get


def product_feed(request):
    products = Product.objects.filter(active=True)
    payment_modules = config_choice_values("PAYMENT", "MODULES")
    payment_types = []
    for type, module in payment_modules:
        payment_types.append(unicode(config_get(type, "LABEL")))
        for type, choice in config_choice_values(type, "CREDITCHOICES"):
            payment_types.append(choice)

    # Make the list unique
    set(payment_types)
    return render_to_response("product_feed.xml", {'products': products, "payment_types": payment_types}, context_instance=RequestContext(request))
