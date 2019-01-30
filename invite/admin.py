"""
Admin configurations for django-invite project
"""
from django.conf import settings
from django.contrib import admin, messages
from django.forms import BooleanField, ModelForm
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .models import Family, Guest, Accompany, Event
from .send_mass_html_mail import send_mass_html_mail


class InviteInline(admin.TabularInline):
    """Family guest admin view"""
    model = Guest


class AccompanyInline(admin.TabularInline):
    """Family accompanies admin view"""
    model = Accompany


class FamilyInvitationForm(ModelForm):
    """Form to permit Family Invitation to be sent"""
    send_mail = BooleanField(label=_('Send the mail'), required=False)


class FamilyInvitationInline(admin.TabularInline):
    """Invitation families admin view"""
    autocomplete_fields = ("family", "event")
    model = Event.families.through
    readonly_fields = ('show_mail',)
    form = FamilyInvitationForm

    @staticmethod
    def show_mail(instance):
        """Extra field adding a link to preview the email"""
        if instance.pk:
            url = reverse('show_mail', kwargs={"family_id": instance.family_id})
            return format_html(u'<a href="{}">{}</a>'.format(url, _("Preview the mail")))
        return ""


class FamilyInvitationModelAdminMixin(admin.ModelAdmin):
    """
    Mixin model admin for family invitation management

    Inlines is preset to add FamilyInvitation Inline and saving it will send the email from the
    formset
    """
    inlines = [FamilyInvitationInline]

    def save_formset(self, request, form, formset, change):
        """Send FamilyInvitation mail after saving the formset"""
        super().save_formset(request, form, formset, change)
        if isinstance(form, FamilyInvitationForm):
            self._send_mail(request, formset)

    @staticmethod
    def _send_mail(request, formset):
        """Send the emails for a formset from a FamilyInvitationForm"""
        family_invitations = {(data['family'], data['event'])
                              for data in formset.cleaned_data
                              if data and data["send_mail"]}
        if family_invitations:
            to_send = (
                event.gen_mass_email(family)
                for family, event in family_invitations
            )
            send_result = send_mass_html_mail(
                to_send,
                reply_to=["{host} <{email}>".format(host=host, email=settings.INVITE_HOSTS[host])
                          for host in settings.INVITE_HOSTS]
            )
            messages.add_message(request, messages.INFO,
                                 _("%(result)d messages send") % {"result": send_result})


@admin.register(Family, site=admin.site)
class FamilyAdmin(FamilyInvitationModelAdminMixin):
    """
    Family admin view

    This view use FamilyInvitationInline to send an initation to a selection of guests
    """
    inlines = [InviteInline, AccompanyInline] + FamilyInvitationModelAdminMixin.inlines
    search_fields = ("guests__name", "accompanies__name")


@admin.register(Event, site=admin.site)
class EventAdmin(FamilyInvitationModelAdminMixin):
    """
    Event admin view

    This view use FamilyInvitationInline to send an initation to a selection of guests
    """
    exclude = ('families', )
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
            invitation.gen_mass_email(family, request=request)
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
