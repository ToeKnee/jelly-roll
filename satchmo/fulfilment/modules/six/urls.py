from django.urls import path, re_path
from satchmo.fulfilment.modules.six.views import despatch

urlpatterns = [
    path('<int:order_id>/<slug:verification_hash>/',
         despatch, name='six_despatch'),
    re_path('(?P<order_id>[0-9]+)-([a-z])/(?P<verification_hash>[a-f0-9]+)/',
            despatch, name='six_despatch_replacement'),
]
