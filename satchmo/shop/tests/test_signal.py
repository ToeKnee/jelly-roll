from django.test import TestCase
from django.contrib.sites.models import Site

from satchmo import caching
from satchmo.caching import cache_delete
from satchmo.l10n.factories import USFactory
from satchmo.product.factories import ProductFactory
from satchmo.shop.exceptions import CartAddProhibited
from satchmo.shop.factories import TestOrderFactory
from satchmo.shop.models import Cart
from satchmo.shop import signals


def vetoAllListener(sender, vetoes={}, **kwargs):
    raise CartAddProhibited(None, "No")


class SignalTest(TestCase):
    def setUp(self):
        caching.cache_delete()
        signals.satchmo_cart_add_verify.connect(vetoAllListener)
        self.US = USFactory()

    def tearDown(self):
        cache_delete()
        signals.satchmo_cart_add_verify.disconnect(vetoAllListener)

    def testCartAddVerifyVeto(self):
        """Test that vetoes from `signals.satchmo_cart_add_verify` are caught and cause an error."""
        try:
            site = Site.objects.get_current()
            cart = Cart(site=site)
            cart.save()
            p = ProductFactory()
            cart.add_item(p, 1)
            TestOrderFactory()
            self.fail("Should have thrown a CartAddProhibited error")
        except CartAddProhibited:
            pass

        self.assertEqual(len(cart), 0)
