"""
join_and utils
"""
from django.utils.translation import ugettext_lazy as _


def join_and(listed):
    """
    Create a "," and "and" sentence from a list of string

    :param listed: the list string to join with comma and "and"
    :return: the list join by "," and "and"

    for example,
    ```
    join_and(["Jean", "Paul", "Marie"])
    ```
    would return : "Jean, Paul and Marie"
    (where "and" is localized)
    """
    if not listed:
        return ''
    if len(listed) == 1:
        return str(listed[0])
    localized_and = ' ' + str(_('and')) + ' '
    if len(listed) == 2:
        return str(listed[0]) + localized_and + str(listed[1])
    return ', '.join(listed[:-1]) + localized_and + str(listed[-1])
