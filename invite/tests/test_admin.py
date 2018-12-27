"""
test_admin

Created by lmarvaud on 03/11/2018
"""
from collections import Iterable
from unittest.mock import patch, Mock

from django.contrib.admin import AdminSite
from django.test import TestCase

from invite.tests.common import TestFamilyMixin, TestEventMixin
from .. import admin
from ..models import Family, Guest, Event


class TestMail(TestEventMixin, TestCase):
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
    @patch.object(admin, 'settings')
    def test_using_invite_use_host_in_from_email(self, unused__settings__mock,
                                                 send_mass_html_mail__mock: Mock):
        """Test mail using INVITE_USE_HOST_IN_FROM_EMAIL setting"""
        admin.settings.INVITE_HOSTS = {
            "Marie": "test_using_invite_use_host_in_from_email@example.com"
        }
        admin.settings.INVITE_USE_HOST_IN_FROM_EMAIL = True
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


class MockSuperUser:  # pylint: disable=too-few-public-methods
    """Fake super user"""
    is_authenticated = True

    @staticmethod
    def has_perm(unused_perm):
        """Return super user permission : always True"""
        return True


class MockRequest:  # pylint: disable=too-few-public-methods
    """Fake request"""
    _instance = None

    def __init__(self):
        """Initialize the user"""
        self.user = MockSuperUser()

    @classmethod
    def instance(cls):
        """Gest singleton instance"""
        if not cls._instance:
            cls._instance = cls()
        return cls._instance


class TestFamilyAdmin(TestFamilyMixin, TestCase):
    """Test Family Admin"""
    def setUp(self):
        super(TestFamilyAdmin, self).setUp()
        self.site = AdminSite()

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


class TestEventAdmin(TestEventMixin, TestCase):
    """Test Event Admin"""
    def setUp(self):
        super(TestEventAdmin, self).setUp()
        self.site = AdminSite()

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
        self.assertListEqual(list(map(type, inline_instances)), [admin.FamilyInvitationInline])


class TestFamilyInvitationInline(TestEventMixin, TestCase):
    """Test FamilyInvitationInline"""
    def test_get_fields(self):
        """Test displayed fields"""
        site = AdminSite()
        fadm = admin.FamilyInvitationInline(Event, site)
        expected_fields = ['event', 'family', 'show_mail', ]
        self.assertEqual(list(fadm.get_fields(MockRequest.instance())), expected_fields)
        self.assertEqual(list(fadm.get_fields(MockRequest.instance(), self.event)), expected_fields)

    def test_show_mail(self):
        """Test show_mail function"""
        self.assertEqual(
            admin.FamilyInvitationInline.show_mail(Event.families.through(family_id=1)), "")
        self.assertEqual(
            admin.FamilyInvitationInline.show_mail(Event.families.through(family_id=2, pk=1)),
            '<a href="/invite/show_mail/2.html">Preview the mail</a>'
        )
