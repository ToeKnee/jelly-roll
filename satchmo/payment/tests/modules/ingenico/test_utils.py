from django.test import TestCase

from satchmo.caching import cache_delete
from satchmo.configuration.models import Setting
from satchmo.payment.modules.ingenico.utils import shasign, verify_shasign


class ShaSignTest(TestCase):
    def tearDown(self):
        cache_delete()

    def test_generates_key(self):
        data = {
            "key_1": "val_1",
            "key_2": "val_2",
        }

        self.assertEqual(
            shasign(data),
            "a03bed660c957ee6fcf9039476e76cfde54f1fcc7f8c5897d34f70fc06029f8fa6585f6020f5fc4ef90f473756b4d43b04328ed1f3cbc0b221756ddff89de2f3"
        )

    def test_different_secrets_produce_different_keys(self):
        data = {
            "key_1": "val_1",
            "key_2": "val_2",
        }
        default_key = shasign(data)

        # Set a new secret key
        Setting.objects.create(
            key='SECRET',
            group='PAYMENT_INGENICO',
            value="My New Key",
        )

        new_key = shasign(data)
        self.assertNotEqual(default_key, new_key)

    def test_excludes_SHASIGN_key(self):
        data = {
            "key_1": "val_1",
            "key_2": "val_2",
        }
        without_shasign = shasign(data)

        # Add the shasign to the data and generate again
        data["SHASIGN"] = without_shasign
        with_shasign = shasign(data)
        self.assertEqual(with_shasign, without_shasign)


class VerifyShaSignTest(TestCase):
    def test_valid_signature(self):
        data = {
            "key_1": "val_1",
            "key_2": "val_2",
        }

        self.assertTrue(
            verify_shasign("a03bed660c957ee6fcf9039476e76cfde54f1fcc7f8c5897d34f70fc06029f8fa6585f6020f5fc4ef90f473756b4d43b04328ed1f3cbc0b221756ddff89de2f3", data),
        )

    def test_invalid_signature(self):
        data = {
            "key_1": "val_1",
            "key_2": "val_2",
        }

        self.assertFalse(
            verify_shasign("a03bed660c957ee6fcf90394", data),
        )
