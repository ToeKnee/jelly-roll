"""
This code is heavily based on samples found here -
http://www.b-list.org/weblog/2006/06/14/django-tips-template-context-processors

It is used to add some common variables to all the templates
"""
from django.conf import settings as site_settings
from satchmo.product.models import Category
from satchmo.shop.satchmo_settings import get_satchmo_setting
from satchmo.shop.models import Config, Cart
from satchmo.utils import current_media_url, request_is_secure
import logging

log = logging.getLogger(__name__)


def settings(request):
    shop_config = Config.objects.get_current()
    cart = Cart.objects.from_request(request)

    all_categories = Category.objects.by_site()
    return {
        'shop_base': get_satchmo_setting('SHOP_BASE'),
        'shop': shop_config,
        'shop_name': shop_config.store_name,
        'shop_domain': shop_config.site.domain,
        'shop_description': shop_config.store_description,
        'media_url': current_media_url(request),
        'cart_count': cart.numItems,
        'cart': cart,
        'categories': all_categories,
        'is_secure': request_is_secure(request),
        'request': request,
        'login_url': site_settings.LOGIN_URL,
        'logout_url': site_settings.LOGOUT_URL,
    }
