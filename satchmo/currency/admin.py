from django.contrib import admin

from .models import Currency, ExchangeRate


class ExchangeRateInline(admin.TabularInline):
    model = ExchangeRate
    readonly_fields = ("currency", "date", "rate")
    ordering = ("-date",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    filter_horizontal = ("countries",)
    list_display = (
        "iso_4217_code",
        "name",
        "symbol",
        "minor_symbol",
        "primary",
        "accepted",
        "current_exchange_rate",
    )
    list_filter = ("accepted",)
    search_fields = ("iso_4217_code", "name", "symbol", "countries__printable_name")
    ordering = ("-primary", "-accepted", "iso_4217_code")
    inlines = [ExchangeRateInline]

    def current_exchange_rate(self, obj):
        try:
            exr = obj.exchange_rates.latest()
        except ExchangeRate.DoesNotExist:
            return ""
        else:
            return exr.rate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    list_display = ("currency", "rate", "date")
    list_filter = ("currency", "date")
    readonly_fields = ("currency", "date", "rate")
    search_fields = (
        "currency__name",
        "currency__iso_4217_code",
        "currency__symbol",
        "date",
    )
    ordering = ("-date", "currency")
