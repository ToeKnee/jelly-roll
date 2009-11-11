try:
    from decimal import Decimal
except:
    from django.utils._decimal import Decimal
from django.core import urlresolvers
from django.core.cache import cache
from django.template import Library
from django.template import Node
import logging
from satchmo.discount.utils import calc_by_percentage
from satchmo.product.brand.models import Brand
from satchmo.product.models import Category
from satchmo.product.queries import bestsellers
from satchmo.shop.templatetags import get_filter_args

log = logging.getLogger('shop.templatetags')

try:
    from xml.etree.ElementTree import Element, SubElement, tostring
except ImportError:
    from elementtree.ElementTree import Element, SubElement, tostring

register = Library()

def recurse_for_children(current_node, parent_node, active_cat, show_empty=False):
    child_count = len(current_node.get_active_children())

    if show_empty or child_count > 0 or current_node.active_products().count():
        temp_parent = SubElement(parent_node, 'li')
        if child_count == 1:
            attrs = {'href': current_node.get_active_children()[0].get_absolute_url()}
        else:
            attrs = {'href': current_node.get_absolute_url()}
        if current_node == active_cat:
            attrs["class"] = "current"
        link = SubElement(temp_parent, 'a', attrs)
        link.text = current_node.translated_name()

        if child_count > 0:
            new_parent = SubElement(temp_parent, 'ul')
            children = current_node.child.all()
            for child in children:
                recurse_for_children(child, new_parent, active_cat)
        else:
            brands = Brand.objects.filter(categories__slug=current_node.slug)
            if brands.count() > 0:
                brand_node = SubElement(temp_parent, 'ul')
                for brand in brands:
                    if  brand.active_products().count():
                        temp_parent = SubElement(brand_node, 'li')
                        url = urlresolvers.reverse('satchmo_brand_category_view', kwargs={'brandname' : brand.slug, 'catname' : current_node.slug})
                        attrs = {'href': url}
                        if brand == active_cat:
                            attrs["class"] = "current"
                        link = SubElement(temp_parent, 'a', attrs)
                        link.text = brand.translation.name

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
    key = 'shop_tree_%s' % id
    if cache.get(key):
        tree = cache.get(key)
    else:
        active_cat = None
        if id:
            active_cat = Category.objects.get(id=id)
        root = Element("ul")
        for cats in Category.objects.root_categories():
            if cats.active_products() or cats.get_active_children():
                recurse_for_children(cats, root, active_cat)
        tree = tostring(root, 'utf-8')
        cache.set(key, tree, 86000)
    return tree

register.simple_tag(category_tree)

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
    if not ct in (3,4):
        raise template.TemplateSyntaxError("%r tag expecting '[slug] as varname', got: %s" % (args[0], args))

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

