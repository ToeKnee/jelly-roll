from django.test import TestCase

from satchmo.currency.factories import GBPCurrencyFactory, EURCurrencyFactory
from satchmo.currency.models import Currency


class CurrencyTest(TestCase):
    def test_unicode(self):
        currency = GBPCurrencyFactory.build()

        self.assertEqual("{currency}".format(currency=currency), "GBP")

    def test_save__set_primary__sets_accepted(self):
        currency = GBPCurrencyFactory(primary=False, accepted=False)
        currency.primary = True
        currency.save()

        currency = Currency.objects.get(iso_4217_code="GBP")
        self.assertTrue(currency.primary)
        self.assertTrue(currency.accepted)

    def test_save__set_primary__turns_off_other_primary(self):
        currency = GBPCurrencyFactory(primary=False, accepted=False)
        currency.primary = True
        currency.save()

        # Make Euro primary currency
        currency = EURCurrencyFactory(primary=False, accepted=False)
        currency.primary = True
        currency.save()

        currency = Currency.objects.get(iso_4217_code="GBP")
        self.assertFalse(currency.primary)
