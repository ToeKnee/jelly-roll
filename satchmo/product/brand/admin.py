from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from satchmo.product.brand.models import Brand


class BrandOptions(admin.ModelAdmin):
    pass


class BrandTranslationOptions(admin.ModelAdmin):
    fieldsets = ((None, {"fields": ("brand", "name", "description", "picture")}),)


admin.site.register(Brand, BrandOptions)
