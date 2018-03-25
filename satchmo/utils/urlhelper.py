from django.conf import settings
from django.contrib.sites.models import Site


def external_url(url):
    if settings.SESSION_COOKIE_SECURE and settings.CSRF_COOKIE_SECURE:
        protocol = "https://"
    else:
        protocol = "http://"

    site = Site.objects.get_current()
    full_url = "{protocol}{domain}{url}".format(
        protocol=protocol,
        domain=site.domain,
        url=url,
    )
    return full_url
