from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'satchmo.product.brand.views',

    url(r'^$', 'brand_list', {}, name='satchmo_brand_list'),
    url(r'^(?P<brandname>[a-z0-9-]+)/$', 'brand_page', {}, name='satchmo_brand_view'),
)
