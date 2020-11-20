from django import template
from functools import reduce

from ..utils.link import Link


register = template.Library()


@register.inclusion_tag("tags/breadcrumbs.html")
def breadcrumbs(links):
    if isinstance(links, list) or isinstance(links, tuple):
        if reduce(lambda a, b: a & isinstance(b, Link), links, True):
            return {
                "links": links,
            }
        else:
            raise TypeError("The sequence should only contain Link instances")
    else:
        raise TypeError("The sequence must be a list or a tuple")
