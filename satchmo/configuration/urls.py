from django.conf.urls import *

urlpatterns = patterns('satchmo.configuration.views',
    (r'^$', 'site_settings', {}, 'satchmo_site_settings'),
    (r'^(?P<group>[^/]+)/$', 'group_settings'),
)
