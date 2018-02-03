from datetime import date

from django.test import TestCase

from satchmo.caching import cache_delete
from satchmo.configuration import config_get_group
from satchmo.configuration.models import Setting
from satchmo.payment.modules.ingenico.forms import IngenicoForm
from satchmo.payment.modules.ingenico.utils import shasign
from satchmo.shop.factories import TestOrderFactory

payment_module = config_get_group('PAYMENT_INGENICO')


class IngenicoFormTest(TestCase):
    def tearDown(self):
        cache_delete()

    def test_alias_enabled(self):
        # Enable Aliasing
        Setting.objects.create(
            key='ALIAS',
            group='PAYMENT_INGENICO',
            value=True,
        )

        form = IngenicoForm()

        self.assertIn("ALIAS", form.fields)

    def test_alias_disabled(self):
        # Disable Aliasing
        Setting.objects.create(
            key='ALIAS',
            group='PAYMENT_INGENICO',
            value=False,
        )

        form = IngenicoForm()

        self.assertNotIn("ALIAS", form.fields)
        self.assertNotIn("ALIASUSAGE", form.fields)

    def test_shasign(self):
        order = TestOrderFactory()

        data = {
            "ACCEPTANCE": "trans-1",
            "AMOUNT": str(order.total),
            "BRAND": "Visa",
            "CARDNO": "xxxx xxxx xxxx 4679",
            "CN": order.bill_addressee,
            "CURRENCY": order.currency.iso_4217_code,
            "ED": "02/2019",
            "NCERROR": None,
            "ORDERID": str(order.id),
            "PAYID": "ingenico-1",
            "PM": "CC",
            "STATUS": "1",
            "TRXDATE": date.today().isoformat(),
        }
        form = IngenicoForm(data)

        self.assertIn("SHASIGN", form.fields)
        self.assertEqual(form.data["SHASIGN"], shasign(data))
