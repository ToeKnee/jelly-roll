"""
URLConf for Satchmo Contacts.
"""

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',

    url(r'^$', 'satchmo.contact.views.view', {}, name='satchmo_account_info'),
    url(r'^update/$', 'satchmo.contact.views.update',
        {}, name='satchmo_profile_update'),
)
