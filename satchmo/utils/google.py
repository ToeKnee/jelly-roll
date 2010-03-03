from satchmo.product.models import Product
from string import lower

from django.shortcuts import render_to_response
from django.template import RequestContext
from satchmo.configuration.functions import config_choice_values
from satchmo.configuration.functions import config_get

def get_google_card_type(card):
    allowed_payment_types = ["AmericanExpress", "Cash", "Check", "Discover", "GoogleCheckout", "MasterCard", "Visa", "wiretransfer"]
    for type in allowed_payment_types:
        if lower(card) == lower(type):
            return type
    return None

def product_feed(request):
    products = Product.objects.filter(active=True)
    payment_modules = config_choice_values("PAYMENT", "MODULES")

    payment_types = []
    payment_notes = []
    for type, module in payment_modules:
        payment_type = unicode(config_get(type, "LABEL"))
        g_payment_type = get_google_card_type(payment_type)
        if g_payment_type:
            payment_types.append(g_payment_type)
        else:
            payment_notes.append(payment_type)
        for type, choice in config_choice_values(type, "CREDITCHOICES"):
            g_payment_type = get_google_card_type(choice)
            if g_payment_type:
                payment_types.append(g_payment_type)
            else:
                payment_notes.append(choice)

    # Make the list unique
    set(payment_types)
    set(payment_notes)
    return render_to_response("product_feed.xml", {'products': products, "payment_types": payment_types, "payment_notes": payment_notes}, context_instance=RequestContext(request))
