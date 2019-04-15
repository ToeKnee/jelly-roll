from satchmo.product.models import (
    Category,
    CategoryTranslation,
    CategoryImage,
    CategoryImageTranslation,
    OptionGroup,
    OptionGroupTranslation,
    Option,
    OptionTranslation,
    Product,
    CustomProduct,
    CustomTextField,
    CustomTextFieldTranslation,
    ConfigurableProduct,
    DownloadableProduct,
    SubscriptionProduct,
    Trial,
    ProductVariation,
    ProductAttribute,
    Price,
    ProductImage,
    ProductImageTranslation,
    ProductTranslation,
    IngredientsList,
    Instruction,
    Precaution,
)
from django.contrib import admin
from django.forms import models, ValidationError
from django.utils.translation import ugettext_lazy as _
from satchmo.shop.satchmo_settings import get_satchmo_setting


class CategoryTranslation_Inline(admin.StackedInline):
    model = CategoryTranslation
    extra = 1


class CategoryImage_Inline(admin.TabularInline):
    model = CategoryImage
    extra = 3


class CategoryImageTranslation_Inline(admin.StackedInline):
    model = CategoryImageTranslation
    extra = 1


class OptionGroupTranslation_Inline(admin.StackedInline):
    model = OptionGroupTranslation
    extra = 1


class Option_Inline(admin.TabularInline):
    model = Option
    extra = 5


class OptionTranslation_Inline(admin.StackedInline):
    model = OptionTranslation
    extra = 1


class CustomTextField_Inline(admin.TabularInline):
    model = CustomTextField
    extra = 3


class CustomTextFieldTranslation_Inline(admin.StackedInline):
    model = CustomTextFieldTranslation
    extra = 1


class Trial_Inline(admin.StackedInline):
    model = Trial
    extra = 2


class ProductAttribute_Inline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


class Price_Inline(admin.TabularInline):
    model = Price
    extra = 1
    verbose_name = _("Price Discount")
    verbose_name_plural = _("Price Discounts")


class ProductImage_Inline(admin.StackedInline):
    model = ProductImage
    extra = 3


class ProductTranslation_Inline(admin.TabularInline):
    model = ProductTranslation
    extra = 1


class ProductImageTranslation_Inline(admin.StackedInline):
    model = ProductImageTranslation
    extra = 1


class CategoryAdminForm(models.ModelForm):
    def clean_parent(self):
        parent = self.cleaned_data["parent"]
        slug = self.cleaned_data["slug"]
        if parent and slug:
            if parent.slug == slug:
                raise ValidationError(_("You must not save a category in itself!"))

            for p in parent._recurse_for_parents(parent):
                if slug == p.slug:
                    raise ValidationError(_("You must not save a category in itself!"))

        return parent


class CategoryOptions(admin.ModelAdmin):
    list_display = ("active", "name", "_parents_repr")
    list_display_links = ("name",)
    list_editable = ("active",)
    ordering = ["active", "parent__id", "ordering", "name"]
    inlines = [CategoryImage_Inline]
    if get_satchmo_setting("ALLOW_PRODUCT_TRANSLATIONS"):
        inlines.append(CategoryTranslation_Inline)
    filter_horizontal = ("related_categories",)
    form = CategoryAdminForm


class CategoryImageOptions(admin.ModelAdmin):
    inlines = [CategoryImageTranslation_Inline]


class OptionGroupOptions(admin.ModelAdmin):
    inlines = [Option_Inline]
    if get_satchmo_setting("ALLOW_PRODUCT_TRANSLATIONS"):
        inlines.append(OptionGroupTranslation_Inline)

    list_display = ["name"]


class OptionOptions(admin.ModelAdmin):
    inlines = []
    if get_satchmo_setting("ALLOW_PRODUCT_TRANSLATIONS"):
        inlines.append(OptionTranslation_Inline)


class ProductOptions(admin.ModelAdmin):
    list_display = (
        "slug",
        "sku",
        "name",
        "unit_price",
        "items_in_stock",
        "total_sold",
        "get_subtypes",
    )
    list_display_links = ("slug", "name")
    list_editable = ("items_in_stock",)
    list_filter = ("active", "category", "brands")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "name",
                    ("slug", "sku"),
                    "description",
                    "enhanced_description",
                    "short_description",
                    ("active", "featured"),
                    "unit_price",
                    ("items_in_stock", "total_sold"),
                    "ordering",
                    "shipclass",
                    ("instructions", "precautions"),
                )
            },
        ),
        (_("Meta Data"), {"fields": ("meta",), "classes": ("collapse",)}),
        (
            _("Item Dimensions"),
            {
                "fields": (
                    (
                        "length",
                        "length_units",
                        "width",
                        "width_units",
                        "height",
                        "height_units",
                    ),
                    ("weight", "weight_units"),
                ),
                "classes": ("collapse",),
            },
        ),
        (_("Tax"), {"fields": ("taxable", "taxClass"), "classes": ("collapse",)}),
        (
            _("Related Products"),
            {"fields": ("related_items", "also_purchased"), "classes": "collapse"},
        ),
    )
    inlines = [Price_Inline, ProductAttribute_Inline, ProductImage_Inline]
    readonly_fields = ("total_sold",)
    search_fields = ["slug", "sku", "name", "brands__slug"]
    if get_satchmo_setting("ALLOW_PRODUCT_TRANSLATIONS"):
        inlines.append(ProductTranslation_Inline)
    filter_horizontal = ("category", "related_items", "also_purchased")


class CustomProductOptions(admin.ModelAdmin):
    inlines = [CustomTextField_Inline]


class CustomTextFieldOptions(admin.ModelAdmin):
    inlines = []
    if get_satchmo_setting("ALLOW_PRODUCT_TRANSLATIONS"):
        inlines.append(CustomTextFieldTranslation_Inline)


class SubscriptionProductOptions(admin.ModelAdmin):
    inlines = [Trial_Inline]


class ProductVariationOptions(admin.ModelAdmin):
    filter_horizontal = ("options",)


class ProductImageOptions(admin.ModelAdmin):
    inlines = []
    if get_satchmo_setting("ALLOW_PRODUCT_TRANSLATIONS"):
        inlines.append(ProductImageTranslation_Inline)


class IngredientsListOptions(admin.ModelAdmin):
    pass


class InstructionsOptions(admin.ModelAdmin):
    pass


class PrecautionsOptions(admin.ModelAdmin):
    pass


admin.site.register(Category, CategoryOptions)
admin.site.register(OptionGroup, OptionGroupOptions)
admin.site.register(Option, OptionOptions)
admin.site.register(Product, ProductOptions)
admin.site.register(CustomProduct, CustomProductOptions)
admin.site.register(CustomTextField, CustomTextFieldOptions)
admin.site.register(ConfigurableProduct)
admin.site.register(DownloadableProduct)
admin.site.register(SubscriptionProduct, SubscriptionProductOptions)
admin.site.register(ProductVariation, ProductVariationOptions)
admin.site.register(IngredientsList, IngredientsListOptions)
admin.site.register(Instruction, InstructionsOptions)
admin.site.register(Precaution, PrecautionsOptions)
