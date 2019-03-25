from decimal import Decimal

from django.test import TestCase

from satchmo.utils import trunc_decimal
from satchmo.utils.case_insensitive_dict import CaseInsensitiveReadOnlyDict


class TruncDecimalTest(TestCase):
    def test_under_half_rounds_down(self):
        self.assertEqual(trunc_decimal("0.004", 2), Decimal("0.00"))

    def test_equal_to_half_rounds_up(self):
        self.assertEqual(trunc_decimal("0.005", 2), Decimal("0.01"))

    def test_over_half_rounds_up(self):
        self.assertEqual(trunc_decimal("0.009", 2), Decimal("0.01"))


class CaseInsensitiveReadOnlyDictTest(TestCase):
    def test_contains__correct_case(self):
        d = {"key": "value"}
        id = CaseInsensitiveReadOnlyDict(d)
        self.assertTrue("key" in id)

    def test_contains__incorrect_case(self):
        d = {"kEy": "value"}
        id = CaseInsensitiveReadOnlyDict(d)
        self.assertTrue("KeY" in id)

    def test_len(self):
        d = {"key": "value"}
        id = CaseInsensitiveReadOnlyDict(d)
        self.assertEqual(len(id), 1)

    def test_iter(self):
        d = {"key": "value"}
        id = CaseInsensitiveReadOnlyDict(d)
        self.assertEqual([i for i in id], ["KEY"])

    def test_getitem__correct_case(self):
        d = {"key": "value"}
        id = CaseInsensitiveReadOnlyDict(d)
        self.assertEqual(id["key"], "value")

    def test_getitem__incorrect_case(self):
        d = {"kEy": "value"}
        id = CaseInsensitiveReadOnlyDict(d)
        self.assertEqual(id["KeY"], "value")

    def test_actual_key_case(self):
        d = {"key": "value"}
        id = CaseInsensitiveReadOnlyDict(d)
        self.assertEqual(id.actual_key_case("KeY"), "key")
