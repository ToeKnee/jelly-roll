from django import template

register = template.Library()


@register.inclusion_tag('shop/_order_details.html', takes_context=True)
def order_details(context, order, default_view_tax=False):
    """Output a formatted block giving order details."""
    context.update({
        'order': order,
        'default_view_tax': default_view_tax,
    })
    return context


@register.inclusion_tag('shop/_order_tracking_details.html', takes_context=True)
def order_tracking_details(context, order, paylink=False, default_view_tax=False):
    """Output a formatted block giving order tracking details."""
    context.update({
        'order': order,
        'default_view_tax': default_view_tax,
        'paylink': paylink,
    })
    return context
