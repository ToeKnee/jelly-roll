from django.conf.urls import *
from satchmo.configuration import config_get_group

config = config_get_group('PAYMENT_PAYPAL')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.paypal.views.pay_ship_info', {}, 'PAYPAL_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.paypal.views.confirm_info', {}, 'PAYPAL_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {}, 'PAYPAL_satchmo_checkout-success'),
     (r'^ipn/$', 'payment.modules.paypal.views.ipn', {}, 'PAYPAL_satchmo_checkout-ipn'),
)
