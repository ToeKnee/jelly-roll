from satchmo.shop.signals import satchmo_cart_add_complete
from . import views

satchmo_cart_add_complete.connect(views.cart_add_listener, sender=None)
