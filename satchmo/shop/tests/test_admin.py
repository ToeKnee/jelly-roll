from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from satchmo.caching import cache_delete


class AdminTest(TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('fredsu', 'fred@root.org', 'passwd')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.login(username='fredsu', password='passwd')

    def tearDown(self):
        cache_delete()

    def test_index(self):
        response = self.client.get('/admin/')
        self.assertContains(response, "contact/contact/", status_code=200)

    def test_product(self):
        response = self.client.get('/admin/product/product/1/')
        self.assertContains(response, "Django Rocks shirt", status_code=200)

    def test_configurableproduct(self):
        response = self.client.get('/admin/product/configurableproduct/1/')
        self.assertContains(response, "Small, Black", status_code=200)

    def test_productimage_list(self):
        response = self.client.get('/admin/product/productimage/')
        self.assertContains(response, "Photo Not Available", status_code=200)

    def test_productimage(self):
        response = self.client.get('/admin/product/productimage/1/')
        self.assertContains(response, "Photo Not Available", status_code=200)
