from django.urls import path


from satchmo.payment.modules.paypal.views import (
    pay_ship_info,
    confirm_info,
    success,
    ipn
)

urlpatterns = [
    path(r'', pay_ship_info, {}, 'satchmo_checkout-step2'),
    path('confirm/', confirm_info, {}, 'satchmo_checkout-step3'),
    path('success/', success, name='satchmo_checkout-success'),
    path('ipn/', ipn, {}, 'satchmo_checkout-ipn'),
]
