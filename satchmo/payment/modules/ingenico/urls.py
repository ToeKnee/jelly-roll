from django.conf.urls import url
from satchmo.configuration import config_get_group

config = config_get_group('PAYMENT_INGENICO')

urlpatterns = [
    url(r'^$', 'satchmo.payment.modules.ingenico.views.pay_ship_info', name='INGENICO_satchmo_checkout-step2'),
    url(r'^confirm/$', 'satchmo.payment.modules.ingenico.views.confirm_info', name='INGENICO_satchmo_checkout-step3'),
    url(r'^accepted/$', 'satchmo.payment.modules.ingenico.views.accepted', name='INGENICO_satchmo_checkout-accepted'),
    url(r'^declined/$', 'satchmo.payment.modules.ingenico.views.declined', name='INGENICO_satchmo_checkout-declined'),
    url(r'^success/$', 'satchmo.payment.modules.ingenico.views.process', name='INGENICO_satchmo_checkout-success'),
    url(r'^failure/$', 'satchmo.payment.modules.ingenico.views.process', name='INGENICO_satchmo_checkout-failure'),
]
