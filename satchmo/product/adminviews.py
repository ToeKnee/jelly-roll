from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from satchmo.shop.models import Order
from satchmo.product import forms
from satchmo.product.models import Product
from satchmo.product.forms import VariationManagerForm
from satchmo.shop.views.utils import bad_or_missing
import logging

log = logging.getLogger(__name__)


def edit_inventory(request):
    """A quick inventory price, qty update form"""
    if request.method == "POST":
        new_data = request.POST.copy()
        form = forms.InventoryForm(new_data)
        if form.is_valid():
            form.save(request)
            url = reverse('satchmo_admin_edit_inventory')
            return HttpResponseRedirect(url)
    else:
        form = forms.InventoryForm()

    context = {
        'title': _('Inventory Editor'),
        'form': form,
    }

    return render(request, 'admin/inventory_form.html', context)


edit_inventory = user_passes_test(lambda u: u.is_authenticated(
) and u.is_staff, login_url='/accounts/login/')(edit_inventory)


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def picking_list(request):
    """A view that returns a list of stock items that need to be picked from the shelf

    Products are order by manufacturer, brand, then product name.
    """
    processing_orders = Order.objects.filter(
        status__status__status="Processing")
    # Category - products
    products = {}

    for order in processing_orders:
        for item in order.orderitem_set.all():
            brand = item.product.brands.all()
            if brand.count():
                brand = brand[0].translation.name
            else:
                brand = "Unknown"

            brand_data = products.get(brand, {})
            product_quantity = brand_data.get(item.product.name, 0)

            brand_data[item.product.name] = product_quantity + item.quantity
            products[brand] = brand_data

    # Sort the dict into a list of tuples
    # so we can order alphabetically
    for brand in products:
        products[brand] = list(products[brand].items())
        products[brand].sort()

    context = {
        'title': "Picking List",
        'products': products,
        'order_count': processing_orders.count(),
    }
    return render(request, 'admin/picking_list.html', context)


def export_products(request, template='admin/product_export_form.html'):
    """A product export tool"""
    if request.method == 'POST':
        new_data = request.POST.copy()
        form = forms.ProductExportForm(new_data)
        if form.is_valid():
            return form.export(request)
    else:
        form = forms.ProductExportForm()
        fileform = forms.ProductImportForm()

    context = {
        'title': _('Product Import/Export'),
        'form': form,
        'importform': fileform,
    }

    return render(request, template, context)


export_products = user_passes_test(lambda u: u.is_authenticated(
) and u.is_staff, login_url='/accounts/login/')(export_products)


def import_products(request, maxsize=10000000):
    """
    Imports product from an uploaded file.
    """

    if request.method == 'POST':
        errors = []
        results = []
        if 'upload' in request.FILES:
            infile = request.FILES['upload']
            form = forms.ProductImportForm()
            results, errors = form.import_from(infile, maxsize=maxsize)

        else:
            errors.append('File: %s' % list(request.FILES.keys()))
            errors.append(_('No upload file found'))

        context = {
            'errors': errors,
            'results': results,
        }
        return render(request, "admin/product_import_result.html", context)
    else:
        url = reverse('satchmo_admin_product_export')
        return HttpResponseRedirect(url)


import_products = user_passes_test(lambda u: u.is_authenticated(
) and u.is_staff, login_url='/accounts/login/')(import_products)


def product_active_report(request):
    products = Product.objects.filter(active=True)
    products = [
        p
        for p
        in products.all()
        if 'productvariation' not in p.get_subtypes
    ]
    context = {'title': 'Active Product Report', 'products': products}
    return render(request, 'admin/product/active_product_report.html', context)


product_active_report = user_passes_test(lambda u: u.is_authenticated(
) and u.is_staff, login_url='/accounts/login/')(product_active_report)


def variation_list(request):
    products = [p for p in Product.objects.all(
    ) if "ConfigurableProduct" in p.get_subtypes()]
    context = {
        'products': products,
    }

    return render(request, 'admin/product/configurableproduct/variation_manager_list.html', context)


def variation_manager(request, product_slug=""):
    try:
        product = Product.objects.get(slug=product_slug)
        subtypes = product.get_subtypes()

        if 'ProductVariation' in subtypes:
            # got a variation, we want to work with its parent
            product = product.productvariation.parent.product
            if 'ConfigurableProduct' in product.get_subtypes():
                url = reverse("satchmo_admin_variation_manager",
                              kwargs={'product_slug': product.slug})
                return HttpResponseRedirect(url)

        if 'ConfigurableProduct' not in subtypes:
            return bad_or_missing(request, _('The product you have requested is not a Configurable Product.'))

    except Product.DoesNotExist:
        return bad_or_missing(request, _('The product you have requested does not exist.'))

    if request.method == 'POST':
        new_data = request.POST.copy()
        form = VariationManagerForm(new_data, product=product)
        if form.is_valid():
            log.debug("Saving form")
            form.save(request)
            # rebuild the form
            form = VariationManagerForm(product=product)
        else:
            log.debug('errors on form')
    else:
        form = VariationManagerForm(product=product)

    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'admin/product/configurableproduct/variation_manager.html', context)


variation_manager = user_passes_test(lambda u: u.is_authenticated(
) and u.is_staff, login_url='/accounts/login/')(variation_manager)
