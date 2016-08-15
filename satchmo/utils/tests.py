from decimal import Decimal

from django.test import TestCase

from satchmo.utils import trunc_decimal


class TruncDecimalTest(TestCase):
    def test_under_half_rounds_down(self):
        self.assertEqual(trunc_decimal("0.004", 2), Decimal("0.00"))

    def test_equal_to_half_rounds_up(self):
        self.assertEqual(trunc_decimal("0.005", 2), Decimal("0.01"))

    def test_over_half_rounds_up(self):
        self.assertEqual(trunc_decimal("0.009", 2), Decimal("0.01"))
