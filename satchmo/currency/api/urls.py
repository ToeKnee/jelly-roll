from django.conf.urls import patterns, url

from .views import CurrencyListAPIView

urlpatterns = patterns(
    '',

    url(r'^$', CurrencyListAPIView.as_view()),
)
