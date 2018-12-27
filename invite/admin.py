"""
Admin configurations for django-invite project
"""
from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .models import Family, Guest, Accompany, Event
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


class FamilyInvitationInline(admin.TabularInline):
    """
    Invitation families admin view
    """
    autocomplete_fields = ("family", "event")
    model = Event.families.through
    readonly_fields = ('show_mail',)

    @staticmethod
    def show_mail(instance):
        """
        Extra field adding a link to preview the email
        """
        if instance.pk:
            url = reverse('show_mail', kwargs={"family_id": instance.family_id})
            return format_html(u'<a href="{}">{}</a>'.format(url, _("Preview the mail")))
        return ""


@admin.register(Family, site=admin.site)
class FamilyAdmin(admin.ModelAdmin):
    """
    Family admin view
    """
    inlines = [InviteInline, AccompanyInline, FamilyInvitationInline]
    search_fields = ("guests__name", "accompanies__name")


@admin.register(Event, site=admin.site)
class EventAdmin(admin.ModelAdmin):
    """
    Event admin view
    """
    exclude = ('families', )
    inlines = [FamilyInvitationInline]
    actions = ["send_mail"]
    search_fields = ("name", "date")

    def send_mail(self, request, invitations):
        """
        Email action, send the email to the guest

        :param unused_model_admin: the admin.ModelAdmin
        :param unused_request: the admin request
        :param families: the list of the selected families to send the mail to
        :return:
        """
        to_send = (
            (
                render_to_string("invite/subject.txt", context=invitation.context(family)),
                render_to_string("invite/mail.txt", context=invitation.context(family)),
                render_to_string("invite/mail.html", context=invitation.context(family)),
                "{} <{}>".format(family.host, settings.INVITE_HOSTS[family.host])
                if settings.__dict__.get("INVITE_USE_HOST_IN_FROM_EMAIL", False) and
                family.host in settings.INVITE_HOSTS
                else None,
                (
                    "{} <{}>".format(*values)
                    for values in family.guests.values_list("name", "email")
                    if all(values)
                )
            )
            for invitation in invitations
            for family in invitation.families.all()
        )
        result = send_mass_html_mail(
            to_send,
            reply_to=["{host} <{email}>".format(host=host, email=settings.INVITE_HOSTS[host])
                      for host in settings.INVITE_HOSTS]
        )
        self.message_user(request, _("%(result)d messages send") % {"result": result})
    send_mail.short_description = _("Send the email")
