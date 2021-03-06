from decimal import Decimal

from django.test import TestCase
from satchmo import caching
from satchmo.configuration.functions import config_value
from satchmo.product.models import ConfigurableProduct, DownloadableProduct, Product
from satchmo.shipping.modules.flat.shipper import Shipper as flat
from satchmo.shipping.modules.per.shipper import Shipper as per
from satchmo.shop.models import Cart


class ShippingBaseTest(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(slug="p1", name="p1")
        self.cart1 = Cart.objects.create()
        self.cartitem1 = self.cart1.add_item(self.product1, 3)

    def tearDown(self):
        caching.cache_delete()

    def test_downloadable_zero_shipping(self):
        subtypes = config_value("PRODUCT", "PRODUCT_TYPES")
        if "product::DownloadableProduct" in subtypes:
            subtype2 = DownloadableProduct.objects.create(product=self.product1)
            self.assertEqual(
                self.product1.get_subtypes(),
                ("ConfigurableProduct", "DownloadableProduct"),
            )

            self.assertFalse(subtype2.is_shippable)
            self.assertFalse(self.product1.is_shippable)
            self.assertFalse(self.cart1.is_shippable)
            self.assertEqual(flat(self.cart1, None).cost(), Decimal("0.00"))
            self.assertEqual(per(self.cart1, None).cost(), Decimal("0.00"))

    def test_simple_shipping(self):
        # Product.is_shippable should be True unless the Product has a subtype
        # where is_shippable == False
        subtype1 = ConfigurableProduct.objects.create(product=self.product1)
        self.assertTrue(getattr(subtype1, "is_shippable", True))
        self.assertTrue(self.cartitem1.is_shippable)
        self.assertTrue(self.product1.is_shippable)
        self.assertTrue(self.cart1.is_shippable)
        self.assertEqual(flat(self.cart1, None).cost(), Decimal("4.00"))
        self.assertEqual(per(self.cart1, None).cost(), Decimal("12.00"))
