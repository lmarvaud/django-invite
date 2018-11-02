"""
Admin configurations for django-invite project
"""
from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .models import Family, Guest, Accompany
from .send_mass_html_mail import send_mass_html_mail


class InviteInline(admin.TabularInline):
    """
    Family guest admin view
    """
    model = Guest


class AccompanyInline(admin.TabularInline):
    """
    Family accompanies admin view
    """
    model = Accompany


def mail(unused_model_admin, unused_request, families):
    """
    Email action, send the email to the guest

    :param unused_model_admin: the admin.ModelAdmin
    :param unused_request: the admin request
    :param families: the list of the selected families to send the mail to
    :return:
    """
    to_send = (
        (
            render_to_string("invite/subject.txt", context=family.context),
            render_to_string("invite/mail.txt", context=family.context),
            render_to_string("invite/mail.html", context=family.context),
            "{} <{}>".format(family.host, settings.INVITE_HOSTS[family.host])
            if settings.__dict__.get("INVITE_USE_HOST_IN_FROM_EMAIL", False) and
            family.host in settings.INVITE_HOSTS
            else None,
            family.guests.values_list("email", flat=True)
        )
        for family in families
    )
    send_mass_html_mail(
        to_send,
        reply_to=["{host} <{email}>".format(host=host, email=settings.INVITE_HOSTS[host])
                  for host in settings.INVITE_HOSTS]
    )
mail.short_description = _("Send the email")


@admin.register(Family, site=admin.site)
class FamilyAdmin(admin.ModelAdmin):
    """
    Family admin view
    """
    inlines = [InviteInline, AccompanyInline]
    actions = [mail]
