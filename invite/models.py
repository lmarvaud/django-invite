"""
Data models configurations of django-invite project

Created by lmarvaud on 03/11/2018
"""

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.template import Template
from django.template.context import make_context
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from .join_and import join_and

__all__ = ['Family', 'Guest', 'Accompany']


class Family(models.Model):
    """
    Representation of a group of linked person

    The invites while receive a mail
    The accompanies can be useful to personalize the e-mail

    In the current version the family can be invited distinctly to 3 parts of the event according to
    those boolean : invited_midday, invited_afternoon and invited_evening
    """
    objects = models.Manager()

    invited_midday = models.BooleanField(verbose_name=_('is invite on lunch'), default=False)
    invited_afternoon = models.BooleanField(verbose_name=_('is invite the afternoon'),
                                            default=False)
    invited_evening = models.BooleanField(verbose_name=_('is invite at the party'), default=True)
    host = models.CharField(verbose_name=_('principal host'), max_length=32)

    @cached_property
    def context(self):
        """
        Create a template context for french language
        """
        guests_count = self.guests.count()
        is_female = not self.guests.exclude(female=True).exists()
        accomanies_are_females = not self.accompanies.exclude(female=True).exists()
        guests = join_and(list(self.guests.values_list('name', flat=True)))
        accompanies = join_and(list(self.accompanies.values_list('name', flat=True)))
        accompanies_count = self.accompanies.aggregate(Sum('number'))
        accompanies_count = accompanies_count['number__sum'] or 0
        has_accompany = accompanies_count >= 1
        has_accompanies = accompanies_count > 1
        context = {
            'family': self,
            'all': join_and(list(self.guests.values_list('name', flat=True)) +
                            list(self.accompanies.values_list('name', flat=True))),
            'count': guests_count + accompanies_count,
            'accompanies': accompanies if accompanies_count else '',
            'accompanies_e': 'e' if accomanies_are_females else '',
            'accompanies_count': accompanies_count,
            'e': ('e' if is_female else ''),
            'guests': guests,
            'guests_count': guests_count,
            'has_accompanies': has_accompanies,
            'has_accompany': has_accompany,
            'is_female': is_female,
            'accompanies_are_female': accomanies_are_females,
        }
        return context

    def __str__(self):
        return str(_('%(all)s family') % {'all': self.context['all']})

    def __format__(self, format_spec):
        """
        acceptable format_spec are [guests, accompanies, full]


        :param format_spec:
        :return:
        """

        if format_spec not in self.context:
            raise ValueError('Invalid format specifier')
        return ('{%s}' % format_spec).format(**self.context)

    class Meta:
        verbose_name = _('family')
        verbose_name_plural = _('families')


class Guest(models.Model):
    """
    Guest of the event

    A personalized email will be send to him/her/them
    """
    family = models.ForeignKey(Family, models.CASCADE, 'guests', verbose_name=_('family'),
                               null=False)
    female = models.BooleanField(verbose_name=_('is a female'), default=False)
    name = models.CharField(verbose_name=_('name'), max_length=64)
    email = models.EmailField(verbose_name=_('email address'), blank=True, null=True)
    phone = models.CharField(verbose_name=_('phone number'), max_length=20, blank=True, default='')

    def __str__(self):
        return '{name} <{email}>'.format(name=self.name, email=self.email)

    class Meta:
        verbose_name = _('Guest')


class Accompany(models.Model):
    """
    Guest accompanies are usually some children/friends/..

    `number` field permit to join accompanies in on field, for "your children" for example
    """
    family = models.ForeignKey(Family, models.CASCADE, 'accompanies', verbose_name=_('family'),
                               null=False)
    female = models.BooleanField(verbose_name=_('is a female'), default=False)
    name = models.CharField(verbose_name=_('name'), max_length=64)
    number = models.IntegerField(verbose_name=_('number of person'), default=1)

    def __str__(self):
        return '{name}'.format(name=self.name)

    class Meta:
        verbose_name = _('accompany')


class Event(models.Model):
    """
    Invitation event
    """
    objects = models.Manager()

    name = models.CharField(verbose_name=_('name'), max_length=64, blank=True, null=True)
    date = models.DateField(verbose_name=_('date'), blank=True, null=True)
    families = models.ManyToManyField('Family', 'invitations', blank=True)

    def context(self, family):
        """
        Create a template context
        """
        context = family.context
        context.update({
            'event': self
        })
        return context

    def gen_mass_email(self, family, request=None):
        """
        Generate the mass mail tuple for one email

        see invite.send_mass_html_mail.send_mass_html_mail for more detail

        :param family: the family to send the event message to
        :param request: the request which initiated the generation
        :return: a tuple with the subject, the text message, the html message and the destinations
        email
        """
        context = self.context(family)
        assert self.has_mailtemplate, 'The event has no email template set'
        return (
            self.mailtemplate.render_subject(  # pylint: disable=no-member
                context=context, request=request),
            self.mailtemplate.render_text(  # pylint: disable=no-member
                context=context, request=request),
            self.mailtemplate.render_html(  # pylint: disable=no-member
                context=context, request=request),
            '{} <{}>'.format(family.host, settings.INVITE_HOSTS[family.host])
            if (getattr(settings, 'INVITE_USE_HOST_IN_FROM_EMAIL', False) and
                family.host in settings.INVITE_HOSTS)
            else None,
            (
                '{} <{}>'.format(*values)
                for values in family.guests.values_list('name', 'email')
                if all(values)
            ),
            (
                (joined_file.document.path, joined_file.name, joined_file.mimetype)
                for joined_file in self.mailtemplate.joined_documents.all()  # pylint: disable=no-member
            )
        )

    @property
    def has_mailtemplate(self) -> bool:
        """Determine wether the event has a mail template set or not yet"""
        try:
            getattr(self, 'mailtemplate')
        except Event.mailtemplate.RelatedObjectDoesNotExist:  # pylint: disable=no-member
            return False
        return True

    def __str__(self):
        if self.name and self.date:
            result = _('%(name)s of the %(date)s') % {'name': self.name, 'date': self.date}
        elif self.name:
            result = _('%(name)s') % {'name': self.name}
        elif self.date:
            result = _('event of the %(date)s') % {'date': self.date}
        else:
            result = '{pk}'.format(pk=self.pk)
        return result

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')


class JoinedDocument(models.Model):
    """Document to join to the mails"""
    objects = models.Manager()

    document = models.FileField(upload_to='joins')
    name = models.CharField(max_length=30, blank=True)
    mimetype = models.CharField(max_length=30, null=False)

    def __str__(self):
        return 'cid:%s' % self.name


class MailTemplate(models.Model):
    """Event mail template"""
    objects = models.Manager()

    subject = models.CharField(_('subject'), max_length=512, blank=True)
    text = models.TextField(_('raw content'), blank=True)
    html = models.TextField(_('html content'), blank=True)
    event = models.OneToOneField(Event, models.CASCADE)
    joined_documents = models.ManyToManyField(JoinedDocument, blank=True)

    @staticmethod
    def _render(template_string, context, request):
        """Render a template string"""
        context = make_context(context, request, autoescape=True)
        return Template(template_string).render(context)

    def render_subject(self, context, request):
        """Render the subject"""
        return self._render(self.subject, context, request)

    def render_text(self, context, request):
        """Render the text"""
        return self._render(self.text, context, request)

    def render_html(self, context, request):
        """Render the html"""
        return self._render(self.html, context, request)
