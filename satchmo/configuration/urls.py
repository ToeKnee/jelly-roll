from django.urls import path
from satchmo.configuration.views import site_settings, group_settings

urlpatterns = [
    path("", site_settings, {}, "satchmo_site_settings"),
    path("<path:group>/", group_settings),
]
