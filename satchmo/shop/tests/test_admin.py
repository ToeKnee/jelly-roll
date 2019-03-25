from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.utils.translation import gettext_lazy as _

from satchmo.shop.admin import OrderOptions, OrderStatusListFilter
from satchmo.shop.factories import (
    StatusFactory,
    TestOrderFactory,
    PaidOrderFactory,
    ShippedOrderFactory,
)
from satchmo.shop.models import Order, OrderStatus


class OrderStatusListFilterTest(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()

    def test_pipeline_approved_list_filter__lookups(self):
        StatusFactory(status="Processing")
        StatusFactory(status="Shipped")
        admin = OrderOptions(OrderStatus, AdminSite())
        request = self.request_factory.get("/admin")

        list_filter = OrderStatusListFilter(request, {}, OrderStatus, admin)

        self.assertEqual(
            list(list_filter.lookups(request, admin)),
            [("Processing", _("Processing")), ("Shipped", _("Shipped"))],
        )

    def test_pipeline_approved_list_filter__queryset_no_filter(self):
        admin = OrderOptions(OrderStatus, AdminSite())
        request = self.request_factory.get("/admin")

        list_filter = OrderStatusListFilter(request, {}, OrderStatus, admin)

        order = TestOrderFactory()
        paid = PaidOrderFactory()
        shipped = ShippedOrderFactory()

        queryset = Order.objects.all()

        self.assertIn(order, list_filter.queryset(request, queryset))
        self.assertIn(paid, list_filter.queryset(request, queryset))
        self.assertIn(shipped, list_filter.queryset(request, queryset))

    def test_pipeline_approved_list_filter__queryset_filtered(self):
        admin = OrderOptions(OrderStatus, AdminSite())
        request = self.request_factory.get("/admin")

        list_filter = OrderStatusListFilter(
            request, {"status": "Shipped"}, OrderStatus, admin
        )

        order = TestOrderFactory()
        paid = PaidOrderFactory()
        shipped = ShippedOrderFactory()

        queryset = Order.objects.all()

        self.assertNotIn(order, list_filter.queryset(request, queryset))
        self.assertNotIn(paid, list_filter.queryset(request, queryset))
        self.assertIn(shipped, list_filter.queryset(request, queryset))
