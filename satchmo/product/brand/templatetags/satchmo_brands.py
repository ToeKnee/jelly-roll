"""Tags for manipulating brands on templates."""

from django.core.cache import cache
from django.template import Library
from django.template import Node
from satchmo.product.brand.models import Brand

register = Library()

class BrandListNode(Node):
    """Template Node tag which pushes the brand list into the context"""
    def __init__(self, var, nodelist):
        self.var = var
        self.nodelist = nodelist

    def render(self, context):
        brands = Brand.objects.active()
        context[self.var] = brands
        context.push()
        context[self.var] = brands
        output = self.nodelist.render(context)
        context.pop()
        return output            
            
def do_brandlistnode(parser, token):
    """Push the brand list into the context using the given variable name.

    Sample usage::

        {% brand_list as var %}
        
    """
    args = token.split_contents()
    if len(args) != 3:
        raise template.TemplateSyntaxError("%r tag expecting '[slug] as varname', got: %s" % (args[0], args))
    
    var = args[2]
    nodelist = parser.parse(('endbrand_list',))
    parser.delete_first_token()
    return BrandListNode(var, nodelist)

register.tag('brand_list', do_brandlistnode)

@register.inclusion_tag('brand_tree.html')
def brand_tree(category=None):
    """
    Creates an unordered list of the brands.

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
    key = 'shop_tree_%s' % category.slug
    if cache.get(key):
        brands = cache.get(key)
    else:
        if category:
            brands = Brand.objects.filter(categories__slug=category.slug)
        else:
            brands = Brand.objects.all()
        cache.set(key, brands, 86000)
    return {"brands": brands, "category": category.slug}
