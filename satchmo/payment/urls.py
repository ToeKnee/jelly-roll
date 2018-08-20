from django.urls import path
from satchmo.configuration.functions import (
    config_get_group,
    config_get,
    config_value,
)
from satchmo.configuration.values import SettingNotSet
from satchmo.payment.views import (
    contact,
    balance,
    cron,
)

import logging
log = logging.getLogger(__name__)

config = config_get_group('PAYMENT')

urlpatterns = [
    path('', contact.contact_info_view,
         {}, 'satchmo_checkout-step1'),
    path('custom/charge/<int:orderitem_id>/',
         balance.charge_remaining, {}, 'satchmo_charge_remaining'),
    path('custom/charge/', balance.charge_remaining_post,
         {}, 'satchmo_charge_remaining_post'),
    path('balance/<int:order_id>/', balance.balance_remaining_order,
         {}, 'satchmo_balance_remaining_order'),
    path('balance/', balance.balance_remaining,
         {}, 'satchmo_balance_remaining'),
    path('cron/', cron.cron_rebill, {}, 'satchmo_cron_rebill'),
    path('mustlogin/', contact.authentication_required,
         {}, 'satchmo_checkout_auth_required'),
]


# Now add all enabled module payment settings
def make_urlpatterns():
    patterns = []
    for key in config_value('PAYMENT', 'MODULES'):
        try:
            cfg = config_get(key, 'MODULE')
        except SettingNotSet:
            log.warning("Could not find module %s, skipping", key)
            continue
        module_name = cfg.editor_value
        url_module = "%s.urls" % module_name
        namespace = module_name.split(".")[-1]
        patterns.append(
            path(
                config_value(key, 'URL_BASE'),
                [url_module, module_name, namespace]
            )
        )
    return patterns


urlpatterns += make_urlpatterns()
