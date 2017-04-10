from __future__ import unicode_literals

import hashlib

from django.test import TestCase

from satchmo.currency.api.serializers import CurrencySerializer
from satchmo.currency.factories import CurrencyFactory, ExchangeRateFactory


class CurrencySerializerTest(TestCase):
    def test_read_fields(self):
        currency = CurrencyFactory()
        serializer = CurrencySerializer(currency)

        self.assertEqual(serializer.data["iso_4217_code"], currency.iso_4217_code)
        self.assertEqual(serializer.data["name"], currency.name)
        self.assertEqual(serializer.data["symbol"], currency.symbol)
        self.assertTrue(serializer.data["primary"])
        self.assertTrue(serializer.data["accepted"])
        self.assertIsNone(serializer.data["latest_exchange_rate"])

    def test_get_latest_exchange_rate(self):
        currency = CurrencyFactory()
        exchange_rate = ExchangeRateFactory(currency=currency)
        serializer = CurrencySerializer(currency)

        self.assertEqual(
            serializer.get_latest_exchange_rate(currency),
            exchange_rate.rate,
        )

    def test_get_latest_exchange_rate__no_exchange_rate(self):
        currency = CurrencyFactory()
        serializer = CurrencySerializer(currency)

        self.assertIsNone(serializer.get_latest_exchange_rate(currency))
