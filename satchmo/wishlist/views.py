from django.conf import settings
from django.core import urlresolvers
from django.dispatch import dispatcher
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.safestring import mark_safe
from django.utils.simplejson.encoder import JSONEncoder
from django.utils.translation import ugettext_lazy as _
from satchmo.contact.models import Contact
from satchmo.contact.signals import order_success
from satchmo.product.models import Product
from satchmo.product.views import find_product_template
from satchmo.shop.models import Cart
from satchmo.shop.signals import satchmo_cart_changed
from satchmo.shop.views.cart import product_from_post
from satchmo.shop.views.utils import bad_or_missing
from satchmo.wishlist.models import ProductWish
import logging


log = logging.getLogger('wishlist.view')

def wishlist_view(request, message=""):
    try:
        contact = Contact.objects.from_request(request)
    except Contact.DoesNotExist:
        return _wishlist_requires_login(request)
        
    wishes = ProductWish.objects.filter(contact=contact)

    ctx = RequestContext(request, {
        'wishlist' : wishes,
        'wishlist_message' : message,
    })
    
    return render_to_response('wishlist/index.html', ctx)
    
def wishlist_add(request):
    """Add an item to the wishlist."""
    try:
        contact = Contact.objects.from_request(request)
    except Contact.DoesNotExist:
        return _wishlist_requires_login(request)
        
    log.debug('FORM: %s', request.POST)
    formdata = request.POST.copy()
    productslug = None
    if formdata.has_key('productname'):
        productslug = formdata['productname']
    try:
        product, details = product_from_post(productslug, formdata)
        template = find_product_template(product)
        
    except (Product.DoesNotExist, MultiValueDictKeyError):
        log.debug("Could not find product: %s", productslug)
        return bad_or_missing(request, _('The product you have requested does not exist.'))
        
    wish = ProductWish.objects.create_if_new(product, contact, details)
    url = urlresolvers.reverse('satchmo_wishlist_view')
    return HttpResponseRedirect(url)

def wishlist_add_ajax(request, template="json.html"):
    data = {'errors': []}
    product = None
    formdata = request.POST.copy()
    productslug = formdata['productname']

    log.debug('WISHLIST AJAX: slug=%s', productslug)
    try:
        product, details = product_from_post(productslug, formdata)

    except (Product.DoesNotExist, MultiValueDictKeyError):
        log.warn("Could not find product: %s", productname)
        product = None

    if not product:
        data['errors'].append(('product', _('The product you have requested does not exist.')))

    else:
        data['id'] = product.id
        data['name'] = product.translated_name()
        
    if not data['errors']:
        wish = ProductWish.objects.create_if_new(product, contact, details)    
        data['results'] = _('Success')
    else:
       data['results'] = _('Error')

    encoded = simplejson.dumps(data)
    encoded = mark_safe(encoded)
    log.debug('WISHLIST AJAX: %s', data)
    
    return render_to_response(template, {'json' : encoded})

def wishlist_move_to_cart(request):
    wish, msg = _wish_from_post(request)
    if wish:
        cart = Cart.objects.from_request(request, create=True)
        if cart.add_item(wish.product, number_added=1, details=wish.details) == False:
            return wishlist_view(request, message=_("Not enough items of '%s' in stock.") % wish.product.translated_name())
            
        url = urlresolvers.reverse('satchmo_cart')
        dispatcher.send(signal=satchmo_cart_changed, cart=cart, request=request)
        return HttpResponseRedirect(url)
    else:
        return wishlist_view(request)
        
    
def wishlist_remove(request):
    contact = Contact.objects.from_request(request)
    if not contact:
        return _wishlist_requires_login(request)
            
    success, msg = _wishlist_remove(request)
        
    return wishlist_view(request, message=msg)

def wishlist_remove_ajax(request, template="json.html"):
    success, msg = _wishlist_remove(request)

    data = {
        'success' : success,
        'wishlist_message' : msg
    }
    encoded = simplejson.dumps(data)
    encoded = mark_safe(encoded)
    
    return render_to_response(template, {'json' : encoded})
    
def _wish_from_post(request):
    wid = request.POST.get('id', None)
    msg = ""
    wish = None
    if wid:
        try:
            wid = int(wid)
        except (TypeError, ValueError):
            msg = _("No such wishlist item.")
            wid = -1
        
        if wid > -1:
            contact = Contact.objects.from_request(request)
            if not contact:
                msg = _("You must be logged in to do that.")
            else:
                try:
                    wish = ProductWish.objects.get(contact=contact, id=wid)
                except ProductWish.DoesNotExist:
                    msg = _("No such wishlist item.")
        else:
            msg = _("No such wishlist item.")
            
    return wish, msg
    
def _wishlist_remove(request):
    success = False
    msg = ""
    wish, msg = _wish_from_post(request)
    if wish:
        success = True
        wish.delete()

    return success, msg

def _remove_wishes_on_order(instance=None):
    log.debug("Caught order success, inspecting for wishes to remove.")
    if instance:
        products = [item.product for item in instance.orderitem_set.all()]
        for wish in ProductWish.objects.filter(contact = instance.contact, product__in = products):
            log.debug('removing fulfilled wish for: %s', wish)
            wish.delete()

dispatcher.connect(_remove_wishes_on_order, signal=order_success)

def _wishlist_requires_login(request):
    log.debug("wishlist requires login")
    ctx = RequestContext(request, {
        'login_url' : settings.LOGIN_URL
        })
    return render_to_response('wishlist/login_required.html', ctx)
