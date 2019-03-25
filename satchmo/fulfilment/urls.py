from django.urls import include, path

from satchmo.fulfilment.modules.six import urls as six_urls

urlpatterns = [path("six/", include(six_urls))]
