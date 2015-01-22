from django.conf.urls import *
from satchmo.configuration import config_get_group, config_value

config = config_get_group('PAYMENT_WORLDPAY')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.worldpay.views.pay_ship_info',        {}, 'WORLDPAY_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.worldpay.views.confirm_info', {}, 'WORLDPAY_satchmo_checkout-step3'),
     (r'^success/$', 'payment.modules.worldpay.views.success',      {}, 'WORLDPAY_satchmo_checkout-success'),
)
 
