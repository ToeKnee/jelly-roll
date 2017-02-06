from django.test import TestCase

from .models import Currency


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
