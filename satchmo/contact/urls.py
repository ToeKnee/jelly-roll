"""
URLConf for Satchmo Contacts.
"""
from django.urls import path
from satchmo.contact.views import (
    view,
    update,
)

urlpatterns = [
    path('', view, {}, name='satchmo_account_info'),
    path('update/', update,
         {}, name='satchmo_profile_update'),
]
