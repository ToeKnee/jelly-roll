import logging

from django.core.cache import cache
from django.template import Library
from django.template import Node

from satchmo.product.models import Category
from satchmo.shop.templatetags import get_filter_args
log = logging.getLogger(__name__)
try:
    from xml.etree.ElementTree import Element, SubElement, tostring
except ImportError:
    from elementtree.ElementTree import Element, SubElement, tostring

register = Library()


@register.inclusion_tag('category_tree.html')
def category_tree(id=None):
    """
    Creates an unordered list of the categories.

    Example::

        <ul>
            <li>Books
                <ul>
                <li>Science Fiction
                    <ul>
                    <li>Space stories</li>
                    <li>Robot stories</li>
                    </ul>
                </li>
                <li>Non-fiction</li>
                </ul>
        </ul>
    """
    key = 'category_tree_%s' % id
    if cache.get(key):
        categories = cache.get(key)
    else:
        if id:
            categories = Category.objects.filter(parent__id=id)
        else:
            categories = Category.objects.root_categories()
        cache.set(key, categories, 86400)
    return {"categories": categories}


class CategoryListNode(Node):
    """Template Node tag which pushes the category list into the context"""

    def __init__(self, slug, var, nodelist):
        self.var = var
        self.slug = slug
        self.nodelist = nodelist

    def render(self, context):

        if self.slug:
            try:
                cat = Category.objects.get(slug__iexact=self.slug)
                cats = cat.child.all()
            except Category.DoesNotExist:
                log.warn("No category found for slug: %s", slug)
                cats = []

        else:
            cats = Category.objects.root_categories()

        context[self.var] = cats

        context.push()
        context[self.var] = cats
        output = self.nodelist.render(context)
        context.pop()
        return output


def do_categorylistnode(parser, token):
    """Push the category list into the context using the given variable name.

    Sample usage::

        {% category_list slug as var %}
        or
        {% category_list as var %}


    """
    args = token.split_contents()
    ct = len(args)
    if not ct in (3, 4):
        raise template.TemplateSyntaxError(
            "%r tag expecting '[slug] as varname', got: %s" % (args[0], args))

    if ct == 3:
        slug = None
        var = args[2]
    else:
        slug = args[1]
        var = args[3]

    nodelist = parser.parse(('endcategory_list',))
    parser.delete_first_token()

    return CategoryListNode(slug, var, nodelist)


register.tag('category_list', do_categorylistnode)


def product_category_siblings(product, args=""):
    args, kwargs = get_filter_args(args,
                                   keywords=('variations', 'include_self'),
                                   boolargs=('variations', 'include_self'),
                                   stripquotes=True)

    sibs = product.get_category.product_set.all().order_by('ordering', 'name')
    if not kwargs.get('variations', True):
        sibs = [sib for sib in sibs if not sib.has_variants]

    if not kwargs.get('include_self', True):
        sibs = [sib for sib in sibs if not sib == product]

    return sibs


register.filter('product_category_siblings', product_category_siblings)
