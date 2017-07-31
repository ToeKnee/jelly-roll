from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from satchmo.contact.factories import UserFactory
from satchmo.l10n.api.views import (
    CountryListAPIView,
    CountrySessionAPIView,
)
from satchmo.l10n.factories import (
    UKFactory,
    USFactory,
)
from satchmo.l10n.models import Country


class CountryListTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_active_countries(self):
        Country.objects.all().update(active=False)
        active_country = UKFactory()
        active_country.active = True
        active_country.save()
        request = self.factory.get('/api/country/')

        response = CountryListAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        test_data = [
            {
                "iso2_code": active_country.iso2_code,
                "iso3_code": active_country.iso3_code,
                "name": active_country.name,
                "printable_name": active_country.printable_name,
                "numcode": active_country.numcode,
                "continent": {
                    'id': active_country.continent.id,
                    'code': active_country.continent.code,
                    'name': active_country.continent.name
                },
                "admin_area": active_country.admin_area,
                "eu": active_country.eu,
            }
        ]
        self.assertEqual(response.data, test_data)

    def test_anonymous__cant_post_country(self):
        country = USFactory.build()  # Build, don't create
        data = {
            "iso2_code": country.iso2_code,
            "iso3_code": country.iso3_code,
            "name": country.name,
            "printable_name": country.printable_name,
            "numcode": country.numcode,
            "admin_area": country.admin_area,
            "eu": country.eu,
        }
        request = self.factory.post('/api/country/', data)

        response = CountryListAPIView.as_view()(request, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'}
        )

    def test_authenticated__cant_post_country(self):
        user = UserFactory()
        country = USFactory.build()  # Build, don't create
        data = {
            "iso2_code": country.iso2_code,
            "iso3_code": country.iso3_code,
            "name": country.name,
            "printable_name": country.printable_name,
            "numcode": country.numcode,
            "admin_area": country.admin_area,
            "eu": country.eu,
        }
        request = self.factory.post('/api/country/', data)
        force_authenticate(request, user)

        response = CountryListAPIView.as_view()(request, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data,
            {'detail': 'You do not have permission to perform this action.'}
        )


class CountrySessionTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_get_active_from_session(self):
        country = UKFactory()
        country.active = True
        country.save()
        request = self.factory.get('/api/country/session/')
        request.session = {
            "shipping_country": country.iso2_code,
        }
        response = CountrySessionAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "iso2_code": country.iso2_code,
                "iso3_code": country.iso3_code,
                "name": country.name,
                "printable_name": country.printable_name,
                "numcode": country.numcode,
                "continent": {
                    'id': country.continent.id,
                    'code': country.continent.code,
                    'name': country.continent.name
                },
                "admin_area": country.admin_area,
                "eu": country.eu,
            }
        )

    def test_set_country_in_session(self):
        country = USFactory()
        active_country = UKFactory()
        active_country.active = True
        active_country.save()
        data = {
            "iso2_code": active_country.iso2_code,
        }
        request = self.factory.post('/api/country/session/', data=data)
        request.session = {
            "country_code": country.iso2_code,
        }

        response = CountrySessionAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        test_data = {
            "iso2_code": active_country.iso2_code,
            "iso3_code": active_country.iso3_code,
            "name": active_country.name,
            "printable_name": active_country.printable_name,
            "numcode": active_country.numcode,
            "continent": {
                'id': active_country.continent.id,
                'code': active_country.continent.code,
                'name': active_country.continent.name
            },
            "admin_area": active_country.admin_area,
            "eu": active_country.eu,
        }

        self.assertEqual(response.data, test_data)
