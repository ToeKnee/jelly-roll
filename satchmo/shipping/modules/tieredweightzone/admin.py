from django.contrib import admin

from satchmo.shipping.modules.tieredweightzone.models import (
    Carrier,
    ShippingDiscount,
    WeightTier,
    Zone,
)


class WeightTierOptions(admin.ModelAdmin):
    extra = 6
    ordering = ("min_weight", "price", "expires")
    list_display = ("min_weight", "price", "zone", "carrier")
    list_display_links = ("min_weight", "price")
    list_filter = ("carrier", "zone")


class ZoneOptions(admin.ModelAdmin):
    ordering = ("key",)


class CarrierOptions(admin.ModelAdmin):
    list_display = (
        "__str__",
        "estimated_delivery_min_days",
        "estimated_delivery_expected_days",
        "estimated_delivery_max_days",
    )
    ordering = ("key",)


class ShippingDiscountOptions(admin.ModelAdmin):
    ordering = ("end_date", "-percentage", "minimum_order_value")
    list_display = (
        "minimum_order_value",
        "percentage",
        "start_date",
        "end_date",
        "zone",
        "carrier",
    )
    list_filter = ("carrier", "zone")


admin.site.register(WeightTier, WeightTierOptions)
admin.site.register(Zone, ZoneOptions)
admin.site.register(Carrier, CarrierOptions)
admin.site.register(ShippingDiscount, ShippingDiscountOptions)
