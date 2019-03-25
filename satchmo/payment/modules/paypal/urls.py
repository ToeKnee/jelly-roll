from django.urls import path


from satchmo.payment.modules.paypal.views import (
    pay_ship_info,
    confirm_info,
    create_payment,
    execute_payment,
    success,
    webhook,
)

urlpatterns = [
    path("", pay_ship_info, {}, "satchmo_checkout-step2"),
    path("confirm/", confirm_info, {}, "satchmo_checkout-step3"),
    path("create-payment/", create_payment, {}, "satchmo_checkout-create-payment"),
    path("execute-payment/", execute_payment, {}, "satchmo_checkout-execute-payment"),
    path("success/", success, name="satchmo_checkout-success"),
    path("webhook/", webhook, name="satchmo_checkout-webhook"),
]
