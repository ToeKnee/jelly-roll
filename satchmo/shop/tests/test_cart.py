from decimal import Decimal

from django.test import TestCase
from django.contrib.sites.models import Site

from satchmo.caching import cache_delete
from satchmo.product.factories import ProductFactory
from satchmo.product.models import Product
from satchmo.shop.satchmo_settings import get_satchmo_setting
from satchmo.shop.models import (
    Cart,
    Config,
)


prefix = get_satchmo_setting('SHOP_BASE')
if prefix == '/':
    prefix = ''


class CartTest(TestCase):
    def tearDown(self):
        cache_delete()

    def test_cart_adding(self, retest=False):
        """
        Validate we can add some items to the cart
        """
        product = ProductFactory()
        print product.get_absolute_url()
        if not retest:
            response = self.client.get(product.get_absolute_url())
            self.assertContains(response, str(product), count=2, status_code=200)

        data = {
            "productname": product.slug,
            "1": "L",
            "2": "BL",
            "quantity": 2,
        }
        response = self.client.post(prefix + '/cart/add/', data)
        if not retest:
            self.assertRedirects(response, prefix + '/cart/',
                                 status_code=302, target_status_code=200)
        response = self.client.get(prefix + '/cart/')
        expect = "<a href=\"%s/product/dj-rocks-l-bl/\">Django Rocks shirt (Large/Blue)</a>" % (prefix)
        self.assertContains(response, expect, count=1, status_code=200)

    def test_cart_adding_errors(self):
        """
        Test proper error reporting when attempting to add items to the cart.
        """

        # Attempting to add a nonexistent product should result in a 404 error.
        response = self.client.post(prefix + '/cart/add/',
                                    {'productname': 'nonexistent-product', 'quantity': '1'})
        self.assertContains(response, "The product you have requested does not exist.", count=1, status_code=404)

        # You should not be able to add a product that is inactive.
        py_shirt = Product.objects.get(slug='PY-Rocks')
        py_shirt.active = False
        py_shirt.save()
        response = self.client.post(prefix + '/cart/add/',
                                    {'productname': 'PY-Rocks', 'quantity': '1'})
        self.assertContains(response, "That product is not available at the moment.", count=1, status_code=200)

        # You should not be able to add a product with a non-integer quantity.
        response = self.client.post(prefix + '/cart/add/',
                                    {'productname': 'neat-book', '3': 'soft', 'quantity': '1.5'})
        self.assertContains(response, "Please enter a whole number.", count=1, status_code=200)

        # You should not be able to add a product with a quantity less than one.
        response = self.client.post(prefix + '/cart/add/',
                                    {'productname': 'neat-book', '3': 'soft', 'quantity': '0'})
        self.assertContains(response, "Please enter a positive number.", count=1, status_code=200)

        # If no_stock_checkout is False, you should not be able to order a
        # product that is out of stock.
        shop_config = Config.objects.get_current()
        shop_config.no_stock_checkout = False
        shop_config.save()
        response = self.client.post(prefix + '/cart/add/',
                                    {'productname': 'neat-book', '3': 'soft', 'quantity': '1'})
        self.assertContains(response, "&#39;A really neat book (Soft cover)&#39; is out of stock.", count=1, status_code=200)

    def test_cart_removing(self):
        """
        Validate we can remove an item
        """
        print "Works with Mysql, and sqlite3 but not Postgres!"
        shop_config = Config.objects.get_current()
        shop_config.no_stock_checkout = True
        shop_config.save()

        self.test_cart_adding(retest=True)
        response = self.client.post(prefix + '/cart/remove/', {'cartitem': '1'})
        response = self.client.get(prefix + '/cart/')
        self.assertContains(response, "Your cart is empty.", count=1, status_code=200)

    def test_line_cost(self):
        lb = Product.objects.get(slug__iexact='dj-rocks-l-bl')
        sb = Product.objects.get(slug__iexact='dj-rocks-s-b')

        cart = Cart(site=Site.objects.get_current())
        cart.save()
        cart.add_item(sb, 1)
        self.assertEqual(cart.numItems, 1)
        self.assertEqual(cart.total, Decimal("20.00"))

        cart.add_item(lb, 1)
        self.assertEqual(cart.numItems, 2)
        items = list(cart.cartitem_set.all())
        item1 = items[0]
        item2 = items[1]
        self.assertEqual(item1.unit_price, Decimal("20.00"))
        self.assertEqual(item2.unit_price, Decimal("23.00"))
        self.assertEqual(cart.total, Decimal("43.00"))
