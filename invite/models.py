"""
Data models configurations of django-invite project
"""
from django.db import models

__all__ = ["Family", "Invite", "Accompany"]


class Family(models.Model):
    """
    Representation of a group of linked person

    The invites while receive a mail
    The accompanies can be useful to personalize the e-mail

    In the current version the family can be invited distinctly to 3 parts of the event according to
    those boolean : invited_midday, invited_afternoon and invited_evening
    """
    invited_midday = models.BooleanField(default=False)
    invited_afternoon = models.BooleanField(default=False)
    invited_evening = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"


class Invite(models.Model):
    """
    Guest of the event

    A personalized email will be send to him/them
    """
    family = models.ForeignKey(Family, models.CASCADE, "invites", null=False)
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
