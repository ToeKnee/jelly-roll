import mock

from django.test import (
    RequestFactory,
    TestCase,
    override_settings,
)

from satchmo.contact.factories import ContactFactory, UserFactory
from satchmo.l10n.factories import (
    CAFactory,
    UKFactory,
    USFactory,
)
from satchmo.l10n.utils import country_for_request
from satchmo.shop.factories import ShopConfigFactory


class CountryForRequest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        ShopConfigFactory.create(country=CAFactory())

    def test_no_request(self):
        self.assertEqual(country_for_request(None), "CA")

    def test_country_code_in_session(self):
        country = UKFactory()
        request = self.request_factory.get("/")
        request.user = UserFactory()
        request.session = {
            "shipping_country": country.iso2_code,
        }

        self.assertEqual(country_for_request(request), country.iso2_code)

    def test_from_contact(self):
        contact = ContactFactory()
        address = contact.addressbook_set.all()[0]
        address.country = USFactory()
        address.is_default_shipping = True
        address.save()

        request = self.request_factory.get("/")
        request.user = contact.user
        request.session = {}

        self.assertEqual(country_for_request(request), "US")

    @override_settings(GEOIP=None)
    def test_geoip__not_set_up(self):
        request = self.request_factory.get("/")
        request.session = {}

        self.assertEqual(country_for_request(request), "CA")

    @override_settings(GEOIP_PATH="/tmp")
    @mock.patch("satchmo.l10n.utils.get_real_ip")
    def test_geoip__no_ip(self, mock_get_real_ip):
        mock_get_real_ip.return_value = None

        request = self.request_factory.get("/")
        request.session = {}

        self.assertEqual(country_for_request(request), "CA")

    @override_settings(GEOIP_PATH="/tmp")
    @mock.patch("satchmo.l10n.utils.GeoIP")
    @mock.patch("satchmo.l10n.utils.get_real_ip")
    def test_geoip__no_country(self, mock_get_real_ip, mock_geoip):
        mock_get_real_ip.return_value = "127.0.0.1"

        class MockGeoIP(object):
            def country(self, ip):
                return {'country_name': None, 'country_code': None}
        mock_geoip.return_value = MockGeoIP()

        request = self.request_factory.get("/")
        request.session = {}

        self.assertEqual(country_for_request(request), "CA")

    @override_settings(GEOIP_PATH="/tmp")
    @mock.patch("satchmo.l10n.utils.GeoIP")
    @mock.patch("satchmo.l10n.utils.get_real_ip")
    def test_geoip__country_doesnt_match_active_country(self, mock_get_real_ip, mock_geoip):
        mock_get_real_ip.return_value = "163.44.191.38"
        uk = UKFactory()
        uk.active = False
        uk.save()

        class MockGeoIP(object):
            def country(self, ip):
                return {'country_name': 'United Kingdom', 'country_code': 'GB'}
        mock_geoip.return_value = MockGeoIP()

        request = self.request_factory.get("/")
        request.session = {}

        self.assertEqual(country_for_request(request), "CA")

    @override_settings(GEOIP_PATH="/tmp")
    @mock.patch("satchmo.l10n.utils.GeoIP")
    @mock.patch("satchmo.l10n.utils.get_real_ip")
    def test_geoip__country_matches_active_country(self, mock_get_real_ip, mock_geoip):
        mock_get_real_ip.return_value = "88.97.34.8"
        uk = UKFactory()
        uk.active = True
        uk.save()

        class MockGeoIP(object):
            def country(self, ip):
                return {'country_name': 'United Kingdom', 'country_code': 'GB'}
        mock_geoip.return_value = MockGeoIP()

        request = self.request_factory.get("/")
        request.session = {}

        self.assertEqual(country_for_request(request), "GB")

    def test_fallback_to_default(self):
        request = self.request_factory.get("/")
        request.session = {}

        self.assertEqual(country_for_request(request), "CA")
