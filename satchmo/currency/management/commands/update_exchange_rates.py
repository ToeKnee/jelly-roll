from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand

from satchmo.currency.modules.fixer import FixerExchangeRateClient
from satchmo.currency.modules.ecb import EcbExchangeRateClient


class Command(BaseCommand):
    help = 'Updates exchange rates'

    def handle(self, *args, **options):
        module = getattr(settings, 'EXCHANGE_RATE_MODULE', 'ecb')
        if module == 'fixer':
            client = FixerExchangeRateClient()
        else:
            client = EcbExchangeRateClient()

        exchange_rates = client.update_exchange_rates()
        for exchange_rate in exchange_rates:
            self.stdout.write('Successfully updated "%s"' % exchange_rate)

        subject = "Updated {num} currencies".format(num=len(exchange_rates))
        message = """Howdy,

Here are the latest exchange rates:

{rates}

See you again soon!

--
JellyRoll
        """.format(
            rates="\n".join("* {rate}".format(rate=rate) for rate in exchange_rates)
        )
        mail_admins(subject, message)
