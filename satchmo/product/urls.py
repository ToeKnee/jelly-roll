from django.urls import include, path
from satchmo.product.views import IngredientsListView
from satchmo.product.filterviews import display_bestsellers

from satchmo.product.adminviews import (
    edit_inventory,
    picking_list,
    export_products,
    import_products,
    product_active_report,
    variation_manager,
    variation_list,
)
from satchmo.product.brand.views import brand_category_page
from satchmo.product.views import (
    get_configurable_product_options,
    get_product,
    get_price,
    get_price_detail,
    category_view,
    category_index,
)


urlpatterns = [
    path('product/view/bestsellers/',
         display_bestsellers, {}, 'satchmo_product_best_selling'),
    path('product/ingredients/',
         IngredientsListView.as_view(), name="ingredients_list"),

    path('product/inventory/edit/',
         edit_inventory, {}, 'satchmo_admin_edit_inventory'),
    path('order/picking-list/',
         picking_list, {}, 'satchmo_admin_picking_list'),
    path('product/inventory/export/',
         export_products, {}, 'satchmo_admin_product_export'),
    path('product/inventory/import/',
         import_products, {}, 'satchmo_admin_product_import'),
    path('product/inventory/report/',
         product_active_report, {}, 'satchmo_admin_product_report'),
    path('product/admin/<slug:product_slug>/variations/',
         variation_manager, {}, 'satchmo_admin_variation_manager'),
    path('product/admin/variations/',
         variation_list, {}, 'satchmo_admin_variation_list'),

    path('brand/', include('satchmo.product.brand.urls')),
    path('<slug:category_slug>/<slug:brand_slug>/',
         brand_category_page, {}, name='satchmo_brand_category_view'),

    path('product/configurableproduct/<int:id>/getoptions/',
         get_configurable_product_options, {}, 'satchmo_admin_configurableproduct'),
    path('<slug:category_slug>/<slug:brand_slug>/<slug:product_slug>/',
         get_product, {}, 'satchmo_product'),
    path('<slug:category_slug>/<slug:brand_slug>/<slug:product_slug>/prices/',
         get_price, {}, 'satchmo_product_prices'),
    path('<slug:category_slug>/<slug:brand_slug>/<slug:product_slug>/price_detail/',
         get_price_detail, {}, 'satchmo_product_price_detail'),
    path('<slug:slug>/',
         category_view, {}, 'satchmo_category'),
    path('', category_index, {}, 'satchmo_category_index'),
]
