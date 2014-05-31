from django.conf.urls.defaults import include, patterns, url

urlpatterns = patterns(
    'satchmo.product.filterviews',

    (r'^product/view/recent/$',
        'display_recent', {}, 'satchmo_product_recently_added'),
    (r'^product/view/bestsellers/$',
        'display_bestsellers', {}, 'satchmo_product_best_selling'),
)

urlpatterns += patterns(
    'satchmo.product.adminviews',

    (r'^product/inventory/edit/$',
        'edit_inventory', {}, 'satchmo_admin_edit_inventory'),
    (r'^order/picking-list/$',
        'picking_list', {}, 'satchmo_admin_picking_list'),
    (r'^product/inventory/export/$',
        'export_products', {}, 'satchmo_admin_product_export'),
    (r'^product/inventory/import/$',
        'import_products', {}, 'satchmo_admin_product_import'),
    (r'^product/inventory/report/$',
        'product_active_report', {}, 'satchmo_admin_product_report'),
    (r'^product/admin/(?P<product_slug>[-\w]+)/variations/$',
        'variation_manager', {}, 'satchmo_admin_variation_manager'),
    (r'^product/admin/variations/$',
        'variation_list', {}, 'satchmo_admin_variation_list'),
)


# Brand category
urlpatterns += patterns(
    'satchmo.product.brand.views',

    (r'^brand/', include('satchmo.product.brand.urls')),

    url(r'^(?P<category_slug>[-\w0-9]+)/(?P<brand_slug>[a-z0-9-]+)/$',
        'brand_category_page', {}, name='satchmo_brand_category_view'),
)


# Products and Categories
urlpatterns += patterns(
    'satchmo.product.views',
    (r"^product/configurableproduct/(?P<id>\d+)/getoptions/",
        'get_configurable_product_options', {}, 'satchmo_admin_configurableproduct'),
    (r'^(?P<category_slug>[-\w0-9]+)/(?P<brand_slug>[a-z0-9-]+)/(?P<product_slug>[-\w]+)/$',
        'get_product', {}, 'satchmo_product'),
    (r'^(?P<category_slug>[-\w0-9]+)/(?P<brand_slug>[a-z0-9-]+)/(?P<product_slug>[-\w]+)/prices/$',
        'get_price', {}, 'satchmo_product_prices'),
    (r'^(?P<category_slug>[-\w0-9]+)/(?P<brand_slug>[a-z0-9-]+)/(?P<product_slug>[-\w]+)/price_detail/$',
        'get_price_detail', {}, 'satchmo_product_price_detail'),
    (r'^(?P<slug>[-\w]+)/$',
        'category_view', {}, 'satchmo_category'),
    (r'^$', 'category_index', {}, 'satchmo_category_index'),
)
