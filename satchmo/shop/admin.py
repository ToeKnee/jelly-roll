from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from satchmo.shop.models import Cart
from satchmo.shop.models import CartItem
from satchmo.shop.models import CartItemDetails
from satchmo.shop.models import Config
from satchmo.shop.models import DownloadLink
from satchmo.shop.models import Order
from satchmo.shop.models import OrderItem
from satchmo.shop.models import OrderItemDetail
from satchmo.shop.models import OrderPayment
from satchmo.shop.models import OrderStatus
from satchmo.shop.models import OrderTaxDetail
from satchmo.shop.models import OrderVariable
from satchmo.shop.models import Status

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
        (None, {'fields': (
            'site', 'store_name', 'store_description', 'no_stock_checkout')
            }),
        (_('Store Contact'), {'fields' : (
            'store_email', 'street1', 'street2',
            'city', 'state', 'postal_code', 'country',)
            }),
        (_('Shipping Countries'), {'fields' : (
            'in_country_only', 'sales_country', 'shipping_countries')
            })
    )

class CartOptions(admin.ModelAdmin):
    list_display = ('date_time_created','numItems','total')
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

class Status_Inline(admin.TabularInline):
    model = Status

class OrderStatus_Inline(admin.StackedInline):
    model = OrderStatus
    readonly_fields = ('time_stamp',)
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
         {'fields': ('site', 'contact', 'method', 'discount_code', 'notes', 'time_stamp', 'frozen')}),
        (_('Shipping Method'),
         {'fields': ('shipping_method', 'shipping_description')}),
        (_('Shipping Address'),
         {'classes': ('collapse',),
          'fields': ('ship_street1', 'ship_street2', 'ship_city', 'ship_state', 'ship_postal_code', 'ship_country')}),
        (_('Billing Address'),
         {'classes': ('collapse',),
          'fields': ('bill_street1', 'bill_street2', 'bill_city', 'bill_state', 'bill_postal_code', 'bill_country')}),
        (_('Totals'),
         {'fields': ('sub_total', 'shipping_cost', 'shipping_discount', 'tax', 'discount', 'total')}
         )
        )
    readonly_fields = ('time_stamp', 'frozen',)
    list_display = ('id', 'contact', 'contact_user', 'time_stamp', 'order_total', 'balance_forward', 'status', 'invoice', 'packingslip', 'shippinglabel', 'frozen')
    list_filter = ['time_stamp', 'status__status', 'frozen']
    search_fields = ['id', 'contact__user__username', 'contact__user__email', 'contact__first_name', 'contact__last_name', 'contact__email']
    date_hierarchy = 'time_stamp'
    inlines = [OrderItem_Inline, OrderStatus_Inline, OrderVariable_Inline, OrderTaxDetail_Inline]
    actions = ['shipped']

    def shipped(self, request, queryset):
        rows_updated = 0
        for obj in queryset:
            shipped_status = Status.objects.get(status="Shipped")
            obj.add_status(status=shipped_status, notes=u"Thanks for your order")
            rows_updated += 1
        if rows_updated == 1:
            message_bit = "1 order was"
        else:
            message_bit = "%s orders were" % rows_updated
        self.message_user(request, "%s successfully set to Shipped." % message_bit)
    shipped.short_description = "Set selected Product Orders to Shipped"

    def contact_user(self, obj):
        return obj.contact.user
    contact_user.short_description = 'Contact User'


class OrderItemOptions(admin.ModelAdmin):
    inlines = [OrderItemDetail_Inline]

class OrderPaymentOptions(admin.ModelAdmin):
    list_filter = ['order', 'payment']
    list_display = ['id', 'order', 'payment', 'amount_total', 'time_stamp']
    fieldsets = (
        (None, {'fields': ('order', 'payment', 'amount', 'transaction_id', 'time_stamp')}), )

admin.site.register(Cart, CartOptions)
admin.site.register(CartItem, CartItemOptions)
admin.site.register(Config, ConfigOptions)
admin.site.register(DownloadLink)
admin.site.register(Status, StatusOptions)
admin.site.register(Order, OrderOptions)
admin.site.register(OrderItem, OrderItemOptions)
admin.site.register(OrderPayment, OrderPaymentOptions)
