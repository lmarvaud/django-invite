"""
forms

Created by leni on 14/04/2019
"""
from os.path import basename

from django.forms import ModelForm, BooleanField, ModelChoiceField
from django.utils.translation import gettext as _

from invite.models import Event
from invite.transitional_form import TransitionalForm

try:
    import magic
except ImportError:  # pragma: no cover
    magic = None


class AddToEventForm(TransitionalForm):
    """
    Transitional Form to add families to an event
    """
    event = ModelChoiceField(queryset=Event.objects.all(), required=True)


class FamilyInvitationForm(ModelForm):
    """Form to permit Family Invitation to be sent"""
    send_mail = BooleanField(label=_('Send the mail'), required=False)


class JoinedDocumentForm(ModelForm):
    """Form to set joined document default name and mimetype"""

    def clean_name(self):
        """Set the file default name"""
        if 'name' in self.cleaned_data and self.cleaned_data['name']:
            return self.cleaned_data['name']
        data = self.cleaned_data
        field = self.fields['name']
        value = field.clean(basename(data['document'].name) if 'document' in data else None)
        return value

    def clean(self):
        """Retrieve the mimetype from the file"""
        cleaned_data = super(JoinedDocumentForm, self).clean()
        if 'document' in self.files:
            if magic:
                mime = magic.Magic(mime=True)
                cleaned_data['mimetype'] = mime.from_buffer(cleaned_data['document'].file.read())
            else:
                cleaned_data['mimetype'] = cleaned_data['document'].content_type
        return cleaned_data

    def _post_clean(self):
        """Set the mimetype in the form instance"""
        super(JoinedDocumentForm, self)._post_clean()
        if 'mimetype' in self.cleaned_data:
            self.instance.mimetype = self.cleaned_data['mimetype']
