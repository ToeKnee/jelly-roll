"""Base urls used by Satchmo.

Split out from urls.py to allow much easier overriding and integration with larger apps.
"""
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap
from satchmo.shop.satchmo_settings import get_satchmo_setting
from satchmo.shop.views.sitemaps import sitemaps
from satchmo.configuration import urls as configuration_urls
from satchmo.shop import urls as shop_urls
from satchmo.caching import urls as caching_urls
from satchmo.utils.google import product_feed

shop_base = get_satchmo_setting("SHOP_BASE")

if shop_base == "":
    shop_paths = ""
else:
    shop_paths = "" + shop_base[1:] + "/"


urlpatterns = [
    path("settings/", include(configuration_urls)),
    path(shop_paths, include(shop_urls)),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, "satchmo_sitemap_xml"),
    path("cache", include(caching_urls)),
    path("product-feed.xml", product_feed),
]
