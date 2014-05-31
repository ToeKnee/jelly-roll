from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from satchmo.product.admin import ProductOptions
from satchmo.product.brand.models import (
    Brand,
    BrandTranslation
)
from satchmo.product.models import Product
from satchmo.thumbnail.field import ImageWithThumbnailField
from satchmo.thumbnail.widgets import AdminImageWithThumbnailWidget


class BrandTranslation_Inline(admin.StackedInline):
    model = BrandTranslation
    extra = 1
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")

# TODO: Fix or remove.
#def formfield_for_dbfield(self, db_field, **kwargs):
#        # This method will turn all TextFields into giant TextFields
#        if isinstance(db_field, ImageWithThumbnailField):
#            kwargs['widget'] = AdminImageWithThumbnailWidget
#            return db_field.formfield(**kwargs)
#
#        return super(BrandTranslation_Inline, self).formfield_for_dbfield(db_field, **kwargs)


class BrandOptions(admin.ModelAdmin):
    inlines = [BrandTranslation_Inline]


class BrandTranslationOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('brand', 'languagecode', 'name', 'description', 'picture')}),
    )


admin.site.register(Brand, BrandOptions)
