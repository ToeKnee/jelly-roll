from django.conf.urls import *
from satchmo.configuration import config_value, config_get_group


config = config_get_group('PAYMENT_TRUSTCOMMERCE')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.trustcommerce.views.pay_ship_info', {}, 'TRUSTCOMMERCE_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.trustcommerce.views.confirm_info', {}, 'TRUSTCOMMERCE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {}, 'TRUSTCOMMERCE_satchmo_checkout-success'),
)