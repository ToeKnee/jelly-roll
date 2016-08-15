from django.contrib import admin

from satchmo.shipping.modules.tieredweightzone.models import (
    Carrier,
    CarrierTranslation,
    ShippingDiscount,
    WeightTier,
    Zone,
    ZoneTranslation,
)


class WeightTierOptions(admin.ModelAdmin):
    extra = 6
    ordering = ('min_weight', 'price', 'expires')
    list_display = ('min_weight', 'price', 'zone', 'carrier')
    list_display_links = ('min_weight', 'price')
    list_filter = ('carrier', 'zone')


class ZoneTransaltion_Inline(admin.TabularInline):
    model = ZoneTranslation
    extra = 1


class ZoneOptions(admin.ModelAdmin):
    ordering = ('key',)
    inlines = [ZoneTransaltion_Inline]


class CarrierTranslation_Inline(admin.TabularInline):
    model = CarrierTranslation
    extra = 1


class CarrierOptions(admin.ModelAdmin):
    list_display = ('__unicode__', 'estimated_delivery_min_days', 'estimated_delivery_expected_days', 'estimated_delivery_max_days')
    ordering = ('key',)
    inlines = [CarrierTranslation_Inline]


class ShippingDiscountOptions(admin.ModelAdmin):
    ordering = ('end_date', '-percentage', 'minimum_order_value')
    list_display = ('minimum_order_value', 'percentage', 'start_date', 'end_date', 'zone', 'carrier')
    list_filter = ('carrier', 'zone')


admin.site.register(WeightTier, WeightTierOptions)
admin.site.register(Zone, ZoneOptions)
admin.site.register(Carrier, CarrierOptions)
admin.site.register(ShippingDiscount, ShippingDiscountOptions)
