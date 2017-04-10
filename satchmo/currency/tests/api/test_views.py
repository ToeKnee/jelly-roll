from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from satchmo.contact.factories import UserFactory
from satchmo.currency.api.views import CurrencyListAPIView
from satchmo.currency.factories import (
    EURCurrencyFactory,
    GBPCurrencyFactory,
)


class CurrencyListTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_primary_currency_only(self):
        currency = EURCurrencyFactory(primary=True)
        request = self.factory.get('/api/currency/')

        response = CurrencyListAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [
            {
                "iso_4217_code": currency.iso_4217_code,
                "name": currency.name,
                "symbol": currency.symbol,
                "primary": currency.primary,
                "accepted": currency.accepted,
                "latest_exchange_rate": None,
            }
        ])

    def test_accepted_currencies(self):
        currency = EURCurrencyFactory(primary=True)
        accepted_currency = GBPCurrencyFactory()
        accepted_currency.accepted = True
        accepted_currency.save()
        request = self.factory.get('/api/currency/')

        response = CurrencyListAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        test_data = [
            {
                "iso_4217_code": currency.iso_4217_code,
                "name": currency.name,
                "symbol": currency.symbol,
                "primary": currency.primary,
                "accepted": currency.accepted,
                "latest_exchange_rate": None,
            },
            {
                "iso_4217_code": accepted_currency.iso_4217_code,
                "name": accepted_currency.name,
                "symbol": accepted_currency.symbol,
                "primary": accepted_currency.primary,
                "accepted": accepted_currency.accepted,
                "latest_exchange_rate": None,
            }
        ]
        self.assertEqual(response.data, test_data)

    def test_anonymous__cant_post_currency(self):
        currency = EURCurrencyFactory.build()  # Build, don't create
        data = {
            "iso_4217_code": currency.iso_4217_code,
            "name": currency.name,
            "symbol": currency.symbol,
            "primary": currency.primary,
            "accepted": currency.accepted,
            "latest_exchange_rate": None,
        }
        request = self.factory.post('/api/currency/', data)

        response = CurrencyListAPIView.as_view()(request, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data,
            {'detail': 'Authentication credentials were not provided.'}
        )

    def test_authenticated__cant_post_currency(self):
        user = UserFactory()
        currency = EURCurrencyFactory.build()  # Build, don't create
        data = {
            "iso_4217_code": currency.iso_4217_code,
            "name": currency.name,
            "symbol": currency.symbol,
            "primary": currency.primary,
            "accepted": currency.accepted,
            "latest_exchange_rate": None,
        }
        request = self.factory.post('/api/currency/', data)
        force_authenticate(request, user)

        response = CurrencyListAPIView.as_view()(request, data)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            response.data,
            {'detail': 'Method "POST" not allowed.'}
        )
