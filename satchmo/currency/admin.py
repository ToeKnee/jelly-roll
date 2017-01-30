from django.contrib import admin

from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    filter_horizontal = ("countries", )
    list_display = ("iso_4217_code", "name", "symbol", "minor_symbol")
