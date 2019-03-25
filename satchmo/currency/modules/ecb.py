import datetime

from currency_converter import CurrencyConverter
from currency_converter.currency_converter import Bounds

from satchmo.currency.models import Currency, ExchangeRate

import logging

logger = logging.getLogger(__name__)


class EcbExchangeRateClient(object):
    """Get the exchange rates from the European Central Bank"""

    API_URL = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip"

    def update_exchange_rates(self):
        primary_currency = Currency.objects.get_primary()
        accepted_currencies = Currency.objects.accepted()
        converter = CurrencyConverter(currency_file=self.API_URL)
        exchange_rates = []
        today = datetime.date.today()

        # As EUR is the default currency for ECB, it doesn't get
        # populated in the data
        converter.currencies.add("EUR")
        converter.bounds["EUR"] = Bounds(today, today)
        converter._rates["EUR"][today] = 1.000

        # As EUR is the default currency for ECB, we have to convert
        # to the primary currency
        if primary_currency.iso_4217_code == "EUR":
            euro_exchange_rate = 1
        else:
            try:
                euro_exchange_rate = converter.convert(
                    1.0, primary_currency.iso_4217_code
                )
            except ValueError:
                return exchange_rates

        for currency in accepted_currencies:
            if currency.iso_4217_code == "EUR":
                rate = euro_exchange_rate
            else:
                try:
                    rate = (
                        1
                        / converter.convert(1, currency.iso_4217_code)
                        * euro_exchange_rate
                    )
                except ValueError:
                    continue
            if (
                ExchangeRate.objects.filter(currency=currency, date=today).exists()
                is False
            ):
                exchange_rate = ExchangeRate.objects.create(
                    currency=currency, date=today, rate=rate
                )
                exchange_rates.append(exchange_rate)

        return exchange_rates
