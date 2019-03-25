from django.contrib.sites.models import Site
from django.urls import reverse, NoReverseMatch
from satchmo.utils import url_join

import logging

log = logging.getLogger(__name__)


def lookup_template(settings, template):
    """Return a template name, which may have been overridden in the settings."""

    if "TEMPLATE_OVERRIDES" in settings:
        val = settings["TEMPLATE_OVERRIDES"]
        template = val.get(template, template)

    return template


def lookup_url(settings, name, include_server=False, ssl=False):
    """Look up a named URL for the payment module.

    Tries a specific-to-general lookup fallback, returning
    the first positive hit.

    First look for a dictionary named "URL_OVERRIDES" on the settings object.
    Next try prepending the module name to the name
    Last just look up the name
    """
    if name.startswith("http"):
        return name
    url = None

    try:
        namespace = settings.KEY.value.lower()
        possible = "{namespace}:{url_name}".format(namespace=namespace, url_name=name)
        url = reverse(possible)
    except NoReverseMatch:
        log.debug("No url found for %s", possible)

    if not url:
        try:
            url = reverse(name)
        except NoReverseMatch as e:
            log.error("Could not find any url for %s", name)
            log.exception(e)
            raise

    if include_server:
        if ssl:
            method = "https://"
        else:
            method = "http://"
        site = Site.objects.get_current()
        url = url_join(method, site.domain, url)

    return url
