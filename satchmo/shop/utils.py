from django.contrib.sites.models import SiteManager
from django.http import HttpResponse


class HttpResponseMethodNotAllowed(HttpResponse):
    status_code = 405


def is_multihost_enabled():
    return getattr(SiteManager, 'MULTIHOST', False)
