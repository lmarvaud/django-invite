"""
invite_extras

Created by leni on 17/03/2019
"""
import operator
from django import template
from ..join_and import join_and

register = template.Library()  # pylint: disable=invalid-name


@register.filter
def attrgetter(iter1, attr):
    """
    additional template tag filter to get attr in a list of object

    example:
        {{ value | itemgetter:"email" }}

    If **value** contains the list `[<User test@example.com>, <User test2@example.com>]`, the result
    will be `["test@example.com", "test2@example.com"]`
    """
    return list(map(operator.attrgetter(attr), iter1))


@register.filter
def itemgetter(iter1, item):
    """
    additional template tag filter to get item in a list of dict or list

    example:
        {{ value | itemgetter:1 }}

    If **value** contains the list `[["a", "b"], ["c", "d"]]`, the result will be `["b", "d"]`
    """
    return list(map(operator.itemgetter(item), iter1))


@register.filter(name='join_and')
def join_and_filter(lst):
    """
    additional template tag to concat a list with commas (", ") and a "and" operator (" and ")

    example:
        {{ value | join_and }}

    If **value** contains the list `["a", "b", "c"]`, the result will be `"a, b and c"` (where "and'
    is localized)
    """
    return join_and(lst)
