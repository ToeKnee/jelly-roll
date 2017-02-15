import datetime
import mock
import requests

from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from .models import Currency, ExchangeRate
from .modules.fixer import FixerEchangeRateClient


class CurrencyTest(TestCase):
    def test_uncode(self):
        currency = Currency(iso_4217_code="GBP")

        self.assertEqual(u"{currency}".format(currency=currency), "GBP")

    def test_save__set_primary__sets_accepted(self):
        currency = Currency.objects.get(iso_4217_code="GBP")
        currency.primary = True
        currency.save()

        currency = Currency.objects.get(iso_4217_code="GBP")
        self.assertTrue(currency.primary)
        self.assertTrue(currency.accepted)

    def test_save__set_primary__turns_off_other_primary(self):
        currency = Currency.objects.get(iso_4217_code="GBP")
        currency.primary = True
        currency.save()

        # Make Euro primary currency
        currency = Currency.objects.get(iso_4217_code="EUR")
        currency.primary = True
        currency.save()

        currency = Currency.objects.get(iso_4217_code="GBP")
        self.assertFalse(currency.primary)


class FixerExchangeRateClientTest(TestCase):
    def setUp(self):
        self.client = FixerEchangeRateClient()

        # Set primary currency + accepted currencies
        currency = Currency.objects.get(iso_4217_code="GBP")
        currency.primary = True
        currency.save()
        Currency.objects.update(accepted=True)

    def test_updates_ok(self):
        data = {
            'date': '2017-02-14',
            'base': 'GBP',
            'rates': {'USD': 1.2483, 'EUR': 1.1751}
        }

        with mock.patch("satchmo.currency.modules.fixer.requests") as mock_requests:
            class mock_request(object):
                def json(self):
                    return data
            mock_requests.get.return_value = mock_request()

            exchange_rates = self.client.update_exchange_rates()
            self.assertEqual(len(exchange_rates), ExchangeRate.objects.count())
            exchange_rates.sort(key=lambda k: k.currency.iso_4217_code)
            self.assertEqual(exchange_rates[0].currency.iso_4217_code, "EUR")
            self.assertEqual(exchange_rates[0].rate, 1.1751)
            year, month, day = data["date"].split("-")
            self.assertEqual(exchange_rates[0].date, datetime.date(int(year), int(month), int(day)))

            self.assertEqual(exchange_rates[1].currency.iso_4217_code, "USD")
            self.assertEqual(exchange_rates[1].rate, 1.2483)
            self.assertEqual(exchange_rates[1].date, datetime.date(int(year), int(month), int(day)))

    def test_updates_twice_on_one_day(self):
        #  Should not create another ExchangeRate
        ExchangeRate.objects.create(
            currency=Currency.objects.get(iso_4217_code="EUR"),
            date=datetime.date.today(),
            rate="1.5001"
        )
        ExchangeRate.objects.create(
            currency=Currency.objects.get(iso_4217_code="USD"),
            date=datetime.date.today(),
            rate="1.0002"
        )

        data = {
            'date': datetime.date.today().isoformat(),
            'base': 'GBP',
            'rates': {'USD': 1.2483, 'EUR': 1.1751}
        }

        with mock.patch("satchmo.currency.modules.fixer.requests") as mock_requests:
            class mock_request(object):
                def json(self):
                    return data
            mock_requests.get.return_value = mock_request()

            self.client.update_exchange_rates()
            self.assertEqual(ExchangeRate.objects.count(), 2)

    def test_api_is_down(self):
        # No errors, but nothing created either

        def ConnectionError():
            raise requests.exceptions.ConnectionError("Service Unavailable")

        with mock.patch("satchmo.currency.modules.fixer.requests", side_effect=ConnectionError):
            self.client.update_exchange_rates()
            self.assertEqual(ExchangeRate.objects.count(), 0)

    def test_api_contents_malformed(self):
        data = {"key": "Not what we are expecting"}
        with mock.patch("satchmo.currency.modules.fixer.requests") as mock_requests:
            class mock_request(object):
                def json(self):
                    return data
            mock_requests.get.return_value = mock_request()

            self.client.update_exchange_rates()
            self.assertEqual(ExchangeRate.objects.count(), 0)

    def test_api_contents_malformed__not_json_decodable(self):
        with mock.patch("satchmo.currency.modules.fixer.requests") as mock_requests:
            class mock_request(object):
                def json(self):
                    raise ValueError("Not JSON")
            mock_requests.get.return_value = mock_request()

            self.client.update_exchange_rates()
            self.assertEqual(ExchangeRate.objects.count(), 0)

    def test_unexpeted_exchange_rate(self):
        data = {
            'date': '2017-02-14',
            'base': 'GBP',
            'rates': {'USD': 1.2483, 'EUR': 1.1751, 'JPY': 412.1111}
        }

        with mock.patch("satchmo.currency.modules.fixer.requests") as mock_requests:
            class mock_request(object):
                def json(self):
                    return data
            mock_requests.get.return_value = mock_request()

            exchange_rates = self.client.update_exchange_rates()
            self.assertEqual(len(exchange_rates), ExchangeRate.objects.count())
            exchange_rates.sort(key=lambda k: k.currency.iso_4217_code)
            self.assertEqual(exchange_rates[0].currency.iso_4217_code, "EUR")
            self.assertEqual(exchange_rates[0].rate, 1.1751)
            year, month, day = data["date"].split("-")
            self.assertEqual(exchange_rates[0].date, datetime.date(int(year), int(month), int(day)))

            self.assertEqual(exchange_rates[1].currency.iso_4217_code, "USD")
            self.assertEqual(exchange_rates[1].rate, 1.2483)
            self.assertEqual(exchange_rates[1].date, datetime.date(int(year), int(month), int(day)))
