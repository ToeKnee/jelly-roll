from django.conf.urls import *
from satchmo.configuration import config_value, config_get_group

config = config_get_group('PAYMENT_DUMMY')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.dummy.views.pay_ship_info', {}, 'DUMMY_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.dummy.views.confirm_info', {}, 'DUMMY_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {}, 'DUMMY_satchmo_checkout-success'),
)
