from __future__ import unicode_literals

import hashlib

from django.test import TestCase

from satchmo.currency.api.serializers import CurrencySerializer, CurrencySessionSerializer
from satchmo.currency.factories import EURCurrencyFactory, ExchangeRateFactory


class CurrencySerializerTest(TestCase):
    def test_read_fields(self):
        currency = EURCurrencyFactory()
        serializer = CurrencySerializer(currency)

        self.assertEqual(serializer.data["iso_4217_code"], currency.iso_4217_code)
        self.assertEqual(serializer.data["name"], currency.name)
        self.assertEqual(serializer.data["symbol"], currency.symbol)
        self.assertTrue(serializer.data["primary"])
        self.assertTrue(serializer.data["accepted"])
        self.assertIsNone(serializer.data["latest_exchange_rate"])

    def test_get_latest_exchange_rate(self):
        currency = EURCurrencyFactory()
        exchange_rate = ExchangeRateFactory(currency=currency)
        serializer = CurrencySerializer(currency)

        self.assertEqual(
            serializer.get_latest_exchange_rate(currency),
            exchange_rate.rate,
        )

    def test_get_latest_exchange_rate__no_exchange_rate(self):
        currency = EURCurrencyFactory()
        serializer = CurrencySerializer(currency)

        self.assertIsNone(serializer.get_latest_exchange_rate(currency))


class CurrencySessionSerializerTest(TestCase):
    def test_read_fields(self):
        currency = EURCurrencyFactory()
        serializer = CurrencySessionSerializer(currency)

        self.assertEqual(serializer.data["iso_4217_code"], currency.iso_4217_code)
        self.assertEqual(len(serializer.data.keys()), 1)

    def test_validate__correct(self):
        EURCurrencyFactory()

        data = {"iso_4217_code": "EUR"}
        serializer = CurrencySessionSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_get__currency_doesnt_exist(self):
        data = {"iso_4217_code": "BTC"}
        serializer = CurrencySessionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors,
            {'iso_4217_code': ["BTC is not an accepted currency"]}
        )
