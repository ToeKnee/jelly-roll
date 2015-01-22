from django.conf.urls import *
from satchmo.configuration import config_get_group

config = config_get_group('PAYMENT_PROTX')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.protx.views.pay_ship_info', 
        {}, 'PROTX_satchmo_checkout-step2'),

     (r'^confirm/$', 'payment.modules.protx.views.confirm_info', 
        {}, 'PROTX_satchmo_checkout-step3'),

    (r'^secure3d/$', 'payment.modules.protx.views.confirm_secure3d', 
       {}, 'PROTX_satchmo_checkout-secure3d'),

     (r'^success/$', 'payment.views.checkout.success', 
        {}, 'PROTX_satchmo_checkout-success'),
)