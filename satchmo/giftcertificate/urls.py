from django.urls import path
from satchmo.giftcerticiate.views import (
    pay_ship_info,
    confirm_info,
    check_balance,
)
from sathcmo.payment.views import success

urlpatterns = [
    path('', pay_ship_info, {}, 'GIFTCERTIFICATE_satchmo_checkout-step2'),
    path('confirm/', confirm_info, {}, 'GIFTCERTIFICATE_satchmo_checkout-step3'),
    path('success/', success, {}, 'GIFTCERTIFICATE_satchmo_checkout-success'),
    path('balance/', check_balance, {}, 'satchmo_giftcertificate_balance'),
]
