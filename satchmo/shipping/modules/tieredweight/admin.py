from satchmo.shipping.modules.tieredweight.models import Carrier, WeightTier, CarrierTranslation
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _

class WeightTier_Inline(admin.TabularInline):
    model = WeightTier
    extra = 6
    ordering = ('weight', 'expires')

class CarrierTranslation_Inline(admin.TabularInline):
    model = CarrierTranslation
    extra = 1

class CarrierOptions(admin.ModelAdmin):
    ordering = ('key',)
    inlines = [CarrierTranslation_Inline, WeightTier_Inline, ]

admin.site.register(Carrier, CarrierOptions)

