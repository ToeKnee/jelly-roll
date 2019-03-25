from django.urls import reverse
from django.test import TestCase
from satchmo import caching
from satchmo.shop.satchmo_settings import get_satchmo_setting

domain = "http://example.com"
prefix = get_satchmo_setting("SHOP_BASE")
if prefix == "/":
    prefix = ""


class GoogleBaseTest(TestCase):
    """Test Google Base feed."""

    fixtures = [
        "l10n_data.xml",
        "sample-store-data.yaml",
        "products.yaml",
        "test-config.yaml",
    ]

    def tearDown(self):
        caching.cache_delete

    def test_feed(self):
        url = reverse("satchmo_atom_feed")
        response = self.client.get(url)
        self.assertContains(
            response,
            "<title>Robots Attack! (Hard cover)</title>",
            count=1,
            status_code=200,
        )
        self.assertContains(
            response,
            '<link href="%s%s/product/robot-attack-hard/" />' % (domain, prefix),
            count=1,
            status_code=200,
        )
