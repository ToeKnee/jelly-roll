from django.urls import include, path
from satchmo.product.urls import urlpatterns as productpatterns
from satchmo.shop.satchmo_settings import get_satchmo_setting

from satchmo.shop.views import (
    home,
    smart,
    cart,
    orders,
    search,
    download,
)


urlpatterns = get_satchmo_setting('SHOP_URLS')

urlpatterns += [
    path('', home.home, {}, 'satchmo_shop_home'),
    path('add/', smart.smart_add, {}, 'satchmo_smart_add'),
    path('cart/', cart.display, {}, 'satchmo_cart'),
    path('cart/accept/', cart.agree_terms, {}, 'satchmo_cart_accept_terms'),
    path('cart/add/', cart.add, {}, 'satchmo_cart_add'),
    path('cart/add/ajax/', cart.add_ajax, {}, 'satchmo_cart_add_ajax'),
    path('cart/qty/', cart.set_quantity, {}, 'satchmo_cart_set_qty'),
    path('cart/qty/ajax/', cart.set_quantity_ajax, {}, 'satchmo_cart_set_qty_ajax'),
    path('cart/remove/', cart.remove, {}, 'satchmo_cart_remove'),
    path('cart/remove/ajax/', cart.remove_ajax, {}, 'satchmo_cart_remove_ajax'),
    path('checkout/', include('satchmo.payment.urls')),
    path('history/', orders.order_history, {}, 'satchmo_order_history'),
    path('tracking/<int:order_id>/',
         orders.order_tracking, {}, 'satchmo_order_tracking'),
    path('search/', search.search_view, {}, 'satchmo_search'),

    # Used for downloadable products.
    path('download/process/<slug:download_key>/',
         download.process, {}, 'satchmo_download_process'),
    path('download/send/<slug:download_key>/',
         download.send_file, {}, 'satchmo_download_send'),

    path('contact/', include('satchmo.contact.urls')),
    path('wishlist/', include('satchmo.wishlist.urls')),
    path('fulfilment/', include('satchmo.fulfilment.urls')),

    # API
    path('api/currency/', include('satchmo.currency.api.urls')),
    path('api/l10n/', include('satchmo.l10n.api.urls')),
    path('i18n/', include('satchmo.l10n.urls'))
]

# Here we add product patterns directly into the root url
urlpatterns += productpatterns
