from ipware.ip import get_real_ip

from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2

from satchmo.contact.models import Contact
from satchmo.shop.models import Config

from .models import Country


def country_for_request(request):
    """ Find the country for the request """
    country_code = None

    if request is not None:
        # Try to look up the country code from the session
        country_code = request.session.get("shipping_country")

        # If not, try looking for a contact
        if country_code is None:
            try:
                contact = Contact.objects.from_request(request)
                country_code = contact.shipping_address.country.iso2_code
            except (AttributeError, IndexError, Contact.DoesNotExist):
                pass

        # If not, try the IP address
        if country_code is None:
            if hasattr(settings, "GEOIP_PATH"):
                ip = get_real_ip(request)
                if ip:
                    geoip = GeoIP2()
                    country = geoip.country(ip)
                    try:
                        # GeoIP returns iso2 codes
                        country = Country.objects.filter().get(
                            active=True,
                            iso2_code=country["country_code"]
                        )
                    except Country.DoesNotExist:
                        pass
                    else:
                        country_code = country.iso2_code

    # If not, fall back to primary country
    if country_code is None:
        config = Config.objects.get_current()
        if config.country:
            try:
                country_code = config.country.iso2_code
            except Country.DoesNotExist:
                pass

    return country_code
