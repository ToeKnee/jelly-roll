"""Base urls used by Satchmo.

Split out from urls.py to allow much easier overriding and integration with larger apps.
"""
from django.conf import settings
from django.conf.urls.defaults import *
from satchmo.shop import get_satchmo_setting
from satchmo.shop.views.sitemaps import sitemaps

shop_base = get_satchmo_setting('SHOP_BASE')
if shop_base == '':
    shopregex = '^'
else:
    shopregex = '^' + shop_base[1:] + '/'


urlpatterns = patterns('',
    (r"^settings/", include('satchmo.configuration.urls')),
    (r"^product/configurableproduct/(?P<id>\d+)/getoptions/", 'satchmo.product.views.get_configurable_product_options', {}, 'satchmo_admin_configurableproduct'),
    (shopregex, include('satchmo.shop.urls')),
    (r'sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}, 'satchmo_sitemap_xml'),
    (r'cache/', include('satchmo.caching.urls')),
    (r'product-feed\.xml$', "satchmo.utils.google.product_feed"),
)

