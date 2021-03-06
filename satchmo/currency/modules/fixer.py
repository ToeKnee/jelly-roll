import datetime
import requests

from django.conf import settings

from satchmo.currency.models import Currency, ExchangeRate

import logging

logger = logging.getLogger(__name__)


class FixerExchangeRateClient(object):
    """Get the exchange rates from http://fixer.io"""

    API_URL = "https://data.fixer.io/api/latest?base={primary}&symbols={accepted}&access_key={access_key}"

    def update_exchange_rates(self):
        primary_currency = Currency.objects.get_primary()
        accepted_currencies = Currency.objects.accepted()
        exchange_rates = []

        url = self.API_URL.format(
            primary=primary_currency.iso_4217_code,
            accepted=",".join(
                (currency.iso_4217_code for currency in accepted_currencies)
            ),
            access_key=getattr(settings, "FIXERIO_KEY"),
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
        for iso_4217_code, rate in list(data.get("rates", {}).items()):
            try:
                currency = accepted_currencies.get(iso_4217_code=iso_4217_code)
            except Currency.DoesNotExist:
                continue

            if (
                ExchangeRate.objects.filter(
                    currency=currency,
                    date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
                ).exists()
                is False
            ):
                exchange_rate = ExchangeRate.objects.create(
                    currency=currency,
                    date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
                    rate=rate,
                )
                exchange_rates.append(exchange_rate)

        return exchange_rates
