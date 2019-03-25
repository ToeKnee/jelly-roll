from django.urls import path

from .views import CountryListAPIView, CountrySessionAPIView

urlpatterns = [
    path("", CountryListAPIView.as_view()),
    path("session/", CountrySessionAPIView.as_view()),
]
