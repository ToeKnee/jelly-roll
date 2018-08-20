import datetime
import mock
import requests

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils.six import StringIO

from satchmo.currency.factories import (
    EURCurrencyFactory,
    GBPCurrencyFactory,
    USDCurrencyFactory,
)
from satchmo.currency.models import Currency, ExchangeRate
from satchmo.currency.modules.fixer import FixerExchangeRateClient


class FixerExchangeRateClientTest(TestCase):
    def setUp(self):
        self.client = FixerExchangeRateClient()

        # Set primary currency + accepted currencies
        EURCurrencyFactory()
        USDCurrencyFactory()
        currency = GBPCurrencyFactory()
        currency.primary = True
        currency.save()
        Currency.objects.update(accepted=True)

    @override_settings(FIXERIO_KEY='test')
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

    @override_settings(FIXERIO_KEY='test')
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

    @override_settings(FIXERIO_KEY='test')
    def test_api_is_down(self):
        # No errors, but nothing created either

        def ConnectionError():
            raise requests.exceptions.ConnectionError("Service Unavailable")

        with mock.patch("satchmo.currency.modules.fixer.requests", side_effect=ConnectionError):
            self.client.update_exchange_rates()
            self.assertEqual(ExchangeRate.objects.count(), 0)

    @override_settings(FIXERIO_KEY='test')
    def test_api_contents_malformed(self):
        data = {"key": "Not what we are expecting"}
        with mock.patch("satchmo.currency.modules.fixer.requests") as mock_requests:
            class mock_request(object):
                def json(self):
                    return data
            mock_requests.get.return_value = mock_request()

            self.client.update_exchange_rates()
            self.assertEqual(ExchangeRate.objects.count(), 0)

    @override_settings(FIXERIO_KEY='test')
    def test_api_contents_malformed__not_json_decodable(self):
        with mock.patch("satchmo.currency.modules.fixer.requests") as mock_requests:
            class mock_request(object):
                def json(self):
                    raise ValueError("Not JSON")
            mock_requests.get.return_value = mock_request()

            self.client.update_exchange_rates()
            self.assertEqual(ExchangeRate.objects.count(), 0)

    @override_settings(FIXERIO_KEY='test')
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


class UpdateExchangeRages(TestCase):
    def setUp(self):
        # Set primary currency + accepted currencies
        EURCurrencyFactory()
        USDCurrencyFactory()
        currency = GBPCurrencyFactory()
        currency.primary = True
        currency.save()
        Currency.objects.update(accepted=True)

    @override_settings(EXCHANGE_RATE_MODULE='fixer')
    @override_settings(FIXERIO_KEY='test')
    def test_sends_emails_when_complete(self):
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

            out = StringIO()
            call_command('update_exchange_rates', stdout=out)

            self.assertIn('Successfully updated "USD 1.2483"', out.getvalue())
            self.assertIn('Successfully updated "EUR 1.1751"', out.getvalue())

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, '[Django] Updated 2 currencies')
            self.assertIn('* USD 1.2483\n', mail.outbox[0].body)
            self.assertIn('* EUR 1.1751\n', mail.outbox[0].body)
