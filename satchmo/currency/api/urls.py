from django.urls import path

from .views import (
    CurrencyListAPIView,
    CurrencySessionAPIView,
)

urlpatterns = [
    path('', CurrencyListAPIView.as_view()),
    path('session/', CurrencySessionAPIView.as_view()),
]
