from django.conf.urls import *
from satchmo.configuration import config_value, config_get_group

config = config_get_group('PAYMENT_AUTHORIZENET')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.authorizenet.views.pay_ship_info', {}, 'AUTHORIZENET_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.authorizenet.views.confirm_info', {}, 'AUTHORIZENET_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {}, 'AUTHORIZENET_satchmo_checkout-success'),
)
