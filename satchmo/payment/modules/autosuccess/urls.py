from django.urls import path
from satchmo.payment.views.checkout import success
from .views import one_step

urlpatterns = [
    path("", one_step, {}, "satchmo_checkout-step2"),
    path("success/", success, {}, "satchmo_checkout-success"),
]
