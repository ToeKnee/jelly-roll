from django.contrib import admin

from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    filter_horizontal = ("countries", )
    list_display = ("iso_4217_code", "name", "symbol", "minor_symbol", "primary", "accepted")
    list_filter = ("accepted", )
    search_fields = ("iso_4217_code", "name", "symbol", "countries__printable_name")
    ordering = ("-primary", "-accepted", "iso_4217_code")
