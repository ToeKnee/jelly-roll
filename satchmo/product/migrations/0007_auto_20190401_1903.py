# Generated by Django 2.1.7 on 2019-04-01 19:03

from django.db import migrations
from datetime import date


def copy_prices(apps, schema_editor):
    # We can't import the Product model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Product = apps.get_model("product", "Product")
    today = date.today()
    for product in Product.objects.all():
        price = product.price_set.filter(quantity=1, expires=None).last()
        if price:
            product.unit_price = price.price
            product.save()

            # Remove old prices
            price.delete()


class Migration(migrations.Migration):

    dependencies = [("product", "0006_product_unit_price")]

    operations = [migrations.RunPython(copy_prices)]
