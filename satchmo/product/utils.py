from satchmo.currency.utils import (
    currency_for_request,
    money_format,
)
from satchmo.product.models import (
    Option,
    OptionGroup,
    ProductPriceLookup,
    split_option_unique_id,
)
from satchmo.shop.models import Config
from satchmo.tax.utils import get_tax_processor

import logging
log = logging.getLogger(__name__)


def get_taxprocessor(user):
    if user.is_authenticated:
        user = user
    else:
        user = None

    return get_tax_processor(user=user)


def get_tax(user, product, quantity):
    taxer = get_taxprocessor(user)
    return taxer.by_product(product, quantity)


def productvariation_details(product, include_tax, user, request, create=False):
    """Build the product variation details, for conversion to javascript.

    Returns variation detail dictionary built like so:
    details = {
        "OPTION_KEY" : {
            "SLUG": "Variation Slug",
            "PRICE" : {"qty" : "$price", [...]},
            "TAXED" : "$taxed price",   # omitted if no taxed price requested
            "QTY" : 1
        },
        [...]
    }
    """

    config = Config.objects.get_current()
    ignore_stock = config.no_stock_checkout

    if include_tax:
        taxer = get_taxprocessor(user)
        tax_class = product.taxClass

    details = {}

    variations = ProductPriceLookup.objects.filter(parentid=product.id)
    if variations.count() == 0:
        if create:
            log.debug('Creating price lookup for %s', product)
            ProductPriceLookup.objects.smart_create_for_product(product)
            variations = ProductPriceLookup.objects.filter(parentid=product.id)
        else:
            log.warning(
                'You must run satchmo_rebuild_pricing and add it to a cron-job to run every day, or else the product details will not work for product detail pages.')
    for detl in variations:
        key = detl.key
        if key in details:
            detail = details[key]
        else:
            detail = {}
            detail['SLUG'] = detl.productslug

            if not detl.active:
                qty = -1
            elif ignore_stock:
                qty = 10000
            else:
                qty = detl.items_in_stock

            detail['QTY'] = qty

            detail['PRICE'] = {}
            if include_tax:
                detail['TAXED'] = {}

            details[key] = detail

        price = detl.dynamic_price
        currency_code = currency_for_request(request)

        detail['PRICE'][detl.quantity] = money_format(price, currency_code)

        if include_tax:
            tax_price = taxer.by_price(tax_class, price) + price
            detail['TAXED'][detl.quantity] = money_format(tax_price, currency_code)

    return details


def serialize_options(product, selected_options=()):
    """
    Return a list of optiongroups and options for display to the customer.
    Only returns options that are actually used by members of this product.

    Return Value:
    [
    {
    name: 'group name',
    id: 'group id',
    items: [{
        name: 'opt name',
        value: 'opt value',
        price_change: 'opt price',
        selected: False,
        },{..}]
    },
    {..}
    ]

    Note: This doesn't handle the case where you have multiple options and
    some combinations aren't available. For example, you have option_groups
    color and size, and you have a yellow/large, a yellow/small, and a
    white/small, but you have no white/large - the customer will still see
    the options white and large.
    """
    all_options = product.get_valid_options()
    group_sortmap = OptionGroup.objects.get_sortmap()

    # First get all objects.
    # Right now we only have a list of option.unique_ids, and there are
    # probably a lot of dupes, so first list them uniquely.
    vals = {}
    groups = {}
    opts = {}
    for options in all_options:
        for option in options:
            if option not in opts:
                k, v = split_option_unique_id(option)
                vals[v] = False
                groups[k] = False
                opts[option] = None

    for option in Option.objects.filter(option_group__id__in=list(groups.keys()), value__in=list(vals.keys())):
        uid = option.unique_id
        if uid in opts:
            opts[uid] = option

    # now we have all the objects in our "opts" dictionary, so build the serialization dict

    serialized = {}

    for option in list(opts.values()):
        if option.option_group_id not in serialized:
            serialized[option.option_group.id] = {
                'name': option.option_group.translated_name(),
                'id': option.option_group.id,
                'items': [],
            }
        if option not in serialized[option.option_group_id]['items']:
            serialized[option.option_group_id]['items'] += [option]
            option.selected = option.unique_id in selected_options

    # first sort the option groups
    values = []
    for k, v in list(serialized.items()):
        values.append((group_sortmap[k], v))

    values.sort()
    values = list(zip(*values))[1]

    log.debug('serialized: %s', values)

    # Now go back and make sure option items are sorted properly.
    for v in values:
        v['items'] = _sort_options(v['items'])

    log.debug('Serialized Options %s: %s', product.product.slug, values)
    return values


def _sort_options(lst):
    work = sorted([(opt.sort_order, opt) for opt in lst])
    return list(zip(*work))[1]
