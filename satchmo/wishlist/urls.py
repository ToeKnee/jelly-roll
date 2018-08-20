from django.urls import path
from satchmo.wishlist.views import (
    wishlist_view,
    wishlist_add,
    wishlist_add_ajax,
    wishlist_remove,
    wishlist_remove_ajax,
    wishlist_move_to_cart,
)

urlpatterns = [
    path('', wishlist_view, {}, 'satchmo_wishlist_view'),
    path('add/', wishlist_add, {}, 'satchmo_wishlist_add'),
    path('add/ajax/', wishlist_add_ajax, {}, 'satchmo_wishlist_add_ajax'),
    path('remove/', wishlist_remove, {}, 'satchmo_wishlist_remove'),
    path('remove/ajax/', wishlist_remove_ajax, {}, 'satchmo_wishlist_remove_ajax'),
    path('add_cart/', wishlist_move_to_cart, {}, 'satchmo_wishlist_move_to_cart'),
]
