from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from satchmo.shop.models import (
    Cart,
    CartItem,
    CartItemDetails,
    Config,
    DownloadLink,
    Order,
    OrderItem,
    OrderItemDetail,
    OrderPayment,
    OrderRefund,
    OrderStatus,
    OrderTaxDetail,
    OrderVariable,
    Status,
)


class CartItem_Inline(admin.TabularInline):
    model = CartItem
    extra = 3


class CartItemDetails_Inline(admin.StackedInline):
    model = CartItemDetails
    extra = 1


class ConfigOptions(admin.ModelAdmin):
    list_display = ('site', 'store_name')
    filter_horizontal = ('shipping_countries',)
    fieldsets = (
        (None, {
            'fields': ('site', 'store_name', 'store_description', 'no_stock_checkout')
        }),
        (_('Store Contact'), {'fields': (
            'store_email', 'street1', 'street2',
            'city', 'state', 'postal_code', 'country',)
        }),
        (_('Shipping Countries'), {'fields': (
            'in_country_only', 'sales_country', 'shipping_countries')
        })
    )


class CartOptions(admin.ModelAdmin):
    list_display = ('date_time_created', 'numItems', 'total')
    inlines = [CartItem_Inline]


class CartItemOptions(admin.ModelAdmin):
    inlines = [CartItemDetails_Inline]


class OrderItem_Inline(admin.TabularInline):
    model = OrderItem
    extra = 3


class OrderItemDetail_Inline(admin.TabularInline):
    model = OrderItemDetail
    extra = 3


class StatusOptions(admin.ModelAdmin):
    model = Status
    list_display = ("status", "notify", "display")


class Status_Inline(admin.TabularInline):
    model = Status


class OrderStatus_Inline(admin.TabularInline):
    model = OrderStatus
    readonly_fields = ('time_stamp',)
    extra = 1


class OrderPayment_Inline(admin.TabularInline):
    model = OrderPayment
    readonly_fields = ('payment', 'amount', 'currency',
                       'exchange_rate', 'time_stamp', 'transaction_id')
    extra = 0


class OrderRefund_Inline(admin.TabularInline):
    model = OrderRefund
    readonly_fields = ('currency', 'exchange_rate', 'timestamp',)
    extra = 1


class OrderVariable_Inline(admin.TabularInline):
    model = OrderVariable
    extra = 1


class OrderTaxDetail_Inline(admin.TabularInline):
    model = OrderTaxDetail
    extra = 1


class OrderOptions(admin.ModelAdmin):
    fieldsets = (
        (None,
         {'fields': ('contact', 'method', 'discount_code', 'tracking_number', 'tracking_url', 'notes', 'time_stamp', 'frozen', 'fulfilled')}),
        (_('Shipping Information'),
         {'fields': ('shipping_method', 'shipping_description', 'shipping_date', 'estimated_delivery_min_date', 'estimated_delivery_expected_date', 'estimated_delivery_max_date')}),
        (_('Shipping Address'),
         {'classes': ('',),
          'fields': ('ship_street1', 'ship_street2', 'ship_city', 'ship_state', 'ship_postal_code', 'ship_country')}),
        (_('Billing Address'),
         {'classes': ('collapse',),
          'fields': ('bill_street1', 'bill_street2', 'bill_city', 'bill_state', 'bill_postal_code', 'bill_country')}),
        (_('Totals'),
         {'fields': ('currency', 'exchange_rate', 'sub_total', 'shipping_cost',
                     'shipping_discount', 'tax', 'discount', 'total', 'refund')}
         )
    )
    readonly_fields = ('contact', 'time_stamp', 'frozen', 'shipping_date', 'estimated_delivery_min_date',
                       'estimated_delivery_expected_date', 'estimated_delivery_max_date', 'currency', 'exchange_rate', 'refund')
    list_display = ('id', 'contact', 'contact_user', 'ship_country', 'time_stamp', 'display_total',
                    'balance_forward', 'status', 'late_date', 'tracking_number', 'invoice', 'frozen')
    list_filter = ['time_stamp', 'status__status', 'frozen']
    search_fields = ['id', 'contact__user__username', 'contact__user__email',
                     'contact__first_name', 'contact__last_name', 'contact__email']
    date_hierarchy = 'time_stamp'
    inlines = [OrderItem_Inline, OrderStatus_Inline, OrderPayment_Inline,
               OrderRefund_Inline, OrderVariable_Inline, OrderTaxDetail_Inline]
    actions = ['shipped']

    def shipped(self, request, queryset):
        rows_updated = 0
        for obj in queryset:
            shipped_status = Status.objects.get(status="Shipped")
            obj.add_status(status=shipped_status,
                           notes="Thanks for your order")
            rows_updated += 1
        if rows_updated == 1:
            message_bit = "1 order was"
        else:
            message_bit = "%s orders were" % rows_updated
        self.message_user(
            request, "%s successfully set to Shipped." % message_bit)
    shipped.short_description = "Set selected Product Orders to Shipped"

    def contact_user(self, obj):
        return obj.contact.user
    contact_user.short_description = 'Contact User'

    def late_date(self, obj):
        return obj.estimated_delivery_max_date().strftime("%d/%m/%Y")


class OrderItemOptions(admin.ModelAdmin):
    inlines = [OrderItemDetail_Inline]


class OrderPaymentOptions(admin.ModelAdmin):
    list_filter = ['payment']
    list_display = ['id', 'order', 'payment', 'amount_total', 'time_stamp']
    date_hierarchy = 'time_stamp'
    readonly_fields = ('order', 'exchange_rate', 'currency')
    fieldsets = (
        (None, {'fields': ('order', 'payment', 'amount', 'currency', 'exchange_rate', 'transaction_id', 'time_stamp')}), )
    search_fields = ['id', 'amount', 'order__id', 'order__contact__user__email',
                     'order__contact__first_name', 'order__contact__last_name', 'order__contact__email']


admin.site.register(Cart, CartOptions)
admin.site.register(CartItem, CartItemOptions)
admin.site.register(Config, ConfigOptions)
admin.site.register(DownloadLink)
admin.site.register(Status, StatusOptions)
admin.site.register(Order, OrderOptions)
admin.site.register(OrderItem, OrderItemOptions)
admin.site.register(OrderPayment, OrderPaymentOptions)
