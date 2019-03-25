from django.urls import path
from satchmo.feeds.views import product_feed, admin_product_feed

urlpatterns = [
    path("atom/", product_feed, {}, "satchmo_atom_feed"),
    path("atom/<slug:category>/", product_feed, {}, "satchmo_atom_category_feed"),
    path(
        "products.csv",
        admin_product_feed,
        {"template": "feeds/product_feed.csv"},
        "satchmo_product_feed",
    ),
]
