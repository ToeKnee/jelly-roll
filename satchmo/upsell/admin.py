from satchmo.upsell.models import Upsell
from django.contrib import admin
from django.utils.translation import get_language, ugettext_lazy as _


class UpsellOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("target", "goal", "style", "notes", "create_date")}),
    )
    filter_horizontal = ("target",)


admin.site.register(Upsell, UpsellOptions)
