from django.conf.urls import *
from satchmo.configuration import config_get_group

config = config_get_group('PAYMENT_GIFTCERTIFICATE')

urlpatterns = patterns('satchmo',
     (r'^$', 'giftcertificate.views.pay_ship_info', {}, 'GIFTCERTIFICATE_satchmo_checkout-step2'),
     (r'^confirm/$', 'giftcertificate.views.confirm_info', {}, 'GIFTCERTIFICATE_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {}, 'GIFTCERTIFICATE_satchmo_checkout-success'),
     (r'^balance/$', 'giftcertificate.views.check_balance', {}, 'satchmo_giftcertificate_balance'),
)
