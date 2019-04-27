"""
test_admin

Created by lmarvaud on 03/11/2018
"""
import os
from collections import Iterable
from unittest.mock import patch, Mock

from datetime import date
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.shortcuts import reverse
from django.test import TestCase, override_settings

import invite.forms
from invite import admin
from invite.admin import JoinedDocumentAdmin
from invite.forms import JoinedDocumentForm
from invite.models import Family, Guest, Event, JoinedDocument
from invite.tests.common import TestEventMixin, TestMailTemplateMixin, MockRequest


class TestMail(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """Test admin mail action"""

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(INVITE_HOSTS={'Marie': 'test_send_mass_html_mail_reply_to@example.com'})
    def test_send_mass_html_mail_reply_to(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        self.assertEqual(send_mass_html_mail__mock.call_args[1]['reply_to'],
                         ['Marie <test_send_mass_html_mail_reply_to@example.com>'])

    @patch.object(admin, 'send_mass_html_mail')
    def test_send_mass_html_mail_to_send(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply to_send argument"""
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        self.assertIsInstance(send_mass_html_mail__mock.call_args[0], Iterable)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        expected_subject = 'Save the date'

        self.assertEqual(len(to_send), 1)
        to_send = list(to_send[0])
        self.assertEqual(len(to_send), 6)
        subject, text, html, from_email, recipient, join_attachment = to_send
        self.assertEqual(subject, expected_subject)
        self.assertEqual(text, self.expected_text)
        self.assertEqual(html, self.expected_html)
        self.assertIsNone(from_email)
        self.assertListEqual(list(recipient),
                             ['Françoise <valid@example.com>', 'Jean <valid@example.com>'])
        self.assertListEqual(list(join_attachment), [(self.joined_document.document.path,
                                                      'happy.png', 'image/png')])

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(
        INVITE_HOSTS={'Marie': 'test_using_invite_use_host_in_from_email@example.com'},
        INVITE_USE_HOST_IN_FROM_EMAIL=True
    )
    def test_using_invite_use_host_in_from_email(self, send_mass_html_mail__mock: Mock):
        """Test mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        from_email = to_send[0][3]
        self.assertEqual(from_email, 'Marie <test_using_invite_use_host_in_from_email@example.com>')

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(INVITE_HOSTS={'Marie': 'test_send_mass_html_mail_reply_to@example.com'})
    def test_send_mass_html_mail_to_send_no_email(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self.family.guests.add(
            Guest(name='Pierre', email=None, phone='0123456789', female=False, family=self.family),
            bulk=False
        )
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        recipient = list(send_mass_html_mail__mock.call_args[0][0])[0][4]
        self.assertListEqual(list(recipient),
                             ['Françoise <valid@example.com>', 'Jean <valid@example.com>'])


class TestFamilyAdmin(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """Test Family Admin"""

    def setUp(self):
        super(TestFamilyAdmin, self).setUp()
        self.event2 = self.create_event(self.family, name='test2', owner=self.user)
        self.site = AdminSite()

    def tearDown(self):
        self.event2.delete()
        super(TestFamilyAdmin, self).tearDown()

    def test_get_fields(self):
        """Test get_fields method"""
        fadm = admin.FamilyAdmin(Family, self.site)
        expected_fields = ['invited_midday', 'invited_afternoon', 'invited_evening', 'host', ]
        self.assertListEqual(list(fadm.get_form(MockRequest.instance()).base_fields),
                             expected_fields)
        self.assertEqual(list(fadm.get_fields(MockRequest.instance())), expected_fields)
        self.assertEqual(list(fadm.get_fields(MockRequest.instance(), self.family)),
                         expected_fields)

    def test_get_list_display(self):
        """Test get_list_display method"""
        fadm = admin.FamilyAdmin(Family, self.site)
        user_list_display = list(fadm.get_list_display(MockRequest.instance(self.user)))
        self.assertListEqual(user_list_display, ['__str__'])

        superuser_list_display = list(fadm.get_list_display(MockRequest.instance()))
        self.assertListEqual(superuser_list_display, ['__str__'])

    def test_get_queryset(self):
        """Test get_list_display method"""
        superuser = get_user_model().objects.create_superuser(
            username='super_user', email='valid@example.com', password='mf(33<QuPzg\'(0')
        family2 = self.create_family('2', owner=superuser)

        fadm = admin.FamilyAdmin(Family, self.site)
        family_qs = fadm.get_queryset(MockRequest.instance(self.user))
        self.assertEqual(family_qs.count(), 1)
        self.assertEqual(family_qs.get(), self.family)

        family_qs = fadm.get_queryset(MockRequest.instance(superuser))
        self.assertEqual(family_qs.count(), 1)
        self.assertEqual(family_qs.get(), family2)

    @override_settings(CSRF_HEADER_NAME='CSRF_HEADER_NAME', CSRF_COOKIE_NAME='CSRF_COOKIE_NAME')
    def _send_form(self, send_mail=True):  # type: (bool) -> HttpResponse
        """
        Mixin function to send email on the formset with cleaned data
        """
        path = reverse('admin:invite_family_change', kwargs={'object_id': self.family.pk})
        event_families_id = Event.families.through.objects.values_list('pk', flat=True)
        data = {
            'Event_families-0-event': self.event.pk,
            'Event_families-0-family': self.family.pk,
            'Event_families-0-id':
                event_families_id.filter(event=self.event, family=self.family).first(),
            'Event_families-1-event': self.event2.pk,
            'Event_families-1-family': self.family.pk,
            'Event_families-1-id':
                event_families_id.filter(event=self.event2, family=self.family).first(),
            'Event_families-INITIAL_FORMS': '2',
            'Event_families-TOTAL_FORMS': '2',

            'invited_evening': 'on',
            'host': 'Marie',

            'guests-INITIAL_FORMS': '0',
            'guests-TOTAL_FORMS': '0',
            'accompanies-INITIAL_FORMS': '0',
            'accompanies-TOTAL_FORMS': '0',
        }
        if send_mail:
            data['Event_families-0-send_mail'] = 'on'
        self.client.force_login(self.user)
        with patch.object(admin.FamilyAdmin, 'log_change'):
            self.client.post(path, data=data)

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(INVITE_HOSTS={'Marie': 'test_send_mass_html_mail_reply_to@example.com'})
    def test_send_mass_html_mail_reply_to(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self._send_form()

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        self.assertEqual(send_mass_html_mail__mock.call_args[1]['reply_to'],
                         ['Marie <test_send_mass_html_mail_reply_to@example.com>'])

    @patch.object(admin, 'send_mass_html_mail')
    def test_send_mass_html_mail_to_send(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply to_send argument"""
        self._send_form()

        self.assertIsInstance(send_mass_html_mail__mock.call_args[0], Iterable)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        expected_subject = 'Save the date'

        self.assertEqual(len(to_send), 1)
        to_send = list(to_send[0])
        self.assertEqual(len(to_send), 6)
        subject, text, html, from_email, recipient, join_attachment = to_send
        self.assertEqual(subject, expected_subject)
        self.assertEqual(text, self.expected_text)
        self.assertEqual(html, self.expected_html)
        self.assertIsNone(from_email)
        self.assertListEqual(list(recipient),
                             ['Françoise <valid@example.com>', 'Jean <valid@example.com>'])
        self.assertListEqual(list(join_attachment), [(self.joined_document.document.path,
                                                      'happy.png', 'image/png')])

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(
        INVITE_HOSTS={'Marie': 'test_using_invite_use_host_in_from_email@example.com'},
        INVITE_USE_HOST_IN_FROM_EMAIL=True)
    def test_using_invite_use_host_in_from_email(self, send_mass_html_mail__mock: Mock):
        """Test Family Invitation Formset send mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        self._send_form()

        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        from_email = to_send[0][3]
        self.assertEqual(from_email, 'Marie <test_using_invite_use_host_in_from_email@example.com>')

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(INVITE_HOSTS={'Marie': 'test_send_mass_html_mail_reply_to@example.com'})
    def test_fifs_send_mass_html_mail_to_send_no_email(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self.family.guests.add(
            Guest(name='Pierre', email=None, phone='0123456789', female=False, family=self.family),
            bulk=False
        )

        self._send_form()

        recipient = list(send_mass_html_mail__mock.call_args[0][0])[0][4]
        self.assertListEqual(list(recipient),
                             ['Françoise <valid@example.com>', 'Jean <valid@example.com>'])

    @patch.object(admin, 'messages')
    @patch.object(admin, 'send_mass_html_mail')
    def test_send_form_without_email(self, send_mass_html_mail__mock: Mock,
                                     messages_mock: Mock):
        """Check that no mail is sent if no family is selected by sending the family admin form"""
        self._send_form(False)

        self.assertEqual(send_mass_html_mail__mock.call_count, 0)
        self.assertEqual(messages_mock.add_message.call_count, 0)

    def test_create_1(self):
        """Validate the admin family creation"""
        path = reverse('admin:invite_family_add')
        self.client.force_login(self.user)

        self.client.post(path, {
            'host': 'Pierre',

            'Event_families-INITIAL_FORMS': '0',
            'Event_families-TOTAL_FORMS': '0',
            'guests-INITIAL_FORMS': '0',
            'guests-TOTAL_FORMS': '0',
            'accompanies-INITIAL_FORMS': '0',
            'accompanies-TOTAL_FORMS': '0',

        })

        family = Family.objects.last()
        self.assertNotEqual(family, self.family)
        self.assertEqual(family.host, 'Pierre')
        self.assertIn(self.user, family.owners.all())

    def test_add_to_event_1(self):
        """Test add_to_event action template"""
        path = reverse('admin:invite_family_changelist')
        self.client.force_login(self.user)

        response = self.client.post(path, {'action': 'add_to_event',
                                           '_selected_action': [str(self.family.pk)], })

        self.assertTemplateUsed(response, 'admin/transitional_action.html')
        form = response.context.get('form')
        self.assertIsInstance(form, invite.forms.AddToEventForm)
        self.assertFalse(any(form.errors.values()))

    def test_add_to_event_2(self):
        """Test add_to_event action success"""
        path = reverse('admin:invite_family_changelist')
        self.client.force_login(self.user)
        family2 = self.create_family('2', owner=self.user)

        response = self.client.post(path, {'action': 'add_to_event',
                                           '_confirm': '1',
                                           '_selected_action': [str(family2.pk)],
                                           'event': str(self.event.pk)})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(family2.invitations.filter(pk=self.event.pk).exists())

    def test_add_to_event_3(self):
        """Test add_to_event with invalid form"""
        path = reverse('admin:invite_family_changelist')
        self.client.force_login(self.user)
        family2 = self.create_family('2', owner=self.user)

        response = self.client.post(path, {'action': 'add_to_event',
                                           '_confirm': '1',
                                           '_selected_action': [str(family2.pk)],
                                           'event': ''})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/transitional_action.html')
        form = response.context.get('form')
        self.assertIsInstance(form, invite.forms.AddToEventForm)
        self.assertTrue(any(form.errors.values()))
        self.assertIn('event', form.errors)
        self.assertEqual(form.errors['event'].data[0].code, 'required')

    def test_add_to_event_4(self):
        """Test add_to_event with not owned family"""
        path = reverse('admin:invite_family_changelist')
        self.client.force_login(self.user)
        user2 = get_user_model().objects.create_user('user2', 'valid@example.com', '1pewofk9q[3r-i')
        family2 = self.create_family('2', owner=user2)

        self.client.post(path, {'action': 'add_to_event',
                                '_confirm': '1',
                                '_selected_action': [str(family2.pk)],
                                'event': str(self.event.pk)})

        self.assertFalse(family2.invitations.filter(pk=self.event.pk).exists())
        self.assertFalse(self.event.families.filter(pk=family2.pk).exists())


class TestEventAdmin(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """Test Event Admin"""

    def setUp(self):
        super(TestEventAdmin, self).setUp()
        self.site = AdminSite()
        self.family2 = self.create_family(name_suffix='2', owner=self.user)
        self.event.families.add(self.family2)

    def test_get_fields(self):
        """Test displayed fields"""
        fadm = admin.EventAdmin(Event, self.site)
        expected_fields = ['name', 'date', ]
        self.assertListEqual(list(fadm.get_form(MockRequest.instance()).base_fields),
                             expected_fields)
        self.assertEqual(list(fadm.get_fields(MockRequest.instance())), expected_fields)
        self.assertEqual(list(fadm.get_fields(MockRequest.instance(), self.event)), expected_fields)

    def test_get_list_display(self):
        """Test displayed fields"""
        fadm = admin.EventAdmin(Event, self.site)
        self.assertListEqual(list(fadm.get_list_display(MockRequest.instance())), ['__str__'])

    def test_get_queryset(self):
        """Test get_list_display method"""
        superuser = get_user_model().objects.create_superuser(
            username='super_user', email='valid@example.com', password='mf(33<QuPzg\'(0')
        event2 = self.create_event(owner=superuser, name='2')

        eadm = admin.EventAdmin(Event, self.site)
        event_qs = eadm.get_queryset(MockRequest.instance(self.user))
        self.assertEqual(event_qs.count(), 1)
        self.assertEqual(event_qs.get(), self.event)

        event_qs = eadm.get_queryset(MockRequest.instance(superuser))
        self.assertEqual(event_qs.count(), 1)
        self.assertEqual(event_qs.get(), event2)

    def test_inlines(self):
        """Test inlines"""
        fadm = admin.EventAdmin(Event, self.site)
        inline_instances = fadm.get_inline_instances(MockRequest.instance())
        self.assertListEqual(list(map(type, inline_instances)), [
            admin.MailTemplateInline,
            admin.FamilyInvitationInline,
        ])

    def test_create_1(self):
        """Validate the admin event creation"""
        path = reverse('admin:invite_event_add')
        self.client.force_login(self.user)

        self.client.post(path, {
            'name': 'Event name',
            'date': '2018-01-01',

            'Event_families-INITIAL_FORMS': '0',
            'Event_families-TOTAL_FORMS': '0',

            'mailtemplate-INITIAL_FORMS': '0',
            'mailtemplate-TOTAL_FORMS': '0',

        })

        event = Event.objects.last()  # type: Event
        self.assertNotEqual(event, self.family)
        self.assertEqual(event.name, 'Event name')
        self.assertEqual(event.date, date(2018, 1, 1))
        self.assertIn(self.user, event.owners.all())

    @override_settings(CSRF_HEADER_NAME='CSRF_HEADER_NAME', CSRF_COOKIE_NAME='CSRF_COOKIE_NAME')
    def _send_form(self, send_mail=True, login_user=None):
        """
        Mixin function to send email on the formset with cleaned data

        :param send_mail: whether or not the email as to be send for the 1st family
        :param login_user: user to log in (default: self.user)
        :return: The response
        """
        path = reverse('admin:invite_event_change', kwargs={'object_id': self.event.pk})
        event_families_id = Event.families.through.objects.values_list('pk', flat=True)
        data = {
            'Event_families-0-event': self.event.pk,
            'Event_families-0-family': self.family.pk,
            'Event_families-0-id':
                event_families_id.filter(event=self.event, family=self.family).first(),
            'Event_families-1-event': self.event.pk,
            'Event_families-1-family': self.family2.pk,
            'Event_families-1-id':
                event_families_id.filter(event=self.event, family=self.family2).first(),
            'Event_families-INITIAL_FORMS': '2',
            'Event_families-TOTAL_FORMS': '2',

            'mailtemplate-INITIAL_FORMS': '0',
            'mailtemplate-TOTAL_FORMS': '0',
        }
        if send_mail:
            data['Event_families-0-send_mail'] = 'on'

        self.client.force_login(login_user or self.user)
        with patch.object(admin.EventAdmin, 'log_change'):
            return self.client.post(path, data=data)

    def test_edit_not_mine(self):
        """Validate the admin event creation"""
        expected_messages = [
            'event with ID "%d" doesn\'t exist. Perhaps it was deleted?' % self.event.pk,
        ]
        user = get_user_model().objects.create_superuser('user4', 'valid@example.com',
                                                         '1pewofk9q[3r-i')

        response = self._send_form(False, user)

        messages = list(map(str, admin.messages.get_messages(response.wsgi_request)))
        self.assertEqual(messages, expected_messages)

    @patch.object(admin, 'messages')
    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(INVITE_HOSTS={'Marie': 'test_send_mass_html_mail_reply_to@example.com'})
    def test_send_mass_html_mail_reply_to(self, send_mass_html_mail__mock: Mock,
                                          messages_mock: Mock):
        """Check send_mass_html_mail reply_to argument"""
        self._send_form()

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        self.assertEqual(send_mass_html_mail__mock.call_args[1]['reply_to'],
                         ['Marie <test_send_mass_html_mail_reply_to@example.com>'])
        self.assertEqual(messages_mock.add_message.call_count, 1)
        messages_mock.add_message.assert_called_once_with(
            messages_mock.add_message.call_args[0][0], admin.messages.INFO, '1 messages send')

    @patch.object(admin, 'send_mass_html_mail')
    def test_send_mass_html_mail_to_send(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply to_send argument"""
        self._send_form()

        self.assertIsInstance(send_mass_html_mail__mock.call_args[0], Iterable)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        expected_subject = 'Save the date'

        self.assertEqual(len(to_send), 1)
        to_send = list(to_send[0])
        self.assertEqual(len(to_send), 6)
        subject, text, html, from_email, recipient, join_attachment = to_send
        self.assertEqual(subject, expected_subject)
        self.assertEqual(text, self.expected_text)
        self.assertEqual(html, self.expected_html)
        self.assertIsNone(from_email)
        self.assertListEqual(list(recipient),
                             ['Françoise <valid@example.com>', 'Jean <valid@example.com>'])
        self.assertListEqual(list(join_attachment), [(self.joined_document.document.path,
                                                      'happy.png', 'image/png')])

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(
        INVITE_HOSTS={'Marie': 'test_using_invite_use_host_in_from_email@example.com'},
        INVITE_USE_HOST_IN_FROM_EMAIL=True)
    def test_using_invite_use_host_in_from_email(self, send_mass_html_mail__mock: Mock):
        """Test Family Invitation Formset send mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        self._send_form()

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        from_email = to_send[0][3]
        self.assertEqual(from_email, 'Marie <test_using_invite_use_host_in_from_email@example.com>')

    @patch.object(admin, 'send_mass_html_mail')
    @override_settings(INVITE_HOSTS={'Marie': 'test_send_mass_html_mail_reply_to@example.com'})
    def test_fifs_send_mass_html_mail_to_send_no_email(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self.family.guests.add(
            Guest(name='Pierre', email=None, phone='0123456789', female=False, family=self.family),
            bulk=False
        )

        self._send_form()

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        recipient = list(send_mass_html_mail__mock.call_args[0][0])[0][4]
        self.assertListEqual(list(recipient),
                             ['Françoise <valid@example.com>', 'Jean <valid@example.com>'])

    def test_send_mail_without_template(self):
        """Test what happend when sending an email using a event without mail template"""
        event_without_mail = self.create_event(self.family, name=None, owner=self.user)
        fadm = admin.EventAdmin(Event, self.site)
        with patch.object(fadm, 'message_user') as message_user_mock:
            fadm.send_mail('Request', [self.event, event_without_mail])
            message_user_mock.assert_called_once_with(
                'Request', 'The event of the 2018-12-31 has no email template set',
                admin.messages.ERROR)

    @patch.object(admin, 'messages')
    @patch.object(admin, 'send_mass_html_mail')
    def test_send_form_without_email(self, send_mass_html_mail__mock: Mock,
                                     messages_mock: Mock):
        """Check that no mail is sent if no family is selected by sending the event admin form"""
        self._send_form(False)

        self.assertEqual(send_mass_html_mail__mock.call_count, 0)
        self.assertEqual(messages_mock.add_message.call_count, 0)


class TestFamilyInvitationInline(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """Test FamilyInvitationInline"""

    def test_get_fields(self):
        """Test displayed fields"""
        site = AdminSite()
        fadm = admin.FamilyInvitationInline(Event, site)
        expected_fields = ['event', 'family', 'send_mail', 'show_mail', ]
        self.assertEqual(list(fadm.get_fields(MockRequest.instance())), expected_fields)
        self.assertEqual(list(fadm.get_fields(MockRequest.instance(), self.event)), expected_fields)

    def test_show_mail(self):
        """Test show_mail function"""
        self.assertEqual(
            admin.FamilyInvitationInline.show_mail(
                Event.families.through(family_id=1, event_id=self.event.pk)), '')
        self.assertEqual(
            admin.FamilyInvitationInline.show_mail(
                Event.families.through(family_id=1, event_id=self.event.pk, pk=1)),
            '<a href="/invite/show_mail/event/%d/family/1.html">Preview the mail</a>' %
            self.event.pk
        )


class TestFamilyInvitationInlineWithoutTemplate(TestEventMixin, TestCase):
    """Test FamilyInvitationInline"""

    def test_show_mail(self):
        """Test show_mail function"""
        self.assertEqual(
            admin.FamilyInvitationInline.show_mail(
                Event.families.through(family_id=1, event_id=self.event.pk, pk=1)),
            'The event has no email template set'
        )


class TestJoinedDocumentAdmin(TestCase):
    """Test joined document admin"""

    def tearDown(self):
        super(TestJoinedDocumentAdmin, self).tearDown()
        path = os.path.join(JoinedDocument.document.field.upload_to, 'test_without_document.txt')
        JoinedDocument.document.field.storage.delete(path)
        path = os.path.join(JoinedDocument.document.field.upload_to, 'fake-file.txt')
        JoinedDocument.document.field.storage.delete(path)

    @patch.object(JoinedDocumentForm._meta, 'model', JoinedDocument, create=True)  # pylint: disable=no-member
    def test_form(self):
        """test with a full filed form"""
        self.assertEqual(JoinedDocumentAdmin.form, JoinedDocumentForm)
        model_form = JoinedDocumentAdmin(JoinedDocument, Mock()).get_form(MockRequest())
        form = model_form(
            {'name': 'name.txt'},
            {'document': SimpleUploadedFile('fake-file.txt', b'attachment\n', 'text/javascript')}
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.name, 'name.txt')
        self.assertEqual(form.instance.mimetype, 'text/plain')
        form.instance.document.file.seek(0)
        self.assertEqual(form.instance.document.file.read(), b'attachment\n')

    @patch('invite.forms.magic', None)
    def test_without_libmagic(self):
        """test with a full filed form libmagic is not installed"""
        model_form = JoinedDocumentAdmin(JoinedDocument, Mock()).get_form(MockRequest())
        form = model_form(
            {'name': 'name.txt'},
            {'document': SimpleUploadedFile('fake-file.txt', b'attachment\n', 'text/javascript')}
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.mimetype, 'text/javascript')

    def test_without_name(self):
        """test with an incomplete form"""
        model_form = JoinedDocumentAdmin(JoinedDocument, Mock()).get_form(MockRequest())
        form = model_form(
            {'name': ''},
            {'document': SimpleUploadedFile('fake-file.txt', b'attachment\n', 'text/javascript')}
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.instance.name, 'fake-file.txt')

    def test_edit_without_name(self):
        """test an edition with an incomplete form"""
        joined_document = JoinedDocument.objects.create(
            document=SimpleUploadedFile('fake-file.txt', b'attachment\n'),
            name='att.txt',
            mimetype='text/plain'
        )
        model_form = JoinedDocumentAdmin(JoinedDocument, Mock()).get_form(MockRequest())
        form = model_form(
            {'name': ''},
            {},
            instance=joined_document
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.name, 'fake-file.txt')
