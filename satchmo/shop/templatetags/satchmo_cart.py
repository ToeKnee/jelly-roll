from django import template
from satchmo.configuration import config_value
from satchmo.currency.utils import (
    currency_for_request,
    money_format,
)
from satchmo.tax.templatetags.satchmo_tax import CartitemLineTaxedTotalNode, CartTaxedTotalNode

import logging
log = logging.getLogger(__name__)

register = template.Library()


class CartitemTotalNode(template.Node):
    """Show the total for the cartitem"""

    def __init__(self, cartitem, show_currency, show_tax):
        self.cartitem = template.Variable(cartitem)
        self.raw_cartitem = cartitem
        self.show_currency = template.Variable(show_currency)
        self.raw_currency = show_currency
        self.show_tax = template.Variable(show_tax)
        self.raw_tax = show_tax

    def render(self, context):

        try:
            show_tax = self.show_tax.resolve(context)
        except template.VariableDoesNotExist:
            show_tax = self.raw_tax

        if show_tax:
            tag = CartitemLineTaxedTotalNode(
                self.raw_cartitem, self.raw_currency)
            return tag.render(context)

        try:
            cartitem = self.cartitem.resolve(context)
        except template.VariableDoesNotExist:
            log.warn('Could not resolve template variable: %s', self.cartitem)
            return ''

        try:
            show_currency = self.show_currency.resolve(context)
        except template.VariableDoesNotExist:
            show_currency = self.raw_currency

        if show_currency:
            request = context.get("request")
            currency_code = currency_for_request(request)
            return money_format(cartitem.line_total, currency_code)
        else:
            return cartitem.line_total


@register.inclusion_tag("product/cart_detail_customproduct.html", takes_context=True)
def cartitem_custom_details(context, cartitem):
    is_custom = "CustomProduct" in cartitem.product.get_subtypes()

    return {
        'cartitem': cartitem,
        'is_custom': is_custom
    }


@register.inclusion_tag("product/cart_detail_subscriptionproduct.html", takes_context=True)
def cartitem_subscription_details(context, cartitem):
    log.debug('sub details')
    return {
        'cartitem': cartitem,
        'is_subscription': cartitem.product.is_subscription
    }


def cartitem_total(parser, token):
    """Returns the line total for the cartitem, possibly with tax added.  If currency evaluates true,
    then return the total formatted through money_format.

    Example::

        {% cartitem_total cartitem [show_tax] [currency] %}
    """

    tokens = token.contents.split()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError("'%s' tag requires a cartitem argument" % tokens[
            0])

    cartitem = tokens[1]

    if len(tokens) > 2:
        show_tax = tokens[2]
    else:
        show_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if len(tokens) > 3:
        show_currency = tokens[3]
    else:
        show_currency = 'True'

    return CartitemTotalNode(cartitem, show_currency, show_tax)


class CartTotalNode(template.Node):
    """Show the total for the cart"""

    def __init__(self, cart, show_currency, show_tax):
        self.cart = template.Variable(cart)
        self.raw_cart = cart
        self.show_currency = template.Variable(show_currency)
        self.raw_currency = show_currency
        self.show_tax = template.Variable(show_tax)
        self.raw_tax = show_tax

    def render(self, context):

        try:
            show_tax = self.show_tax.resolve(context)
        except template.VariableDoesNotExist:
            show_tax = self.raw_tax

        if show_tax:
            tag = CartTaxedTotalNode(self.raw_cart, self.raw_currency)
            return tag.render(context)

        try:
            cart = self.cart.resolve(context)
        except template.VariableDoesNotExist:
            log.warn('Could not resolve template variable: %s', self.cart)
            return ''

        try:
            show_currency = self.show_currency.resolve(context)
        except template.VariableDoesNotExist:
            show_currency = self.raw_currency

        if show_currency:
            request = context.get("request")
            currency_code = currency_for_request(request)
            return money_format(cart.total, currency_code)
        else:
            return cart.total


@register.tag()
def cart_total(parser, token):
    """Returns the total for the cart, possibly with tax added.  If currency evaluates true,
    then return the total formatted through money_format.

    Example::

        {% cart_total cart [show_tax] [currency] %}
    """

    tokens = token.contents.split()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError("'%s' tag requires a cart argument" % tokens[0])

    cart = tokens[1]

    if len(tokens) > 2:
        show_tax = tokens[2]
    else:
        show_tax = config_value('TAX', 'DEFAULT_VIEW_TAX')

    if len(tokens) > 3:
        show_currency = tokens[3]
    else:
        show_currency = 'True'

    return CartTotalNode(cart, show_currency, show_tax)
