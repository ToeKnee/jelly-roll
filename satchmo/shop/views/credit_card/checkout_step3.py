####################################################################
# Last step in the order process - confirm the info and process it
#####################################################################

import datetime
import sys
from django import http
from django.conf import settings
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader
from satchmo.shop.models import Cart, CartItem, Config
from satchmo.contact.models import Order, OrderItem, OrderStatus

#Import the appropriate credit card processing back end
__import__(settings.CREDIT_PROCESSOR)
credit_processor = sys.modules[settings.CREDIT_PROCESSOR]

def confirm_info(request):
    if not request.session.get('orderID', False):
        return http.HttpResponseRedirect('%s/checkout' % (settings.SHOP_BASE))
    if request.session.get('cart',False):
        tempCart = Cart.objects.get(id=request.session['cart'])
        if tempCart.numItems == 0:
            return render_to_response('checkout_empty_cart.html',RequestContext(request))
    else:
        return render_to_response('checkout_empty_cart.html',RequestContext(request))    
    orderToProcess = Order.objects.get(id=request.session['orderID'])
    if request.POST:
        #Do the credit card processing here & if successful, empty the cart and update the status
        processor = credit_processor.PaymentProcessor()
        processor.prepareData(orderToProcess)
        results, reason_code, msg = processor.process()
        if results:
            tempCart.empty()
            #Update status
            status = OrderStatus()
            status.status = "Pending"
            status.notes = "Order successfully submitted"
            status.timeStamp = datetime.datetime.now()
            status.order = orderToProcess #For some reason auto_now_add wasn't working right in admin
            status.save()
            #del request.session['orderID']
            #Redirect to the success page
            return http.HttpResponseRedirect(urlresolvers.reverse('satchmo_checkout-success')
        #Since we're not successful, let the user know via the confirmation page
        else:
            errors = msg
            return render_to_response('checkout_confirm.html', {'order': orderToProcess, 'errors': errors}, RequestContext(request))
    else:
        return render_to_response('checkout_confirm.html', {'order': orderToProcess}, RequestContext(request))
