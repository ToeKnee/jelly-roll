from django.conf.urls import patterns, url

urlpatterns = patterns(
    'satchmo.fulfilment.modules.six.views',

    url(r'^(?P<order_id>[0-9]+)/(?P<verification_hash>[a-f0-9]+)/$', 'despatch', name='six_despatch'),
    url(r'^(?P<order_id>[0-9]+-[a-z])/(?P<verification_hash>[a-f0-9]+)/$', 'despatch', name='six_despatch_replacement'),

)
