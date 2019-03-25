from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from satchmo.product.brand.models import Brand, BrandTranslation


class BrandTranslation_Inline(admin.StackedInline):
    model = BrandTranslation
    extra = 1
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")


class BrandOptions(admin.ModelAdmin):
    inlines = [BrandTranslation_Inline]


class BrandTranslationOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("brand", "languagecode", "name", "description", "picture")}),
    )


admin.site.register(Brand, BrandOptions)
