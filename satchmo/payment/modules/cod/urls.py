from django.conf.urls import *
from satchmo.configuration import config_value, config_get_group

config = config_get_group('PAYMENT_COD')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.cod.views.pay_ship_info', {}, 'COD_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.cod.views.confirm_info', {}, 'COD_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {}, 'COD_satchmo_checkout-success'),
)
