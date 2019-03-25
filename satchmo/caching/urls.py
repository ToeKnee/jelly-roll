"""
URLConf for Caching app
"""

from django.urls import path
from satchmo.caching.views import stats_page, view_page, delete_page

urlpatterns = [
    path("", stats_page, {}, "caching_stats"),
    path("view/", view_page, {}, "caching_view"),
    path("delete/", delete_page, {}, "caching_delete"),
]
