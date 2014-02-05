from satchmo.l10n.models import Country, AdminArea
from django.contrib import admin


class AdminArea_Inline(admin.TabularInline):
    model = AdminArea
    extra = 1


class CountryOptions(admin.ModelAdmin):
    list_display = ('printable_name', 'iso2_code', 'eu',)
    list_filter = ('continent', 'active', 'eu',)
    search_fields = ('name', 'iso2_code', 'iso3_code')
    inlines = [AdminArea_Inline]

admin.site.register(Country, CountryOptions)
