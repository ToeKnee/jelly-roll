import datetime
import requests

from satchmo.currency.models import Currency, ExchangeRate

import logging
logger = logging.getLogger(__name__)


class FixerEchangeRateClient(object):
    """Get the exchange rates from http://fixer.io"""

    API_URL = "https://api.fixer.io/{date}?base={primary}&symbols={accepted}"

    def update_exchange_rates(self):
        primary_currency = Currency.objects.get_primary()
        accepted_currencies = Currency.objects.accepted()
        exchange_rates = []

        url = self.API_URL.format(
            date=datetime.date.today().isoformat(),
            primary=primary_currency.iso_4217_code,
            accepted=",".join((
                currency.iso_4217_code
                for currency in accepted_currencies
            ))
        )

        try:
            request = requests.get(url)
        except requests.exceptions.RequestException as e:
            logging.exception(e)
            return exchange_rates

        try:
            data = request.json()
        except ValueError as e:
            logging.exception(e)
            return exchange_rates

        exchange_rates = []
        for iso_4217_code, rate in data.get("rates", {}).items():
            try:
                currency = accepted_currencies.get(iso_4217_code=iso_4217_code)
            except Currency.DoesNotExist:
                continue

            if ExchangeRate.objects.filter(
                currency=currency,
                date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
            ).exists() is False:
                exchange_rate = ExchangeRate.objects.create(
                    currency=currency,
                    date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
                    rate=rate
                )
                exchange_rates.append(exchange_rate)

        return exchange_rates
