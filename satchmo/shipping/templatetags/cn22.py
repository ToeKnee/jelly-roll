from decimal import Decimal
from django import template

register = template.Library()


@register.inclusion_tag('cn22.html')
def cn22(order, group_by_category=True):
    """Generate a CN22 form for customs usage

    If group_by_category is True (default), it will group the items by
    category to reduce size of form
    """

    items = order.orderitem_set.all()
    items_dict = {}
    total_weight = 0
    total_value = Decimal("0.00")
    for item in items:
        if group_by_category:
            name = str(item.category)
        else:
            name = str(item)

        if name not in items_dict:
            items_dict[name] = {
                "name": name,
                "quantity": item.quantity,
                "weight": item.weight,
                "value": item.line_item_price
            }
        else:
            items_dict[name]["quantity"] += item.quantity
            items_dict[name]["weight"] += item.weight
            items_dict[name]["value"] += item.line_item_price

        # Update the totals for the table footer
        total_weight += item.weight
        total_value += item.line_item_price

    return {
        "order": order,
        "items": list(items_dict.values()),
        "total_weight": total_weight,
        "total_value": total_value
    }
