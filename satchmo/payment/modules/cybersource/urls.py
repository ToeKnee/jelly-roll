from django.conf.urls import *
from satchmo.configuration import config_value, config_get_group

config = config_get_group('PAYMENT_CYBERSOURCE')

urlpatterns = patterns('satchmo',
     (r'^$', 'payment.modules.cybersource.views.pay_ship_info', {}, 'CYBERSOURCE_satchmo_checkout-step2'),
     (r'^confirm/$', 'payment.modules.cybersource.views.confirm_info', {}, 'CYBERSOURCE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {}, 'CYBERSOURCE_satchmo_checkout-success'),
)
