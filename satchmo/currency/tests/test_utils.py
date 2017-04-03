from decimal import Decimal

from django.test import TestCase, RequestFactory
from django.utils.encoding import force_str

from satchmo.configuration.models import Setting
from satchmo.currency.factories import (
    EURCurrencyFactory,
    ExchangeRateFactory,
    GBPCurrencyFactory,
)
from satchmo.currency.models import Currency
from satchmo.currency.utils import (
    convert_to_currency,
    currency_for_request,
    money_format,
)


class MoneyFormatTest(TestCase):
    def test_currency(self):
        EURCurrencyFactory()
        value = Decimal("1.00")
        currency_code = "EUR"

        self.assertEqual(money_format(value, currency_code), u"\u20ac1.00 (EUR)")

    def test_currency__does_not_exist(self):
        value = Decimal("1.00")
        currency_code = "BTC"

        self.assertEqual(force_str(money_format(value, currency_code)), "BTC is not accepted")


class ConvertToCurrencyTest(TestCase):
    def setUp(self):
        EURCurrencyFactory(primary=True)
        Currency.objects.update(accepted=True)

    def test_no_value(self):
        currency_code = "EUR"
        test_value = convert_to_currency(None, currency_code)
        self.assertEqual(test_value, Decimal("0.00"))

    def test_currency_is_primary(self):
        value = Decimal("1.00")
        currency_code = "EUR"
        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, value)

    def test_given_currency_doesnt_exist(self):
        value = Decimal("1.00")
        currency_code = "BTC"

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, value)

    def test_exchange_rate_doesnt_exist(self):
        """If the exchange rate doesn't exist, the value shouldn't change
        """
        value = Decimal("1.00")
        currency_code = "GBP"
        Setting.objects.create(
            group='CURRENCY',
            key='BUFFER',
            value=Decimal("0.00"),
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, value)

    def test_exchange_rate_exists(self):
        """If the exchange rate doesn't exist, the value shouldn't change
        """
        value = Decimal("1.00")
        currency_code = "GBP"
        currency = GBPCurrencyFactory()
        ExchangeRateFactory(
            rate=Decimal("0.75"),
            currency=currency
        )
        Setting.objects.create(
            group='CURRENCY',
            key='BUFFER',
            value=Decimal("0.00"),
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("0.75"))

    def test_buffer_is_added(self):
        value = Decimal("1.00")
        currency_code = "GBP"

        Setting.objects.create(
            group='CURRENCY',
            key='BUFFER',
            value=Decimal("0.10"),
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("1.10"))

    def test_round_up_is_honoured__whole_number(self):
        value = Decimal("0.50")
        currency_code = "GBP"
        currency = GBPCurrencyFactory()
        ExchangeRateFactory(
            rate=Decimal("1.11"),
            currency=currency
        )
        Setting.objects.create(
            group='CURRENCY',
            key='ROUND_UP',
            value=True,
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("1.00"))

    def test_round_up_is_honoured__half_number(self):
        value = Decimal("0.33")
        currency_code = "GBP"
        currency = GBPCurrencyFactory()
        ExchangeRateFactory(
            rate=Decimal("1.11"),
            currency=currency
        )
        Setting.objects.create(
            group='CURRENCY',
            key='ROUND_UP',
            value=True,
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("0.50"))

    def test_round_up_is_off(self):
        value = Decimal("0.33")
        currency_code = "GBP"
        currency = GBPCurrencyFactory()
        ExchangeRateFactory(
            rate=Decimal("1.11"),
            currency=currency
        )
        Setting.objects.create(
            group='CURRENCY',
            key='ROUND_UP',
            value=False,
        )
        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("0.3663"))

    def test_psychological_pricing__whole_currency(self):
        value = Decimal("1.00")

        currency_code = "GBP"
        currency = GBPCurrencyFactory()
        ExchangeRateFactory(
            rate=Decimal("2.00"),
            currency=currency
        )

        Setting.objects.create(
            group='CURRENCY',
            key='PSYCHOLOGICAL_PRICING',
            value=True,
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("1.99"))

    def test_psychological_pricing__not_whole_currency(self):
        value = Decimal("0.75")
        currency_code = "GBP"
        currency = GBPCurrencyFactory()
        ExchangeRateFactory(
            rate=Decimal("2.00"),
            currency=currency
        )
        Setting.objects.create(
            group='CURRENCY',
            key='PSYCHOLOGICAL_PRICING',
            value=True,
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("1.50"))

    def test_psychological_pricing__default_currency(self):
        value = Decimal("1.00")
        currency_code = "EUR"

        Setting.objects.create(
            group='CURRENCY',
            key='PSYCHOLOGICAL_PRICING',
            value=True,
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("0.99"))

    def test_psychological_pricing_is_off(self):
        value = Decimal("1.00")
        currency_code = "EUR"

        Setting.objects.create(
            group='CURRENCY',
            key='PSYCHOLOGICAL_PRICING',
            value=False,
        )

        test_value = convert_to_currency(value, currency_code)
        self.assertEqual(test_value, Decimal("1.00"))


class CurrencyForRequest(TestCase):
    def setUp(self):
        EURCurrencyFactory(primary=True)
        self.request_factory = RequestFactory()

    def test_no_request(self):
        self.assertEqual(currency_for_request(None), "EUR")

    def test_currency_code_in_session(self):
        GBPCurrencyFactory()
        request = self.request_factory.get("/")
        request.session = {
            "currency_code": "GBP",
        }

        self.assertEqual(currency_for_request(request), "GBP")

    def test_fallback_to_primary(self):
        request = self.request_factory.get("/")
        request.session = {}

        self.assertEqual(currency_for_request(request), "EUR")
