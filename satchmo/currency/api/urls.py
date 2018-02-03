from django.conf.urls import patterns, url

from .views import (
    CurrencyListAPIView,
    CurrencySessionAPIView,
)

urlpatterns = patterns(
    '',

    url(r'^$', CurrencyListAPIView.as_view()),
    url(r'^session/$', CurrencySessionAPIView.as_view()),
)
