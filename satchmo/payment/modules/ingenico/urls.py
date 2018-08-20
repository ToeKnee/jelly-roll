from django.urls import path

from satchmo.payment.modules.ingenico.views import (
    pay_ship_info,
    confirm_info,
    accepted,
    declined,
    process,
)

urlpatterns = [
    path('', pay_ship_info, name='satchmo_checkout-step2'),
    path('confirm/', confirm_info, name='satchmo_checkout-step3'),
    path('accepted/', accepted, name='satchmo_checkout-accepted'),
    path('declined/', declined, name='satchmo_checkout-declined'),
    path('success/', process, name='satchmo_checkout-success'),
    path('failure/', process, name='satchmo_checkout-failure'),
]
