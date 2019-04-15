from satchmo.wishlist.models import ProductWish
from django.contrib import admin


class ProductWishOptions(admin.ModelAdmin):
    list_display = ("contact", "product", "create_date")
    ordering = ("contact", "-create_date", "product")


admin.site.register(ProductWish, ProductWishOptions)
