from django.urls import path

from satchmo.product.brand.views import (
    brand_list,
    brand_page,
)


urlpatterns = [
    path('', brand_list, {}, name='satchmo_brand_list'),
    path('<slug:brandname>/',
         brand_page, {}, name='satchmo_brand_view'),
]
