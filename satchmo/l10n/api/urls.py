
from django.conf.urls import patterns, url

from .views import (
    CountryListAPIView,
    CountrySessionAPIView,
)

urlpatterns = patterns(
    '',

    url(r'^$', CountryListAPIView.as_view()),
    url(r'^session/$', CountrySessionAPIView.as_view()),
)
