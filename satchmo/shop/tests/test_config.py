from django.test import TestCase

from satchmo.caching import cache_delete
from satchmo.shop.factories import ShopConfigFactory
from satchmo.shop.models import Config


class ConfigTest(TestCase):
    def tearDown(self):
        cache_delete()

    def test_base_url(self):
        ShopConfigFactory()
        config = Config.objects.get_current()
        self.assertEqual(config.base_url, 'http://example.com')
