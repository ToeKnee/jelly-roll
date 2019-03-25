from django.urls import path
from satchmo.payment.modules.worldpay.views import pay_ship_info, confirm_info, success

urlpatterns = [
    path("", pay_ship_info, {}, "satchmo_checkout-step2"),
    path("confirm/", confirm_info, {}, "satchmo_checkout-step3"),
    path("success/", success, {}, "satchmo_checkout-success"),
]
