from django.conf.urls.defaults import *

urlpatterns = patterns('satchmo.product.brand.views',
    url(r'^$', 'brand_list', {}, name='satchmo_brand_list'),
    url(r'^(?P<brandname>[a-z0-9-]+)/(?P<catname>[a-z0-9-]+)/$', 'brand_category_page', {}, name='satchmo_brand_category_view'),
    url(r'^(?P<brandname>[a-z0-9-]+)/$', 'brand_page', {}, name='satchmo_brand_view'),
)
