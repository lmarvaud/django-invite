"""
Data models configurations of django-invite project
"""
from django.db import models
from django.db.models import Sum
from django.template.defaultfilters import capfirst
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .join_and import join_and

__all__ = ["Family", "Guest", "Accompany"]


class Family(models.Model):
    """
    Representation of a group of linked person

    The invites while receive a mail
    The accompanies can be useful to personalize the e-mail

    In the current version the family can be invited distinctly to 3 parts of the event according to
    those boolean : invited_midday, invited_afternoon and invited_evening
    """
    objects = models.Manager()

    invited_midday = models.BooleanField(verbose_name=_("is invite on lunch"), default=False)
    invited_afternoon = models.BooleanField(verbose_name=_("is invite the afternoon"),
                                            default=False)
    invited_evening = models.BooleanField(verbose_name=_("is invite at the party"), default=True)
    host = models.CharField(verbose_name=_("principal host"), max_length=32)

    @cached_property
    def context(self):
        """
        Create a template context for french language
        """
        many = self.guests.count() > 1
        is_female = self.guests.exclude(female=True).count() > 0
        guests = join_and(list(self.guests.values_list("name", flat=True)))
        accompanies = join_and(list(self.accompanies.values_list("name", flat=True)))
        accompanies_number = self.accompanies.aggregate(Sum("number"))
        accompanies_number = accompanies_number["number__sum"] or 0
        has_accompany = accompanies_number >= 1
        has_accompanies = accompanies_number > 1
        context = {
            "family": self,
            "full": join_and(list(self.guests.values_list("name", flat=True)) +
                             list(self.accompanies.values_list("name", flat=True))),
            "prenom": guests,
            "Françoise": guests,
            "invités": guests,
            "has_accompanies": has_accompanies,
            "has_accompany": has_accompany,
            "tu": "tu" if not many else "vous",
            "vas": "vas" if not many else "allez",
            "es": "es" if not many else "êtes",
            "sais": "sais" if not  many else "savez",
            "e": ("e" if is_female else "") + ("s" if many else ""),
            "avec": "avec" if has_accompany else "",
            "accompagnant": accompanies if has_accompany else "",
            "Marie": accompanies if has_accompany else "",
            "est": "sont" if has_accompanies else ("est" if has_accompany else ""),
        }
        for key in list(context.keys()):
            if isinstance(context[key], str):
                context.setdefault(capfirst(key), capfirst(context[key]))
        return context

    def __str__(self):
        return str(_("{:full} family")).format(self)

    def __format__(self, format_spec):
        """
        acceptable format_spec are [guests, accompanies, full]


        :param format_spec:
        :return:
        """

        if format_spec not in self.context:
            raise ValueError("Invalid format specifier")
        return ('{%s}' % format_spec).format(**self.context)

    class Meta:
        verbose_name = _("family")
        verbose_name_plural = _("families")


class Guest(models.Model):
    """
    Guest of the event

    A personalized email will be send to him/her/them
    """
    family = models.ForeignKey(Family, models.CASCADE, "guests", verbose_name=_("family"),
                               null=False)
    female = models.BooleanField(verbose_name=_("is a female"), default=False)
    name = models.CharField(verbose_name=_("name"), max_length=64)
    email = models.EmailField(verbose_name=_("email address"))
    phone = models.CharField(verbose_name=_("phone number"), max_length=20, blank=True, default="")

    def __str__(self):
        return "{name} <{email}>".format(name=self.name, email=self.email)

    class Meta:
        verbose_name = _("Guest")


class Accompany(models.Model):
    """
    Guest accompanies are usually some children/friends/..

    `number` field permit to join accompanies in on field, for "your children" for example
    """
    family = models.ForeignKey(Family, models.CASCADE, "accompanies", verbose_name=_("family"),
                               null=False)
    name = models.CharField(verbose_name=_("name"), max_length=64)
    number = models.IntegerField(verbose_name=_("number of person"), default=1)

    def __str__(self):
        return "{name}".format(name=self.name)

    class Meta:
        verbose_name = _("accompany")
