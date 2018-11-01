"""
Data models configurations of django-invite project
"""
from operator import attrgetter

from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

__all__ = ["Family", "Invite", "Accompany"]


def join_and(queryset):
    """
    Create a "," and "and" sentence from Invite or Accompany list

    :param queryset: a queryset with a list of Invite or Accompany
    :return: the list of name join by "," and "and"

    for example,
    ```
    join_and([Invite(name="Jean"), Invite(name="Paul"), Invite(name="Marie")])
    ```
    would return : "Jean, Paul and Marie"
    (where " and " is localized)
    """
    listed = list(map(str, map(attrgetter('name'), queryset)))
    if not listed:
        return ''
    if len(listed) == 1:
        return listed[0]
    if len(listed) == 2:
        return listed[0] + str(_(' and ')) + listed[1]
    return ', '.join(listed[:-1]) + str(_(' and ')) + listed[-1]


class Family(models.Model):
    """
    Representation of a group of linked person

    The invites while receive a mail
    The accompanies can be useful to personalize the e-mail

    In the current version the family can be invited distinctly to 3 parts of the event according to
    those boolean : invited_midday, invited_afternoon and invited_evening
    """
    objects = models.Manager()

    invited_midday = models.BooleanField(default=False)
    invited_afternoon = models.BooleanField(default=False)
    invited_evening = models.BooleanField(default=True)

    @property
    def context(self):
        """
        Create a template context for french language
        """
        many = self.invites.count() > 1
        female = self.invites.exclude(female=True).count() > 0
        number = self.accompanies.aggregate(Sum("number"))
        number = number["number__sum"]
        has_accompanies = number > 1
        has_accompany = number >= 1
        return {
            "prenom": join_and(self.invites.all()),
            "has_accompanies": has_accompanies,
            "has_accompany": has_accompany,
            "tu": "tu" if not many else "vous",
            "vas": "vas" if not many else "allez",
            "es": "es" if not many else "êtes",
            "e": ("e" if female else "") + ("s" if many else ""),
            "avec": "avec "
        }

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"


class Invite(models.Model):
    """
    Guest of the event

    A personalized email will be send to him/her/them
    """
    family = models.ForeignKey(Family, models.CASCADE, "invites", null=False)
    female = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    email = models.EmailField()
    phone = models.CharField(max_length=20)


class Accompany(models.Model):
    """
    Guest accompanies are usually some children/friends/..

    `number` field permit to join accompanies in on field, for "your children" for example
    """
    family = models.ForeignKey(Family, models.CASCADE, "accompanies", null=False)
    name = models.CharField(max_length=64)
    number = models.IntegerField(default=1)
