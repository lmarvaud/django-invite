"""
test_admin

Created by lmarvaud on 03/11/2018
"""
from collections import Iterable
from unittest.mock import patch, Mock

from django.contrib.admin import AdminSite
from django.shortcuts import reverse
from django.test import TestCase

from invite.tests.common import TestEventMixin, TestMailTemplateMixin, MockSuperUser, MockRequest
from invite import admin
from invite.models import Family, Guest, Event


class TestMail(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """Test admin mail action"""

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_send_mass_html_mail_reply_to(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        self.assertEqual(send_mass_html_mail__mock.call_args[1]['reply_to'],
                         ["Marie <test_send_mass_html_mail_reply_to@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    def test_send_mass_html_mail_to_send(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply to_send argument"""
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        self.assertIsInstance(send_mass_html_mail__mock.call_args[0], Iterable)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        expected_subject = "Save the date"

        self.assertEqual(len(to_send), 1)
        to_send = list(to_send[0])
        self.assertEqual(len(to_send), 5)
        subject, text, html, from_email, recipient = to_send
        self.assertEqual(subject, expected_subject)
        self.assertEqual(text, self.expected_text)
        self.assertEqual(html, self.expected_html)
        self.assertIsNone(from_email)
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_using_invite_use_host_in_from_email@example.com"})
    @patch.object(admin.settings, 'INVITE_USE_HOST_IN_FROM_EMAIL', True, create=True)
    def test_using_invite_use_host_in_from_email(self, send_mass_html_mail__mock: Mock):
        """Test mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        from_email = to_send[0][3]
        self.assertEqual(from_email, "Marie <test_using_invite_use_host_in_from_email@example.com>")

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_send_mass_html_mail_to_send_no_email(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self.family.guests.add(
            Guest(name="Pierre", email=None, phone="0123456789", female=False, family=self.family),
            bulk=False
        )
        events = Event.objects.filter(pk=self.event.pk)

        admin.EventAdmin.send_mail(Mock(), None, events)

        recipient = list(send_mass_html_mail__mock.call_args[0][0])[0][4]
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])


class TestFamilyAdmin(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """Test Family Admin"""
    def setUp(self):
        super(TestFamilyAdmin, self).setUp()
        self.event2 = self.create_event(self.family, name="test2")
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
        self.assertListEqual(list(fadm.get_list_display(MockRequest.instance())), ["__str__"])

    def _send_form(self):
        """Mixin function to send email on the formset with cleaned data"""
        path = reverse("admin:invite_family_change", kwargs={"object_id": self.family.pk})
        event_families_id = Event.families.through.objects.values_list("pk", flat=True)
        data = {
            'Event_families-0-event': self.event.pk,
            'Event_families-0-family': self.family.pk,
            'Event_families-0-id':
                event_families_id.filter(event=self.event, family=self.family).first(),
            'Event_families-0-send_mail': 'on',
            'Event_families-1-event': self.event2.pk,
            'Event_families-1-family': self.family.pk,
            'Event_families-1-id':
                event_families_id.filter(event=self.event2, family=self.family).first(),
            'Event_families-INITIAL_FORMS': '2',
            'Event_families-TOTAL_FORMS': '2',

            "invited_evening": "on",
            "host": "Marie",

            'guests-INITIAL_FORMS': '0',
            'guests-TOTAL_FORMS': '0',
            'accompanies-INITIAL_FORMS': '0',
            'accompanies-TOTAL_FORMS': '0',
        }
        request_mock = Mock(user=MockSuperUser(), POST=data, GET={}, method="POST", path=path,
                            current_app="invite", COOKIES={"csrftoken": "mocked"},
                            META={"csrftoken": "mocked", "SCRIPT_NAME": ""})
        fadm = admin.FamilyAdmin(Family, self.site)
        with patch.object(fadm, "log_change"):
            fadm.changeform_view(request_mock, str(self.family.pk), path)

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_send_mass_html_mail_reply_to(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self._send_form()

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        self.assertEqual(send_mass_html_mail__mock.call_args[1]['reply_to'],
                         ["Marie <test_send_mass_html_mail_reply_to@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    def test_send_mass_html_mail_to_send(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply to_send argument"""
        self._send_form()

        self.assertIsInstance(send_mass_html_mail__mock.call_args[0], Iterable)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        expected_subject = "Save the date"

        self.assertEqual(len(to_send), 1)
        to_send = list(to_send[0])
        self.assertEqual(len(to_send), 5)
        subject, text, html, from_email, recipient = to_send
        self.assertEqual(subject, expected_subject)
        self.assertEqual(text, self.expected_text)
        self.assertEqual(html, self.expected_html)
        self.assertIsNone(from_email)
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_using_invite_use_host_in_from_email@example.com"})
    @patch.object(admin.settings, 'INVITE_USE_HOST_IN_FROM_EMAIL', True, create=True)
    def test_using_invite_use_host_in_from_email(self, send_mass_html_mail__mock: Mock):
        """Test Family Invitation Formset send mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        self._send_form()

        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        from_email = to_send[0][3]
        self.assertEqual(from_email, "Marie <test_using_invite_use_host_in_from_email@example.com>")

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_fifs_send_mass_html_mail_to_send_no_email(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self.family.guests.add(
            Guest(name="Pierre", email=None, phone="0123456789", female=False, family=self.family),
            bulk=False
        )

        self._send_form()

        recipient = list(send_mass_html_mail__mock.call_args[0][0])[0][4]
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])


class TestEventAdmin(TestMailTemplateMixin, TestEventMixin, TestCase):  # pylint: disable=too-many-ancestors
    """Test Event Admin"""
    def setUp(self):
        super(TestEventAdmin, self).setUp()
        self.site = AdminSite()
        self.family2 = self.create_family(name_suffix="2")
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
        self.assertListEqual(list(fadm.get_list_display(MockRequest.instance())), ["__str__"])

    def test_inlines(self):
        """Test inlines"""
        fadm = admin.EventAdmin(Event, self.site)
        inline_instances = fadm.get_inline_instances(MockRequest.instance())
        self.assertListEqual(list(map(type, inline_instances)), [
            admin.MailTemplateInline,
            admin.FamilyInvitationInline,
        ])

    def _send_form(self):
        """Mixin function to send email on the formset with cleaned data"""
        path = reverse("admin:invite_event_change", kwargs={"object_id": self.event.pk})
        event_families_id = Event.families.through.objects.values_list("pk", flat=True)
        data = {
            'Event_families-0-event': self.event.pk,
            'Event_families-0-family': self.family.pk,
            'Event_families-0-id':
                event_families_id.filter(event=self.event, family=self.family).first(),
            'Event_families-0-send_mail': 'on',
            'Event_families-1-event': self.event.pk,
            'Event_families-1-family': self.family2.pk,
            'Event_families-1-id':
                event_families_id.filter(event=self.event, family=self.family2).first(),
            'Event_families-INITIAL_FORMS': '2',
            'Event_families-TOTAL_FORMS': '2',

            'mailtemplate-INITIAL_FORMS': '0',
            'mailtemplate-TOTAL_FORMS': '0',
        }
        request_mock = Mock(user=MockSuperUser(), POST=data, GET={}, method="POST", path=path,
                            current_app="invite", COOKIES={"csrftoken": "mocked"},
                            META={"csrftoken": "mocked", "SCRIPT_NAME": ""})
        fadm = admin.EventAdmin(Event, self.site)
        with patch.object(fadm, "log_change"):
            fadm.changeform_view(request_mock, str(self.event.pk), path)

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_send_mass_html_mail_reply_to(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self._send_form()

        self.assertEqual(send_mass_html_mail__mock.call_count, 1)
        self.assertEqual(send_mass_html_mail__mock.call_args[1]['reply_to'],
                         ["Marie <test_send_mass_html_mail_reply_to@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    def test_send_mass_html_mail_to_send(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply to_send argument"""
        self._send_form()

        self.assertIsInstance(send_mass_html_mail__mock.call_args[0], Iterable)
        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        expected_subject = "Save the date"

        self.assertEqual(len(to_send), 1)
        to_send = list(to_send[0])
        self.assertEqual(len(to_send), 5)
        subject, text, html, from_email, recipient = to_send
        self.assertEqual(subject, expected_subject)
        self.assertEqual(text, self.expected_text)
        self.assertEqual(html, self.expected_html)
        self.assertIsNone(from_email)
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_using_invite_use_host_in_from_email@example.com"})
    @patch.object(admin.settings, 'INVITE_USE_HOST_IN_FROM_EMAIL', True, create=True)
    def test_using_invite_use_host_in_from_email(self, send_mass_html_mail__mock: Mock):
        """Test Family Invitation Formset send mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        self._send_form()

        to_send = list(send_mass_html_mail__mock.call_args[0][0])
        from_email = to_send[0][3]
        self.assertEqual(from_email, "Marie <test_using_invite_use_host_in_from_email@example.com>")

    @patch.object(admin, 'send_mass_html_mail')
    @patch.object(admin.settings, 'INVITE_HOSTS',
                  {"Marie": "test_send_mass_html_mail_reply_to@example.com"})
    def test_fifs_send_mass_html_mail_to_send_no_email(self, send_mass_html_mail__mock: Mock):
        """Check send_mass_html_mail_reply reply_to argument"""
        self.family.guests.add(
            Guest(name="Pierre", email=None, phone="0123456789", female=False, family=self.family),
            bulk=False
        )

        self._send_form()

        recipient = list(send_mass_html_mail__mock.call_args[0][0])[0][4]
        self.assertListEqual(list(recipient),
                             ["Françoise <valid@example.com>", "Jean <valid@example.com>"])

    def test_send_mail_without_mail(self):
        """Test what happend when sending an email using a event without mail template"""
        event_without_mail = self.create_event(self.family, name=None)
        fadm = admin.EventAdmin(Event, self.site)
        with patch.object(fadm, "message_user") as message_user_mock:
            fadm.send_mail("Request", [self.event, event_without_mail])
            message_user_mock.assert_called_once_with(
                "Request", "The event of the 2018-12-31 has no email template set",
                admin.messages.ERROR)


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
                Event.families.through(family_id=1, event_id=self.event.pk)), "")
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
